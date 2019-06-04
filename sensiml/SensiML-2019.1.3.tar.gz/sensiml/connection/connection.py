##################################################################################
#  SENSIML CONFIDENTIAL                                                          #
#                                                                                #
#  Copyright (c) 2017  SensiML Corporation.                                      #
#                                                                                #
#  The source code contained or  described  herein and all documents related     #
#  to the  source  code ("Material")  are  owned by SensiML Corporation or its   #
#  suppliers or licensors. Title to the Material remains with SensiML Corpora-   #
#  tion  or  its  suppliers  and  licensors. The Material may contain trade      #
#  secrets and proprietary and confidential information of SensiML Corporation   #
#  and its suppliers and licensors, and is protected by worldwide copyright      #
#  and trade secret laws and treaty provisions. No part of the Material may      #
#  be used,  copied,  reproduced,  modified,  published,  uploaded,  posted,     #
#  transmitted, distributed,  or disclosed in any way without SensiML's prior    #
#  express written permission.                                                   #
#                                                                                #
#  No license under any patent, copyright,trade secret or other intellectual     #
#  property  right  is  granted  to  or  conferred upon you by disclosure or     #
#  delivery of the Materials, either expressly, by implication,  inducement,     #
#  estoppel or otherwise.Any license under such intellectual property rights     #
#  must be express and approved by SensiML in writing.                           #
#                                                                                #
#  Unless otherwise agreed by SensiML in writing, you may not remove or alter    #
#  this notice or any other notice embedded in Materials by SensiML or SensiML's #
#  suppliers or licensors in any way.                                            #
#                                                                                #
##################################################################################

try:
    from http.cookiejar import CookiePolicy
except ImportError:
    from cookielib import CookiePolicy
import os
import re
import json as JSON
import requests_oauthlib
import requests
from requests import Response
from oauthlib.oauth2 import LegacyApplicationClient, InvalidGrantError, MissingTokenError, TokenExpiredError
from requests_oauthlib import OAuth2Session, OAuth2
from getpass import getpass
from appdirs import user_config_dir
import errno
from uuid import uuid4
from time import sleep
import logging
import warnings
from functools import partial
from .connection_config import ConnectionConfig
from six.moves import input

try:
    import configparser as ConfigParser
except:
    import ConfigParser
from .errors import *

logger = logging.getLogger(__name__)

# Get configuration directory
config_dir = user_config_dir(__name__.split('.')[0], False)

cid = "f7J0QNKkKcIkHMpk5lvq0wGZtBEpw1YcJ8Bea9Pv"
csid = "4OxQzkEnVc6OmTMKHgi77o8uFhEDz1QCuyKsNFm2Jo84r0TlGBXli0NrZ5uHTI769P3UurvDVB86awZkrEikCUJ7RM333BTS5oajO32BRwsNkPcOzA3JlBkPblvKM0l0"


class Warnings:
    insecure_warning = "You have chosen to disable certificate verification. Your connection is not secure!"


