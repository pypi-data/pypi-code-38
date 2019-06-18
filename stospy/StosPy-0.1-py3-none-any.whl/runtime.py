from importlib import import_module

from .backends import Backend
from .config import config


class Runtime:
    backend: Backend

    def __getattr__(self, item):
        if item == "backend":
            package_name, backend_name = config.BACKEND.rsplit(".", 1)
            package = import_module(package_name)
            backend_class = getattr(package, backend_name)
            self.backend = backend_class()
            return self.backend


runtime = Runtime()
