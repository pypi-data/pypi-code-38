from __future__ import unicode_literals
from datetime import datetime, date, time
from decimal import Decimal
import importlib
import json
import os
from dateutil.parser import parse as dateutil_parse
from keystoneclient.session import Session as KeystoneSession
from keystoneclient.v3.client import Client as KeystoneClient
from .cloudcixauth import CloudCIXAuth
import cloudcix.api

__all__ = ['KeystoneSession', 'KeystoneClient', 'settings',
           'get_admin_session', 'get_admin_client', 'get_admin_token']


class ExtendedJSONEncoder(json.JSONEncoder):

    def prepare_data(self, data):
        """Prepare any data that will not be properly parsed by JSON here

        :param any data: Piece of data that should be recursively prepared for
                         json dumps
        :returns: Parsed data that if json friendly
        """
        if isinstance(data, (datetime, date, time)):
            return data.isoformat()
        if isinstance(data, Decimal):
            return float(data)
        if hasattr(data, 'items'):
            for k, v in data.items():
                data[k] = self.prepare_data(v)
        elif hasattr(data, '__iter__'):
            for i, v in enumerate(data):
                data[i] = self.prepare_data(v)
        return data

    def encode(self, obj):
        obj = self.prepare_data(obj)
        return super(ExtendedJSONEncoder, self).encode(obj)


class ExtendedJSONDecoder(json.JSONDecoder):

    def unparse_data(self, data):
        """Parses the json data returned from response.json back to python
        Calling response.json does most of the parsing however there are some
        leftovers left after that, for example: dates.

        :param any data: Piece of data that should be processed after json
                         load
        :returns: Piece of data parsed for python use
        """
        if isinstance(data, basestring):
            try:
                # try to parse into datetime, time or date
                if data.count('-') == 2 and data.count(':') in [1, 2] and \
                        data.count('.') <= 1:
                    return dateutil_parse(data, yearfirst=True)
                elif data.count('-') == 2:
                    return dateutil_parse(data, yearfirst=True).date()
                elif data.count(':') in [1, 2] and data.count('.') <= 1:
                    return dateutil_parse(data).time()
            except Exception:
                return data
        if hasattr(data, 'items'):
            for k, v in data.items():
                data[k] = self.unparse_data(v)
        elif hasattr(data, '__iter__'):
            for i, v in enumerate(data):
                data[i] = self.unparse_data(v)
        return data

    def decode(self, *args, **kwargs):
        obj = super(ExtendedJSONDecoder, self).decode(*args, **kwargs)
        return self.unparse_data(obj)


def new_method_proxy(func):
    """When attribute is accessed in lazy object, this method makes sure that
    lazy object was properly initialized and _setup method has been run
    """
    def inner(self, *args):
        if self._wrapped is None:
            self._setup()
        return func(self._wrapped, *args)
    return inner


class LazySettings(object):
    """Lazy settings module. We want settings to be imported when they are
    accessed not earlier.
    """
    _wrapped = None
    __getattr__ = new_method_proxy(getattr)

    def _setup(self):
        """
        Load the settings module pointed to by the environment variable. This
        is used the first time we need any settings at all, if the user has not
        previously configured the settings manually.
        """
        try:
            settings_module = os.environ['CLOUDCIX_SETTINGS_MODULE']
            if not settings_module:  # If it's set but is an empty string.
                raise KeyError
        except KeyError:
            raise ImportError("You must specify the CLOUDCIX_SETTINGS_MODULE "
                              "environment variable.")
        else:
            settings_module = settings_module.split(":")
            self._wrapped = importlib.import_module(settings_module[0])
            if len(settings_module) > 1:
                self._wrapped = getattr(self._wrapped, settings_module[1])
            api_setting = 'CLOUDCIX_API_VERSION'
            api_v2_url = 'CLOUDCIX_API_V2_URL'
            if not hasattr(self, api_setting):
                setattr(self._wrapped, api_setting, 1)
            if not hasattr(self, api_v2_url):
                setattr(self, api_v2_url, self.CLOUDCIX_SERVER_URL)


settings = LazySettings()


def get_required_settings():
    settings_obj = dict()
    try:
        settings_obj['auth_url'] = settings.OPENSTACK_KEYSTONE_URL
        settings_obj['username'] = settings.CLOUDCIX_API_USERNAME
        settings_obj['password'] = settings.CLOUDCIX_API_PASSWORD
        settings_obj['idMember'] = settings.CLOUDCIX_API_ID_MEMBER
    except ImportError:
        settings_obj['auth_url'] = os.environ['OPENSTACK_KEYSTONE_URL']
        settings_obj['username'] = os.environ['CLOUDCIX_API_USERNAME']
        settings_obj['password'] = os.environ['CLOUDCIX_API_PASSWORD']
        settings_obj['idMember'] = os.environ['CLOUDCIX_API_ID_MEMBER']
    return settings_obj


admin_session = None


def get_admin_session(private_session=False, **kwargs):
    """Returns an admin session instance. If private_session is passed in a
    new instance is returned.

    :param bool private_session: Denotes if new session instance should be
                                 returned
    :param kwargs: Any kwargs that should be passed down to CloudCIXAuth
                   instance, Ignored if session was already initialised
    :returns: Keystone session
    :rtype: KeystoneSession
    """
    global admin_session
    if admin_session and not private_session:
        return admin_session
    settings_obj = get_required_settings()
    t = CloudCIXAuth(
        auth_url=settings_obj['auth_url'],
        username=settings_obj['username'],
        password=settings_obj['password'],
        idMember=settings_obj['idMember'],
        **kwargs)
    s = KeystoneSession(auth=t)
    if not private_session:
        admin_session = s
    return s


def get_admin_client():
    """Wraps admin session into a KeystoneClient instance."""
    settings_obj = get_required_settings()
    admin_session = get_admin_session()
    return KeystoneClient(session=admin_session,
                          auth_url=settings_obj['auth_url'],
                          endpoint_override=settings_obj['auth_url'])


def get_admin_token():
    """
    Generates an `admin` token using the credentials specified
    in the settings module
    """
    data = {
        'email': settings.CLOUDCIX_API_USERNAME,
        'password': settings.CLOUDCIX_API_PASSWORD,
        'api_key': settings.CLOUDCIX_API_ID_MEMBER,
    }
    response = cloudcix.api.membership.token.create(data=data)
    if response.status_code == 201:
        return response.json()['token']
    raise Exception(response.json()['error_code'])
