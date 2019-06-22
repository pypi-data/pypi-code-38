# -*- coding: utf-8 -*-
"""Data structure defining a plugin, i.e., a set of pypes."""

import getpass
import importlib
from os import path
from re import sub
from sys import path as syspath

from pype.exceptions import PypeException
from pype.type_pype import Pype
from pype.util.iotools import get_immediate_subfiles, resolve_path


class Plugin():
    """Data structure defining a plugin, i.e., a set of pypes."""

    def __init__(self, plugin_config, config_path):
        """Activate plugins for the provided configuration."""
        self.active = False
        if not self.__valid_for_user(plugin_config):
            return
        if 'path' in plugin_config:
            # plugin pype
            self.name = plugin_config['name']
            self.internal = False
            python_abspath = path.join(resolve_path(
                self.__handle_relative_path(
                    plugin_config['path'],
                    config_path
                )))
            syspath.append(python_abspath)
            self.abspath = path.join(python_abspath, plugin_config['name'])
        else:
            # internal pype
            self.name = 'pype.' + plugin_config['name']
            self.internal = True
            self.abspath = path.join(path.dirname(
                __file__), plugin_config['name'])
        try:
            self.module = importlib.import_module(self.name)
        except ModuleNotFoundError:  # noqa: F821
            raise PypeException('No plugin named "{}" found at {}'
                                .format(self.name, self.abspath))
        self.doc = self.__get_docu_or_default(self.module)
        self.pypes = [
            Pype(path.join(self.abspath, subfile), subfile, self)
            for subfile in
            get_immediate_subfiles(self.abspath, r'^(?!__).*(?!__)\.py$')
        ]
        self.active = True

    def __handle_relative_path(self, plugin_path, config_path):
        if not plugin_path.startswith('./'):
            return plugin_path
        return sub(r'^\./', path.dirname(config_path) + '/', plugin_path)

    def __get_docu_or_default(self, module):
        return (
            sub(r'[\.]+$', '', module.__doc__)  # replace trailing dots
            if module.__doc__ else 'Not documented yet'
        )

    def __valid_for_user(self, plugin_config):
        plugin_users = plugin_config.get('users', [])
        if len(plugin_users) == 0:
            return True
        username = getpass.getuser()
        if any([user for user in plugin_users if user == username]):
            return True
        return False
