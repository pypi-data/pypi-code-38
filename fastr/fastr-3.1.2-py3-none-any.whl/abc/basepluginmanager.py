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

import collections
import imp
import inspect
import os
import sys
import traceback
from abc import abstractproperty

from .basemanager import BaseManager
from .baseplugin import BasePlugin, PluginState
from .. import exceptions
from ..helpers import log


plugin_option_type = collections.namedtuple('plugin_option_type', ['filename', 'name', 'namespace', 'id'])


class BasePluginManager(BaseManager):
    """
    Baseclass for PluginManagers, need to override the self._plugin_class
    """

    def __init__(self, path=None, recursive=False, module=None):
        """
        Create a BasePluginManager and scan the give path for matching plugins

        :param str path: path to scan
        :param bool recursive: flag to indicate a recursive search
        :param module module: the module to register plugins into
        :return: newly created plugin manager
        :raises FastrTypeError: if self._plugin_class is set to a class not
                                 subclassing BasePlugin
        """
        self._loaded_plugins = {}
        self._plugin_options = {}
        self._module = module

        super(BasePluginManager, self).__init__(path, recursive)

        if not issubclass(self.plugin_class, BasePlugin):
            raise exceptions.FastrTypeError(
                'Plugin type to manage ({}) not a valid plugin! (needs to be subclass of BasePlugin)'.format(
                    self.plugin_class.__name__
                )
            )

    def set_module(self, module):
        if self._module is not None:
            raise ValueError('Cannot reset module!')
        self._module = module

    def test_plugin(self, plugin):
        # Since we cannot know what Plugins might throw, catch all
        # pylint: disable=broad-except
        try:
            # Let the Plugin think it is loaded, or it will refuse to instantiate
            plugin.set_status(PluginState.preload, 'Set to PreLoad to perform testing')
            plugin.test()
            # Let the Plugin think it is loaded, or it will refuse to instantiate
            plugin.set_status(PluginState.loaded, 'Testing successful, loaded properly')
        # Register the configuration for the plugin
        except Exception as exception:
            log.info('Could not load plugin file {}\n{}'.format(plugin.filename, exception))
            exc_type, _, _ = sys.exc_info()
            exc_info = traceback.format_exc()
            log.debug('Encountered exception ({}) during instantiation of the plugin:\n{}'.format(
                exc_type.__name__, exc_info)
            )
            exception_stacktrace = ('Encountered exception ({}) during'
                                    ' instantiation of the plugin:\n{}').format(exc_type.__name__, exc_info)
            exception_message = '[{}] {}'.format(plugin.fullid, exception.message)
            plugin.set_status(PluginState.failed, exception_message, exception_stacktrace)

    def __getitem__(self, key):
        """
        Retrieve item from BaseManager

        :param key: the key of the item to retrieve
        :return: the value indicated by the key
        :raises FastrKeyError: if the key is not found in the BaseManager
        """
        try:
            plugin = super(BasePluginManager, self).__getitem__(key)
        except exceptions.FastrKeyError:
            self.load_plugin(key.lower())

            plugin = super(BasePluginManager, self).__getitem__(key)

        if plugin.status not in [PluginState.loaded, PluginState.failed]:
            self.test_plugin(plugin)

        return plugin

    @abstractproperty
    def plugin_class(self):
        """
        The class from which the plugins must be subclassed
        """
        raise exceptions.FastrNotImplementedError

    @property
    def _item_extension(self):
        """
        Plugins should be loaded from files with a .py extension
        """
        return '.py'

    @property
    def _instantiate(self):
        """
        Flag indicating that the plugin should be instantiated prior to saving
        """
        return True

    def _print_key(self, key):
        print_out = (self[key].status.value, key)

        return print_out

    def _print_value(self, val):
        """
        Function for printing values (plugins) in this manager

        :param BasePlugin val: value to print
        :return: print representation
        :rtype: str
        """
        if val._instantiate:
            val = type(val)

        print_out = '<{}: {}>'.format(val.__bases__[0].__name__, val.__name__)
        return print_out

    def _load_item(self, filepath, namespace):
        """
        Load a plugin

        :param str filepath: path of the plugin to load
        """
        name = os.path.basename(filepath)
        name = os.path.splitext(name)[0].lower()

        value = plugin_option_type(filename=filepath, name=name, namespace=namespace, id=None)

        self._plugin_options[name] = value

    def populate(self):
        """
        Populate the manager with the data. This is a method that will be
        called when the Managers data is first accessed. This way we avoid
        doing expensive directory scans when the data is never requested.
        """
        super().populate()

        # Use list to avoid changing dictionary during loop
        for plugin_key in list(self._plugin_options.keys()):
            if plugin_key in self._plugin_options:
                self.load_plugin(plugin_key)

    def load_plugin(self, plugin_key):
        plugin_option = self._plugin_options[plugin_key]
        filepath = plugin_option.filename

        # Since we cannot know what Plugins might throw, catch all
        # pylint: disable=broad-except
        try:
            filebase, _ = os.path.splitext(os.path.basename(filepath))
            temp_module = imp.load_source(filebase, filepath)
            for name, obj in inspect.getmembers(temp_module):
                if not inspect.isclass(obj):
                    continue

                if filebase.lower() != obj.__name__.lower():
                    log.debug('Plugin name and module do not match ({} vs {})'.format(obj.__name__, filebase))
                    continue

                if not issubclass(obj, self.plugin_class):
                    log.debug('{} is not a subclass of {}'.format(obj, self.plugin_class))
                    continue

                obj.filename = filepath
                if inspect.isabstract(obj):
                    log.debug('Skipping abstract Plugin: {} ({})'.format(name, filepath))
                    continue

                if obj.status == PluginState.uninitialized:
                    obj.register_configuration()
                elif obj.status not in (PluginState.loaded, PluginState.failed):
                    log.warning('Invalid Plugin status: {}!'.format(obj.status))

                # Save the source in the obj
                obj.set_code(inspect.getsource(obj))
                obj.module = temp_module

                if obj.instantiate:
                    log.debug('Store instantiated plugin')
                    self.test_plugin(obj)
                    if obj.status == PluginState.loaded:
                        self._store_item(name, obj())
                    else:
                        self._store_item(name, obj)
                else:
                    log.debug('Store uninstantiated plugin')
                    self._store_item(name, obj)

        except Exception as exception:
            log.warning('Could not load {} file {}\n{}'.format(self.plugin_class.__name__, filepath, exception))
            exc_type, _, _ = sys.exc_info()
            exc_info = traceback.format_exc()
            log.info('Encountered exception ({}) during loading of the plugin:\n{}'.format(exc_type.__name__, exc_info))
        finally:
            del self._plugin_options[plugin_key]


