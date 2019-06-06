# -*- coding: utf-8 -*-
import os
import logging
import json

from .utils.os_utils import mkdir_recursive
from .eprint import eprint


def _config_folder_path():
    return os.path.join(os.path.expanduser('~'), '.MissingLinkAI')


def _defaults_path():
    return os.path.join(_config_folder_path(), 'defaults.json')


def get_defaults():
    try:
        with open(_defaults_path()) as f:
            return json.load(f)
    except ValueError:
        logging.warning('Defaults file at %s is corrupted', _defaults_path(), exc_info=1)
    except (IOError, OSError):
        pass

    return {}


def _set_defaults(data):
    mkdir_recursive(_config_folder_path())
    try:
        with open(_defaults_path(), 'w') as f:
            json.dump(data, f)
    except (IOError, OSError) as ex:
        eprint('Failed to save defaults to %s: %s', _defaults_path(), ex)
        logging.exception('Failed to save defaults to %s', _defaults_path())


def set_default(key, value):
    new_doc = get_defaults()
    new_doc[str(key)] = str(value)

    _set_defaults(new_doc)


def del_default(key):
    new_doc = get_defaults()
    val = new_doc.pop(key, None)
    if val is not None:
        logging.debug('Removing %s default value %s', key, val)

    _set_defaults(new_doc)


def get_default(val):
    return get_defaults().get(val)