class Connection(object):
    """Connection class"""

    def __init__(self, server=None, username=None, password=None, **kwargs):
        """Create Connection object

        Args:
            server (str, optional): Server URL or name in config file.
            username (str, optional)
            password (str, optional)
            **kwargs (optional): Mostly used when passing `server` as URL. See below.

        Keyword Args:
            insecure (bool): Whether or not to require valid SSL/TLS in requests
            path (str, optional): When specifiying a server name instead of a URL, the path of the config file.
            server_name (str, optional): user-readable name of server. defaults to the server domain.
            url (str, optional): Alternative name for server argument.
            auth_url (str, optional): URL of the oauth server. Defaults to server url.
        """
        # Check url parameter to allow direct passing of ConnectionConfig instances

        server = server or kwargs.get('url')
        if re.match(r'^https?://', server):
            self.server_url = re.sub(r'([^/])$', r'\1/', server)
            self.server_name = re.sub(r'^https?://([A-Za-z0-9.\-_]+).*$',
                                      r'\1', server)
            self.auth_url = kwargs.pop('auth_url', self.server_url)
            self.client_id = cid
            self.client_secret = csid
            self.username = username
        else:
            path = kwargs.pop('path', 'connect.cfg')
            config = ConnectionConfig(server)
            try:
                config.load_from_file(path)
            except ConfigParser.NoSectionError:
                choice = input(
                    'No configuration found, would you like to create one? (y)/n ') or 'y'
                if choice.lower() in ['y', 'yes', 't', 'true']:
                    config.create_config_object(path)
                else:
                    raise ConnectionAbortedError()

            self.server_name = config.server
            self.server_url = config.url
            self.auth_url = config.auth_url
            self.client_id = cid
            self.client_secret = csid
            self.username = username

        self.token_url = self.auth_url.rstrip('/') + '/token/'
        self.max_retries = kwargs.pop('max_retries', 3)

        self._token_filename = os.path.join(
            config_dir, '{}_token.json'.format(self.server_name))

        try:
            self._token_last_updated = os.path.getmtime(self._token_filename)
        except OSError as e:
            if e.errno == errno.ENOENT:
                self._token_last_updated = None
            else:
                raise

        # Disable SSL check for localhost or when insecure=True
        self.insecure = kwargs.pop('insecure', False)
        if self.insecure:
            logger.error(Warnings.insecure_warning)
        if re.match(r'^https?://localhost', self.server_url) or self.insecure:
            requests.packages.urllib3.disable_warnings()
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
            self._verify = False
        else:
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = ''
            self._verify = True

        self._login(password)

    def _login(self, password, attempt=0):
        if attempt >= self.max_retries:
            raise LoginAttemptsExceededError()

        self.session = OAuth2Session(
            client=LegacyApplicationClient(client_id=self.client_id),
            auto_refresh_url=self.token_url,
            token_updater=self._token_updater
        )
        self._set_session_retries()
        self.session.cookies.set_policy(BlockAll())

        if self.username is None or password is None:
            if os.path.exists(self._token_filename):
                with open(self._token_filename, 'r') as f:
                    self.session.token = JSON.load(f)
            else:
                self.username = input('Enter username: ')
                password = getpass('Enter password: ')

        if not self.session.token:
            try:
                self.session.fetch_token(
                    token_url=self.token_url,
                    username=self.username,
                    password=password,
                    # UAA endpoints always require id/secret as basic auth
                    auth=(self.client_id, self.client_secret),
                    verify=self._verify)
            except (InvalidGrantError, MissingTokenError) as e:
                if isinstance(e, InvalidGrantError):
                    print('Invalid log in credentials, please try again.')
                else:
                    print(
                        'No token received: The remote server did not return a valid authorization response.')
                if os.path.exists(self._token_filename):
                    os.remove(self._token_filename)
                password = None
                self.username = None
                return self._login(password, attempt=attempt + 1)
            self._save_token(self.session.token)
        logger.debug('Login completed')

    def request(self, method, path, json=None, headers=None, **kwargs):
        """Sends request to server with authentication

        Args:
            method (str): HTTP Method.
            path (str): Path from server root to request.
            json (dict, optional): dictionary of information to be submitted as json
            headers (dict, optional): http headers to be sent
            **kwargs: Additional keyword arguments passed to underlying request library.

        Keyword Args:
            data (dict): Data to upload as application/x-www-form-urlencoded or multipart/form-data.
                Do not use in conjunction with json.
            paged (boolean): Return [PagedRequest] iterator instead of response

        Returns:
            Response: Response object from requests library with the result of the request
        """

        attempt = kwargs.pop('attempt', 0)
        paged = kwargs.pop('paged', False)
        verify = kwargs.pop('verify', self._verify)
        url = self.server_url.strip('/') + '/' + path.lstrip('/')
        if self._token_last_updated != os.path.getmtime(self._token_filename):
            with open(self._token_filename, 'r') as f:
                self.session.token = JSON.load(f)
        while attempt < self.max_retries:
            if paged:
                return PagedRequest(self.session, method, url, json=json, headers=headers, verify=verify,
                                    client_id=self.client_id, client_secret=self.client_secret, **kwargs)
            else:
                response = self.session.request(method, url, json=json, headers=headers, verify=verify,
                                                client_id=self.client_id, client_secret=self.client_secret, **kwargs)
            # temp workaround for bug in django-oauth-toolkit
            if response.status_code not in [401]:
                return response
            attempt += 1
            try:
                # If normal autorefresh fails we force it
                token = self.session.refresh_token(
                    self.token_url,
                    auth=(self.client_id, self.client_secret),
                    verify=self._verify
                )
                self._save_token(token)
            except (TokenExpiredError, InvalidGrantError) as e:
                print('Refresh Token expired, please re-enter your login information.')
                try:
                    os.unlink(
                        os.path.join(config_dir, '{}_token.json'.format(
                            self.server_name)))
                except OSError as e:
                    if e.errno != errno.ENOENT:
                        raise
                self._login(None)

        return response

    def paged_request(self, method, path, json=None, headers=None, limit=1000, **kwargs):
        """Returns an iterator that will request a new page each call.

        The result returned by the iterator will be the json decoded data of the
        'results' property of the response. Function args are the same as [request()]

        Args:
            method
            path
            json
            headers
            limit (Optional[int]): Number of entries per page, defaults to 1000.
                Note: this will override the 'limit' param specified in 'params'
                request kwarg.
            **kwargs: passed to request method
        """
        params = kwargs.pop('params', {})
        params['limit'] = limit
        return self.request(method, path, json, headers, params=params, paged=True, **kwargs)

    def file_request(self, path, file_path, data, read_type='rb', method='post', **kwargs):
        """Loads a file and formats metadata for specific endpoints and makes server request

        Args:
            path (str): Path to API endpoint
            file_path (str): Local path to file
            data (dict): Data to send to server along with request. May be sent in nonstandard headers instead of request body for some endpoints.
            method (str, optional): HTTP method, defaults to POST
            read_type (str, optional): Mode to open the file. defaults to binary read ('rb')

        Returns:
            Response
        """
        with open(file_path, read_type) as f:

            # TODO: Make this send params as body instead of headers.
            if path.find('segmenter/') >= 0:
                headers = {
                    'Name': data['name'],
                    'Type': data['specific_type'],
                    'Functioninfile': data['functioninfile']
                }
                request = partial(self.request, method, path,
                                  data=f, headers=headers)

            # TODO: Make this send params as body instead of headers.
            elif path.find('transform/') >= 0:
                headers = {
                    'Name': data['name'],
                    'Type': data['type'],
                    'Functioninfile': data['functioninfile'],
                    'Subtype': data['subtype'],
                    'HasCVersion': data['has_c_version'],
                    'CFileName': data['c_file_name'],
                }
                request = partial(self.request, method, path,
                                  data=f, headers=headers)

            elif path.find('capture/') >= 0:
                request = partial(
                    self.request,
                    method,
                    path,
                    files={'file': f},
                    data={
                        'name': data['name'],
                        'asynchronous': data['asynchronous']
                    })

            elif path.find('eventfile/') >= 0:
                request = partial(
                    self.request,
                    method,
                    path,
                    files={'data_file': f},
                    data={'name': data['name']})

            elif path.find('featurefile/') >= 0:
                request = partial(
                    self.request,
                    method,
                    path,
                    files={'data_file': f},
                    data={'name': data['name']})
            else:
                request = partial(self.request, method, path,
                                  data=data, files={'file': f})

            # call method with previously applied arguments
            return request(**kwargs)

    @staticmethod
    def logout(name):
        """Deletes saved session data for name"""
        try:
            os.unlink(os.path.join(config_dir, '{}_token.json'.format(name)))
        except OSError as e:
            if e.errno == errno.ENOENT:
                print('No session saved for {}.'.format(name))
                return
            else:
                raise
        print('Logged out.')

    def _set_session_retries(self):
        """set the number of retries a session has"""
        self.session.mount(
            "http://",
            requests.adapters.HTTPAdapter(max_retries=self.max_retries))
        self.session.mount(
            "https://",
            requests.adapters.HTTPAdapter(max_retries=self.max_retries))

    def _token_updater(self, token, save=True):
        """a simple function to save our token on refresh

        Args:
            token (dict): a token object for oauth2
        """
        self.session.token = token
        if save:
            self._save_token(token)

    def _save_token(self, token):
        if not os.path.exists(config_dir):
            try:
                os.makedirs(config_dir)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
        with open(self._token_filename, 'w') as f:
            # f.write(json.dumps(token))
            JSON.dump(token, f)
            self._token_last_updated = os.path.getmtime(f.name)


# With ouath we don't want to send cookies, this will overwite and block session cookies
class BlockAll(CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, * \
        args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False


class PagedRequest(object):
    def __init__(self, session, method, path, json=None, headers=None, **kwargs):
        self.session = session
        self._method = method
        self._path = path
        self._json = json
        self._headers = headers
        self._kwargs = kwargs

        self.response = None

    def __iter__(self):
        return self

    def next(self):
        """
        Returns:
            (dict) content of the results property in the response
        """
        if not self.response:
            self.response = self.session.request(
                self._method, self._path, self._json, self._headers, **self._kwargs)
        else:
            json = self.response.json()
            path = json['next']
            if not path:
                raise StopIteration
            self.response = self.session.request(
                self._method, path, self._json, self._headers, **self._kwargs)
        self.response.raise_for_status()
        return self.response.json()['results']
