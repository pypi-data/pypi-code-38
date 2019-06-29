import importlib
import logging
import os
import pkgutil
import re


log = logging.getLogger(__name__)


def _import(path, continue_on_error):
    log.debug(f"Importing {path}")
    try:
        return importlib.import_module(path)
    except Exception as ex:
        log.exception(ex)
        if not continue_on_error:
            raise


def _load(path, include=".*", exclude="test", continue_on_error=True):
    if path.endswith(".py"):
        path, _ = os.path.splitext(path)

    path = path.rstrip("/").replace("/", ".")

    package = _import(path, continue_on_error)
    if not package:
        return

    do_include = re.compile(include).search if include else lambda x: True
    do_exclude = re.compile(exclude).search if exclude else lambda x: False

    if not hasattr(package, "__path__"):
        return

    prefix = package.__name__ + "."
    for _, name, is_pkg in pkgutil.iter_modules(path=package.__path__, prefix=prefix):
        if not name.startswith(prefix):
            name = prefix + name
        if is_pkg:
            _load(name, include, exclude, continue_on_error)
        else:
            if do_include(name) and not do_exclude(name):
                _import(name, continue_on_error)


def load(*paths, **kwargs):
    """
    Each path in paths should be a full package or module name. They are
    recursively imported.

    Args:
        paths (str): A package or module to load

    Keyword Args:
        include (str): A regular expression of packages and modules to include.
            Defaults to '.*'
        exclude (str): A regular expression of packges and modules to exclude.
            Defaults to 'test'
        continue_on_error (bool): If True, continue importing even if something
            raises an ImportError. If False, raise the first ImportError.

    Raises:
        ImportError
    """
    for path in paths:
        _load(path, **kwargs)
