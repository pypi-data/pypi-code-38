from importlib import import_module

from .api import API
from .exceptions import ClientException


class BSecureClient:
    DEFAULT_DOMAIN = 'bsec.me'
    DEFAULT_APIS = (
        'bsecure_client.api.integration_api',
        'bsecure_client.api.place_api',
        'bsecure_client.api.asset_api',
        'bsecure_client.api.routing_api'
    )

    def __init__(self, domain=None, encrypt=True, jwt=None):
        self.protocol = 'https' if encrypt else 'http'
        self.domain = domain or self.DEFAULT_DOMAIN
        self.jwt = jwt
        self.apis = []
        self.load_apis()

    def load_apis(self):
        for api_name in self.DEFAULT_APIS:
            module = import_module(api_name)
            for cls in module.__dict__.values():
                if self.is_valid_api(cls):
                    self.add_api(cls(self))

    def is_valid_api(self, cls):
        try:
            return issubclass(cls, API) and cls != API
        except TypeError:
            return False

    def add_api(self, api):
        self.apis.append(api)
        for attr_name in dir(api):
            attr = getattr(api, attr_name)
            if getattr(attr, 'expose', False):
                self.expose_api_method(attr_name, attr)

    def expose_api_method(self, name, method):
        if getattr(self, name, None) is not None:
            raise ClientException(f'Name already exists on client: {name}')
        setattr(self, name, method)
