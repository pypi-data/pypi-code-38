import pkgutil as __pkgutil

__path__ = __pkgutil.extend_path(__path__, __name__)
for __importer, __modname, __ispkg in __pkgutil.walk_packages(path=__path__, prefix=__name__ + '.'):
    __import__(__modname)
