from qsa.ext.base import BaseExtension

from .secrets import DatabaseConnectionAdapter


class Extension(BaseExtension):
    name = command_name  = 'laravel'

    def on_setup_secret_adapters(self, adapters):
        adapters.register(
            DatabaseConnectionAdapter())

