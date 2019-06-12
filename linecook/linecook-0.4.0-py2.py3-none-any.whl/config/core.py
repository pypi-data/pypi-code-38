# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import imp
from os import path

from .. import recipes
from .parsers import collect_recipes, collect_tranforms


# File configuration order: Files later in the list override earlier ones.
CONFIG_SEARCH_PATHS = [
    path.expanduser('~/.linecook/config.py'),
    path.abspath('./.linecook/config.py'),
]


DEFAULT_LINECOOK_CONFIG = {
    'recipes': {
        'identity': [],  # Recipe that does noting; useful for testing.
        'default': [],

        'python': recipes.python.recipe,
        'dpkg.log': recipes.dpkg_log.recipe,
    },
}


class LineCookConfig(object):
    """Configuration for `linecook` parsed from known configuration files.

    Attributes:
        transforms (dict): Named transforms available for recipes.
        recipes (dict): Named recipes, which are simply text transforms, or
            sequences of transforms, that are applied to each line of text.

    See `load_config` for a description of known configuration files, and
    hierarchical configuration works.

    """

    def __init__(self, config_dicts):
        self.transforms = collect_tranforms(config_dicts)
        self.recipes = collect_recipes(config_dicts, self.transforms)


def _load_config_file_from_path(path):
    try:
        module = imp.load_source('linecook_custom_config', path)
        return module.LINECOOK_CONFIG
    except (IOError, OSError):
        return {}


def load_config():
    """Return `LineCookConfig` reduced from all known configuration files.

    The following configuration files are loaded, in order:

        - `linecook.config.core`
        - `~/.linecook/config.py`
        - `./.linecook/config.py`

    Each file should define a dictionary named `LINECOOK_CONFIG` containing
    keys such as `transforms` and `recipes`.

    Files loaded later (lower on the list) override values loaded earlier. Note
    that the overriding happens at the *second* level of dictionaries. For
    example, if `~/.linecook/config.py` is defined as::

        from linecook.transforms.core import color_text

        LINECOOK_CONFIG = {
            'transforms': {
                'warn_color': color_text(' WARN ', color='yellow'),
                'error_color': color_text(' ERROR ', on_color='on_red'),
            },
            'recipes': {
                'logs': ['warn_color', 'error_color'],
                'default': ['warn_color', 'error_color'],
            },
        }

    And then, `./.linecook/config.py` is defined as::

        from linecook.transforms.core import filter_line

        LINECOOK_CONFIG = {
            'recipes': {
                'default': [filter_line(' DEBUG '), 'error_color']
            },
        }

    The loaded result would roughly translate to::

        LINECOOK_CONFIG = {
            'transforms': {
                'warn_color': color_text(' WARN ', color='yellow'),
                'error_color': color_text(' ERROR ', on_color='on_red'),
            },
            'recipes': {
                'logs': ['warn_color', 'error_color'],
                'default': [filter_line(' DEBUG '), 'error_color']
            },
        }

    You'll notice that `recipes` doesn't match the `recipes` in the second
    config file: Instead, the second file only overrode the `'default'` value
    in the first config file, but preseved the `'logs'` value.
    """
    config_dicts = [DEFAULT_LINECOOK_CONFIG]
    config_dicts.extend(_load_config_file_from_path(file_path)
                        for file_path in CONFIG_SEARCH_PATHS)
    return LineCookConfig(config_dicts)
