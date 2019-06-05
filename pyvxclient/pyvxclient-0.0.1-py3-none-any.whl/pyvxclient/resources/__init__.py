from .resources import REGISTERED_RESOURCES
import pkgutil

__limit__ = 1000

__path__ = pkgutil.extend_path(__path__, __name__)
for importer, modname, ispkg in pkgutil.walk_packages(path=__path__, prefix=__name__ + '.'):
    __import__(modname)

__all__ = [
    'REGISTERED_RESOURCES'
]
