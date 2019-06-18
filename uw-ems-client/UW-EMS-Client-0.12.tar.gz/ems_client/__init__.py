"""
Base module to support exposing EMS SOAP Service methods
"""
import atexit
from importlib import import_module
from logging import getLogger
from os.path import dirname, realpath
from shutil import rmtree
import sys
from tempfile import mkdtemp

from commonconf import settings
from restclients_core.util.mock import convert_to_platform_safe
from suds.client import Client
from suds import byte_str, WebFault
from suds.cache import ObjectCache

from .mock import EMSMockData


def load_object_by_name(object_name):
    """Load an object from a module by name"""
    mod_name, attr = object_name.rsplit('.', 1)
    mod = import_module(mod_name)
    return getattr(mod, attr)


url_base = '/EMSAPI'


class EMSAPIException(Exception):
    pass


class EMSAPI(object):
    """EMS API base
    """

    def __init__(self, options={}):
        if hasattr(settings, 'EMS_API_HOST'):
            self._wsdl = '%s%s/%s' % (
                settings.EMS_API_HOST, url_base, options.get('wsdl', ''))
            self._data = self._live
        else:
            self._wsdl = 'file://%s/resources/ems/file/%s/%s' % (
                dirname(realpath(__file__)), url_base,
                convert_to_platform_safe(options.get('wsdl', '')))
            self._data = self._mock

        self._log = getLogger('ems_client')
        cache_path = mkdtemp(prefix='ems_client-', suffix='-suds')
        atexit.register(rmtree, cache_path)
        client_opts = {'cache': ObjectCache(cache_path, days=1)}
        if hasattr(settings, 'EMS_API_TRANSPORT_CLASS'):
            transport = load_object_by_name(settings.EMS_API_TRANSPORT_CLASS)
            client_opts['transport'] = transport()
            client_opts['location'] = '%s/%s/Service.asmx' % (
                settings.EMS_API_HOST, url_base)
        self._api = Client(self._wsdl, **client_opts)
        self._api.set_options(cachingpolicy=0)

    def _request(self, methodName, params={}):
        try:
            return self._data(methodName, params)
        except WebFault as err:
            self._log.exception(err)
            raise EMSAPIException(
                'Cannot connect to the EMS server: %s' % err)
        except Exception as err:
            self._log.error('Error: (%s) %s' % (err, str(sys.exc_info()[0])))

            if type(err.args[0]) is tuple and type(err.args[0][0]) is int:
                if err.args[0][0] in [401, 403]:
                    errmsg = 'The request cannot be authenticated (%s)' % (
                        err.args[0][0])
                if err.args[0][0] in [404, 405, 406, 500]:
                    errmsg = 'The server is currently unavailable (%s)' % (
                        err.args[0][0])
                else:
                    errmsg = 'Unanticipated error: %s (%s)' % (
                        err.args[0][1], err.args[0][0])
            else:
                errmsg = 'Error connecting: %s' % (err)

            raise EMSAPIException(errmsg)

    def _live(self, methodName, params={}):
        params['UserName'] = settings.EMS_API_USERNAME
        params['Password'] = settings.EMS_API_PASSWORD
        return self._api.service[self._port][methodName](**params)

    def _mock(self, methodName, params={}):
        params['__inject'] = {
            'reply': byte_str(EMSMockData().mock(
                self._port, methodName, params))
        }
        return self._api.service[self._port][methodName](**params)
