"""Returns appropriate storage provider based on the url provided"""
from __future__ import print_function

from pkg_resources import iter_entry_points

from .interface import Interface
from .util import path_from_uuid, format_hash, parse_storage_url

STORAGE_TYPES = {}
LOADED_TYPES = {}
DEFAULT_TYPE = None

def create_flywheel_fs(url, default='osfs'):
    """
    This loads the storage provider based on the url provided
    """
    if not STORAGE_TYPES:
        for entry_point in iter_entry_points('flywheel.storage'):
            STORAGE_TYPES[entry_point.name] = entry_point

    protocol = None
    url_parts = parse_storage_url(url)
    if url_parts[0]:
        protocol = url_parts[0]

    if protocol and protocol in STORAGE_TYPES:
        if protocol not in LOADED_TYPES:
            LOADED_TYPES[protocol] = STORAGE_TYPES[protocol].load()
        return LOADED_TYPES[protocol](url)

    if default in STORAGE_TYPES:
        if default not in LOADED_TYPES:
            LOADED_TYPES[default] = STORAGE_TYPES[default].load()
        # Assume the rest are paths which we can use with osfs even though they are not urls
        return LOADED_TYPES[default](url)

    raise ValueError('Could not load the storage type specified: {}'.format(protocol if protocol else default))
