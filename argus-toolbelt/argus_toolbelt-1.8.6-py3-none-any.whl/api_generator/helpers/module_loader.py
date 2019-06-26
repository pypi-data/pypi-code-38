import importlib, pkgutil

from api_generator.helpers.log import log


def import_submodules(package: str, exclude_name: str = None, recursive=True) -> dict:
    """Import all submodules of a module, recursively. 

    This is used to import all APIs when Argus is loaded,
    so that the commands become registered as plugins,
    but can also be used to recursively import any other 
    package where you want every single file to load.

    TODO: Plugin loader can use this function to recursively
    load argus_plugins package!
    
    :param package_name: Package name, e.g "api_generator.api"
    :param exclude_name: Any module containing this string will not be imported
    """
    prefix = package
    package = importlib.import_module(package)

    results = {}

    for loader, name, is_pkg in pkgutil.iter_modules(package.__path__, prefix=prefix + '.'):
        if not exclude_name or exclude_name not in name:
            try:
                results[name] = importlib.import_module(name)
                if recursive and is_pkg:
                    results.update(import_submodules(name, exclude_name=exclude_name))
            except ImportError as e:
                log.exception(e)
    return results
