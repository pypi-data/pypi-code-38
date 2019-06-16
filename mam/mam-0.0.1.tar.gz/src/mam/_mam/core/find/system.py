"""Find system."""

import os.path
import pkgutil
from typing import Optional, Tuple, cast

from .objects import System

__all__ = [
    'find_system',
]


def normalize_path(path: str) -> str:
    """Normalize path."""
    return path.replace('\\', '/')


def split_module(path: str) -> Tuple[Optional[str], Optional[str]]:
    """Split module and system path."""
    if not path.startswith('@'):
        return None, path

    index = path.find('/')
    if index == -1:
        return path[1:], None
    else:
        return path[1:index], path[index + 1:]


def normalize_filesystem(file_system: str) -> System:
    """Normalize filesystem path."""
    if not os.path.isabs(file_system):
        file_system = os.path.abspath(file_system)
    return System(None, file_system)


def normalize_module_path(module: str, file_system: str) -> System:
    """Normalize module and system path."""
    # nosa: mypy[:"Loader" has no attribute]
    # TODO: find out how to fix these errors.
    loader = pkgutil.get_loader(module)
    if not loader.is_package(module):
        raise FileNotFoundError(
            'Can only find files relative to a package.'
            ' {package_name!r} is a module.'
            .format(package_name=module),
        )
    if os.path.isabs(file_system):
        raise ValueError(
            'File system path must be relative when module is set.',
        )
    package_path = os.path.dirname(loader.path)
    return System(
        None,
        os.path.normpath(os.path.join(package_path, file_system)),
    )


def normalize_module(module: str) -> System:
    """Normalize module path."""
    # nosa: mypy[:"Loader" has no attribute]
    loader = pkgutil.get_loader(module)
    if loader is None:
        raise ValueError('Unknown module {0}'.format(module))
    path = loader.path
    if not os.path.isabs(path):
        path = os.path.abspath(path)
    return System(loader.load_module(module), path)


def normalize_output(module: Optional[str], file_system: Optional[str],
                     ) -> System:
    """Normalize path."""
    if module is None and file_system is None:
        return System(None, None)
    if module is None:
        # file_system cannot be None here.
        return normalize_filesystem(cast(str, file_system))
    if file_system is not None:
        return normalize_module_path(module, file_system)
    return normalize_module(module)


def find_system(path: str) -> System:
    """Find system path."""
    path = normalize_path(path)
    module, file_system = split_module(path)
    return normalize_output(module, file_system)
