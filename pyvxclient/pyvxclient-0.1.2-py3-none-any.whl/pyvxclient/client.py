import importlib

from bravado.requests_client import RequestsClient
from bravado.client import SwaggerClient
from bravado.swagger_model import load_file, load_url
from bravado.exception import HTTPForbidden, HTTPNotFound
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.error import URLError
import socket
import json
from pyvxclient.errors import WrongCredentials, NotAuthorized, NoSwaggerDef, EndpointURLNotFound
import logging
import requests
from requests.auth import HTTPBasicAuth
from pyvxclient.resource import Resource

__hostname__ = socket.gethostname()

client_config = {
    "url": None,
    "cache": None,
    "api_key": None,
    "username": None,
    "password": None
}

bravado_config = {
    'validate_swagger_spec': True,
    'validate_requests': False,
    'validate_responses': False,
    # if this is used a Bravdo-Core model is being returned
    # it does not simplify getting data from the API..
    'use_models': False,
    'also_return_response': True
}


# TODO cache with many api versions, more than one files is needed + download cache considering version api

class Client(object):
    def __init__(self, url, specs_path='api/v1/spec', port=None, api_key=None,
                 cache_path=None, force_cache=False, timeout=5, ssl_verify=True,
                 api_basePath=None, force_download_swag=True, auth_path="api/v1/api/api_key", logger=None):
        self.log = logger if logger else logging.getLogger(__name__)
        self._url = urlparse(url)
        self.api_basePath = api_basePath
        self.auth_path = auth_path
        self.force_download_swag = force_download_swag
        self.specs_url = urlparse(urljoin(url, specs_path))
        self.url = self._url.geturl()
        self.port = port if port else self._url.port
        self.timeout = timeout
        if cache_path and not cache_path.endswith('.json'):
            raise Exception("cache_path must end with .json extension")
        self.cache_path = cache_path
        self.ssl_verify = False if not ssl_verify else True
        self.http_client = RequestsClient(ssl_verify=self.ssl_verify)

        self.api_key = api_key

    def setup(self):
        if self.api_key:
            self.set_api_key(self.api_key)
        else:
            raise NotAuthorized('api-key is not set, please authenticate again')

        if self.force_download_swag is True:
            self.log.debug("force download swag is enabled")
            self.download_swag()
        self.init_swag()
        self.init_client()

    def set_api_key(self, api_key):
        self.http_client.set_api_key(
            host=self._url.hostname, api_key=api_key,
            param_name='api_key', param_in='query'
        )

    def download_swag(self):
        try:
            self.log.debug("downlading new swag def...")
            swag_dict = load_url(self.specs_url.geturl(), http_client=self.http_client)
            with open(self.cache_path, "w") as f:
                f.write(json.dumps(swag_dict))
            self.swag_dict = swag_dict
            # TODO fixed vxctl version
            self.swag_dict['basePath'] = urljoin(self._url.path, self.swag_dict['basePath'].replace('/', '', 1))
            self.log.debug("download complete")
        except HTTPForbidden:
            self.log.warning('unauthorized to fetch swagger-defintion from url: %s' % self.specs_url.geturl())
            raise NotAuthorized('unauthorized user')
        except HTTPNotFound:
            self.log.warning('could not fetch swagger-defintion from url: %s' % self.specs_url.geturl())
            raise EndpointURLNotFound('could not download definition from %s' % self.specs_url.geturl())
        return

    def init_swag(self):
        try:
            self.log.debug("loading swac dict from cache")
            self.swag_dict = load_file(self.cache_path)
        except URLError:
            self.download_swag()
            self.log.debug("could not read cache, rewrite it.")

    def reconfigure_swag(self):
        if self._url.port:
            self.log.debug("set host with port (%s:%d)" % (self._url.hostname, self._url.port))
            self.swag_dict['host'] = "{}:{}".format(self._url.hostname, self._url.port)
        else:
            self.log.debug("set host (%s)" % (self._url.hostname))
            self.swag_dict['host'] = self._url.hostname

        if "https" in self.url:
            self.log.debug("set SSL scheme")
            self.swag_dict['schemes'] = ['https']

        if self.api_basePath:
            self.log.debug("set api basePath (%s)" % (self.api_basePath))
            self.swag_dict['basePath'] = self.api_basePath

    def init_client(self):
        if not hasattr(self, 'swag_dict'):
            raise NoSwaggerDef('swagger def is missing')

        # fix the swag dict with data from config
        self.reconfigure_swag()

        self.swagclient = SwaggerClient.from_spec(self.swag_dict, http_client=self.http_client, config=bravado_config)

        # dynamic resources definition
        for tag_name in dir(self.swagclient):
            for resource_name in map(lambda n: n.replace('get', ''),
                                     filter(lambda m: m.startswith('get'),
                                            dir(getattr(self.swagclient, tag_name)))):
                # dynamic creation specific class
                # resource_class = type(resource_name, (Resource, object,), {})
                resource_class = Resource

                resource_module = 'pyvxclient.resources.{rsc_module}'.format(rsc_module=resource_name.lower())
                resource_module_spec = importlib.util.find_spec(resource_module)
                if resource_module_spec is not None:
                    resource_module_imported = importlib.import_module(resource_module)
                    resource_class_defined = getattr(resource_module_imported, resource_name, None)
                    if resource_class_defined:  # and issubclass(resource_class_defined, Resource)
                        resource_class = resource_class_defined

                resource_instance = resource_class(self.swagclient, tag_name, resource_name)

                setattr(self, resource_name, resource_instance)

    def get_token(self, user, password):
        try:
            ep = urljoin(self._url.geturl(), self.auth_path)
            result = requests.get(ep, auth=HTTPBasicAuth(user, password), timeout=self.timeout, verify=self.ssl_verify)
            result.raise_for_status()
            return result.json()
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 401:
                raise WrongCredentials('wrong username / password')
            else:
                raise EndpointURLNotFound(err)

                # self.print_html_doc()
