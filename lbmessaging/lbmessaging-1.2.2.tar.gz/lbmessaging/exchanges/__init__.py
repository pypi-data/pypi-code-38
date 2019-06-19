import importlib
import pkgutil

"""
Imports all the submodules in order to create their exposure in the annotated
services
"""
for _, name, __ in pkgutil.walk_packages(__path__,
                                         prefix=__name__ + '.'):
    if 'test' in name:
        continue
    importlib.import_module(name)
