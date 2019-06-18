# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module contains the Manager class for Plugins in the fastr system
"""

import collections.abc
import sys
from types import ModuleType

from ...abc.baseplugin import BasePlugin, Plugin
from ...abc.basepluginmanager import BasePluginManager
from ...helpers import config, log


class PluginsView(collections.abc.MutableMapping):
    """
    A collection that acts like view of the plugins of another plugin manager.
    This is a proxy object that only gives access the plugins of a certain
    plugin class. It behaves like a mapping and is used as the data object for
    a PluginSubManager.
    """
    def __init__(self, parent, plugin_class):
        """
        Constructor for the plugins view

        :param BasePluginManager parent: the parent plugin manager
        :param class plugin_class: the class of the plugins to expose
        """
        self.plugin_class = plugin_class
        self.parent = parent

    def filter_plugin(self, plugin):
        if self.plugin_class.instantiate and isinstance(plugin, self.plugin_class):
            return True
        elif not self.plugin_class.instantiate and (isinstance(plugin, type) and issubclass(plugin, self.plugin_class)):
            return True
        else:
            return False

    def __getitem__(self, item):
        result = self.parent[item]

        if not self.filter_plugin(plugin=result):
            raise KeyError(item)

        return result

    def __setitem__(self, key, value):
        if not self.filter_plugin(value):
            raise TypeError(value)

        if key in self.parent and not self.filter_plugin(self.parent[key]):
            raise TypeError(key)

        self.parent[key] = value

    def __delitem__(self, key):
        if key in self.parent and not self.filter_plugin(self.parent[key]):
            raise TypeError(key)

        del self.parent[key]

    def __len__(self):
        return sum(1 for v in self.parent.values() if self.filter_plugin(v))

    def __iter__(self):
        for key, value in self.parent.items():
            if not self.filter_plugin(value):
                continue

            yield key


class PluginSubManager(BasePluginManager):
    """
    A PluginManager that is a selection of a parent plugin manger. It uses the
    PluginsView to only exponse part of the parent PluginManager. This is used
    to create plugin plugins.managers for only certain types of plugins (e.g. IOPlugins)
    without loading them multiple times.
    """
    def __init__(self, parent, plugin_class):
        self.parent = parent
        self._plugin_class = plugin_class
        self._data_link = PluginsView(parent=parent, plugin_class=plugin_class)
        super().__init__()

    @property
    def data(self):
        return self._data_link

    @property
    def plugin_class(self):
        """
        PluginSubManagers only expose the plugins of a certain class
        """
        return self._plugin_class


class PluginManager(BasePluginManager):
    def __init__(self, path=None):
        if path is None:
            path = config.plugins_path

        super().__init__(path=path, recursive=True)

    @property
    def plugin_class(self):
        """
        The plugin manager contains any Plugin subclass
        """
        return Plugin

    def __setitem__(self, key, value):
        """
        Store an item in the BaseManager, will ignore the item if the key is
        already present in the BaseManager.

        :param name: the key of the item to save
        :param value: the value of the item to save
        :return: None
        """
        if not (isinstance(value, Plugin) or issubclass(value, Plugin)):
            raise TypeError(value)

        super(PluginManager, self).__setitem__(key, value)

    def _store_item(self, name, value):
        """
        Store an item in the BaseManager, will ignore the item if the key is
        already present in the BaseManager.

        :param name: the key of the item to save
        :param value: the value of the item to save
        :return: None
        """
        if name in list(self.keys()):
            log.warning('Skipping {} from {} (the plugin is already in the {})'.format(name, value.filename, type(self).__name__))
        else:

            # Set the module to the fastr plugins
            if isinstance(value, BasePlugin):
                type(value).__module__ = 'fastr.plugins'
                setattr(self._module, value.id, type(value))
            else:
                value.__module__ = 'fastr.plugins'
                setattr(self._module, value.id, value)

            self[name] = value
