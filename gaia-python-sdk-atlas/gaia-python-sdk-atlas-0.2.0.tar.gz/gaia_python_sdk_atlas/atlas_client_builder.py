from gaia_python_sdk_api.client_options import ClientOptions
from gaia_python_sdk_api.transporter.http_transport import HttpTransport

from .atlas_client import AtlasClient


class AtlasClientBuilder(object):
    """
    Builder pattern implementation for AtlasClient instances.
    """

    @staticmethod
    def http(url):
        return AtlasClientBuilder(url)

    def __init__(self, url):
        self.url = url

    def with_apikey(self, apikey):
        self.apikey = apikey
        return self

    def with_secret(self, secret):
        self.secret = secret
        return self

    def build(self):
        return AtlasClient(HttpTransport(self.url, ClientOptions(self.apikey, self.secret)))
