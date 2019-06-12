"""Returns appropriate storage provider based on the url provided"""
from __future__ import print_function

from pkg_resources import iter_entry_points

from .interface import Interface
from .util import path_from_uuid, format_hash, parse_storage_url

STORAGE_TYPES = {}
LOADED_TYPES = {}
DEFAULT_TYPE = None

def create_flywheel_fs(type_=None, config=None, creds=None):
    """
    This loads the storage provider based on the type and values supplied
    args:
        type_ String: Constant for the type of the plugin to load
        config dict: config for the plugin
        creds dict: creds for the plugin
    """
    if not STORAGE_TYPES:
        for entry_point in iter_entry_points('flywheel.storage'):
            STORAGE_TYPES[entry_point.name] = entry_point

    if type_ not in STORAGE_TYPES:
        raise ValueError('Could not load the storage type specified: {}'.format(type_))

    if type_ not in LOADED_TYPES:
        LOADED_TYPES[type_] = STORAGE_TYPES[type_].load()

    return LOADED_TYPES[type_](config=config, creds=creds)
