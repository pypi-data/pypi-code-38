from qsa.ext.base import BaseExtension

from .secrets import ClientCertificateAdapter


class Extension(BaseExtension):
    name = command_name  = 'rdbms'

    def on_setup_secret_adapters(self, adapters):
        adapters.register(
            ClientCertificateAdapter())
