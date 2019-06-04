import gc
import logging
import sys
from typing import Type, Tuple, Optional

import os
from abc import ABCMeta, abstractmethod, abstractproperty
from collections import defaultdict
from importlib.util import find_spec
from jsoncfg.value_mappers import require_string, require_array
from twisted.internet.defer import inlineCallbacks

from peek_platform import PeekPlatformConfig
from peek_plugin_base.PluginCommonEntryHookABC import PluginCommonEntryHookABC
from peek_plugin_base.PluginPackageFileConfig import PluginPackageFileConfig
from vortex.PayloadIO import PayloadIO
from vortex.Tuple import removeTuplesForTupleNames, registeredTupleNames, \
    tupleForTupleName
from vortex.TupleAction import TupleGenericAction, TupleUpdateAction
from vortex.TupleSelector import TupleSelector
from vortex.rpc.RPC import _VortexRPCResultTuple, _VortexRPCArgTuple

logger = logging.getLogger(__name__)

# This doesn't do anything, but it makes sure it's imported before any plugins import it.
TupleSelector()
TupleUpdateAction()
TupleGenericAction()
_VortexRPCResultTuple()
_VortexRPCArgTuple()

corePlugins = [
    "peek_core_email",
    "peek_core_device"
]


class PluginLoaderABC(metaclass=ABCMeta):
    _instance = None

    def __new__(cls, *args, **kwargs):
        assert cls._instance is None, "PluginServerLoader is a singleton, don't construct it"
        cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        self._loadedPlugins = {}

        self._vortexEndpointInstancesByPluginName = defaultdict(list)
        self._vortexTupleNamesByPluginName = defaultdict(list)

    @abstractproperty
    def _entryHookFuncName(self) -> str:
        """ Entry Hook Func Name.
        Protected property
        :return: EG  "peekServerEntryHook"

        """

    @abstractproperty
    def _entryHookClassType(self):
        """ Entry Hook Class Type
        Protected property
        :return: EG  PluginServerEntryHookABC

        """

    @abstractproperty
    def _platformServiceNames(self) -> [str]:
        """ Platform Service Name
        Protected property
        :return: one or more of "server", "worker", "agent", "client", "storage"

        """

    def pluginEntryHook(self, pluginName) -> Optional[PluginCommonEntryHookABC]:
        """ Plugin Entry Hook

        Returns the loaded plugin entry hook for the plugin name.

        :param pluginName: The name of the plugin to load

        :return: An instance of the plugin entry hook

        """
        return self._loadedPlugins.get(pluginName)

    @inlineCallbacks
    def loadPlugin(self, pluginName):
        try:
            self.unloadPlugin(pluginName)

            # Make note of the initial registrations for this plugin
            endpointInstancesBefore = set(PayloadIO().endpoints)
            tupleNamesBefore = set(registeredTupleNames())

            modSpec = find_spec(pluginName)
            if not modSpec:
                raise Exception("Failed to find package %s,"
                                " is the python package installed?" % pluginName)

            PluginPackage = modSpec.loader.load_module()
            pluginRootDir = os.path.dirname(PluginPackage.__file__)

            # Load up the plugin package info
            pluginPackageJson = PluginPackageFileConfig(pluginRootDir)
            pluginVersion = pluginPackageJson.config.plugin.version(require_string)
            pluginRequiresService = pluginPackageJson.config.requiresServices(
                require_array)

            # Make sure the service is required
            # Storage and Server are loaded at the same time, hence the intersection
            if not set(pluginRequiresService) & set(self._platformServiceNames):
                logger.debug("%s does not require %s, Skipping load",
                             pluginName, self._platformServiceNames)
                return

            # Get the entry hook class from the package
            entryHookGetter = getattr(PluginPackage, str(self._entryHookFuncName))
            EntryHookClass = entryHookGetter() if entryHookGetter else None

            if not EntryHookClass:
                logger.warning(
                    "Skipping load for %s, %s.%s is missing or returned None",
                    pluginName, pluginName, self._entryHookFuncName)
                return

            if not issubclass(EntryHookClass, self._entryHookClassType):
                raise Exception("%s load error, Excpected %s, received %s"
                                % (pluginName, self._entryHookClassType, EntryHookClass))

            ### Perform the loading of the plugin
            yield self._loadPluginThrows(pluginName, EntryHookClass,
                                         pluginRootDir, tuple(pluginRequiresService))

            # Make sure the version we have recorded is correct
            # JJC Disabled, this is just spamming the config file at the moment
            # PeekPlatformConfig.config.setPluginVersion(pluginName, pluginVersion)

            # Make note of the final registrations for this plugin
            self._vortexEndpointInstancesByPluginName[pluginName] = list(
                set(PayloadIO().endpoints) - endpointInstancesBefore)

            self._vortexTupleNamesByPluginName[pluginName] = list(
                set(registeredTupleNames()) - tupleNamesBefore)

            self.sanityCheckServerPlugin(pluginName)

        except Exception as e:
            logger.error("Failed to load plugin %s", pluginName)
            logger.exception(e)

    @abstractmethod
    def _loadPluginThrows(self, pluginName: str,
                          EntryHookClass: Type[PluginCommonEntryHookABC],
                          pluginRootDir: str,
                          requiresService: Tuple[str, ...]) -> None:
        """ Load Plugin (May throw Exception)

        This method is called to perform the load of the module.

        :param pluginName: The name of the Peek App, eg "plugin_noop"
        :param EntryHookClass: The plugin entry hook class to construct.
        :param pluginRootDir: The directory of the plugin package,
         EG dirname(plugin_noop.__file__)

        """

    def unloadPlugin(self, pluginName: str):
        oldLoadedPlugin = self._loadedPlugins.get(pluginName)

        if not oldLoadedPlugin:
            return

        del oldLoadedPlugin

        # Remove the registered endpoints
        for endpoint in self._vortexEndpointInstancesByPluginName[pluginName]:
            PayloadIO().remove(endpoint)
        del self._vortexEndpointInstancesByPluginName[pluginName]

        # Remove the registered tuples
        removeTuplesForTupleNames(self._vortexTupleNamesByPluginName[pluginName])
        del self._vortexTupleNamesByPluginName[pluginName]

        self._unloadPluginPackage(pluginName)

    def listPlugins(self):
        def pluginTest(name):
            if not name.startswith("plugin_"):
                return False
            return os.path.isdir(os.path.join(self._pluginPath, name))

        plugins = os.listdir(self._pluginPath)
        plugins = list(filter(pluginTest, plugins))
        return plugins

    # ---------------
    # Core Plugins

    @inlineCallbacks
    def loadCorePlugins(self):
        for pluginName in corePlugins:
            yield self.loadPlugin(pluginName)

    @inlineCallbacks
    def startCorePlugins(self):
        # Start the Plugin
        for pluginName in corePlugins:
            if pluginName not in self._loadedPlugins:
                continue

            yield self._tryStart(pluginName)

    @inlineCallbacks
    def stopCorePlugins(self):
        # Start the Plugin
        for pluginName in corePlugins:
            if pluginName not in self._loadedPlugins:
                continue

            yield self._tryStop(pluginName)

    def unloadCorePlugins(self):
        for pluginName in corePlugins:
            if pluginName in self._loadedPlugins:
                self.unloadPlugin(pluginName)

    # ---------------
    # Optional Plugins

    @inlineCallbacks
    def loadOptionalPlugins(self):
        for pluginName in PeekPlatformConfig.config.pluginsEnabled:
            if pluginName.startswith("peek_core"):
                raise Exception("Core plugins can not be configured")
            yield self.loadPlugin(pluginName)

    @inlineCallbacks
    def startOptionalPlugins(self):
        # Start the Plugin
        for pluginName in PeekPlatformConfig.config.pluginsEnabled:
            if pluginName not in self._loadedPlugins:
                continue

            yield self._tryStart(pluginName)

    @inlineCallbacks
    def stopOptionalPlugins(self):
        # Start the Plugin
        for pluginName in reversed(PeekPlatformConfig.config.pluginsEnabled):
            if pluginName not in self._loadedPlugins:
                continue

            yield self._tryStop(pluginName)

    def unloadOptionalPlugins(self):
        for pluginName in reversed(PeekPlatformConfig.config.pluginsEnabled):
            if pluginName in self._loadedPlugins:
                self.unloadPlugin(pluginName)

        remainingOptionalPlugins = list(filter(lambda n: not n.startswith("peek_core"),
                                               self._loadedPlugins))

        if remainingOptionalPlugins:
            logger.debug(remainingOptionalPlugins)
            raise Exception("Some plugins are still loaded")

    # ---------------
    # Util methods Plugins

    def _tryStart(self, pluginName):
        plugin = self._loadedPlugins[pluginName]
        try:
            return plugin.start()

        except Exception as e:
            logger.error("An exception occured while starting plugin %s,"
                         " starting continues" % pluginName)
            logger.exception(e)

    def _tryStop(self, pluginName):
        plugin = self._loadedPlugins[pluginName]
        try:
            return plugin.stop()

        except Exception as e:
            logger.error("An exception occured while stopping plugin %s,"
                         " stopping continues" % pluginName)
            logger.exception(e)

    def _unloadPluginPackage(self, pluginName):

        oldLoadedPlugin = self._loadedPlugins.get(pluginName)

        # Stop and remove the Plugin
        del self._loadedPlugins[pluginName]

        try:
            oldLoadedPlugin.unload()

        except Exception as e:
            logger.error("An exception occured while unloading plugin %s,"
                         " unloading continues" % pluginName)
            logger.exception(e)

        # Unload the packages
        loadedSubmodules = [modName
                            for modName in list(sys.modules.keys())
                            if modName.startswith('%s.' % pluginName)]

        for modName in loadedSubmodules:
            del sys.modules[modName]

        if pluginName in sys.modules:
            del sys.modules[pluginName]

        gc.collect()

        # pypy doesn't have getrefcount
        # ("oldLoadedPlugin" in this method and the call to getrefcount) == 2 references
        if hasattr(sys, "getrefcount") and sys.getrefcount(oldLoadedPlugin) > 2:
            logger.warning("Old references to %s still exist, count = %s",
                           pluginName, sys.getrefcount(oldLoadedPlugin))

        del oldLoadedPlugin
        gc.collect()
        # Now there should be no references.

    def sanityCheckServerPlugin(self, pluginName):
        ''' Sanity Check Plugin

        This method ensures that all the things registed for this plugin are
        prefixed by it's pluginName, EG plugin_noop
        '''

        # All endpoint filters must have the 'plugin' : 'plugin_name' in them
        for endpoint in self._vortexEndpointInstancesByPluginName[pluginName]:
            filt = endpoint.filt
            if 'plugin' not in filt and filt['plugin'] != pluginName:
                raise Exception("Payload endpoint does not contan 'plugin':'%s'\n%s"
                                % (pluginName, filt))

        # all tuple names must start with their pluginName
        for tupleName in self._vortexTupleNamesByPluginName[pluginName]:
            TupleCls = tupleForTupleName(tupleName)
            if not tupleName.startswith(pluginName):
                raise Exception("Tuple name does not start with '%s', %s (%s)"
                                % (pluginName, tupleName, TupleCls.__name__))

    def notifyOfPluginVersionUpdate(self, pluginName, pluginVersion):
        logger.info("Received PLUGIN update for %s version %s", pluginName, pluginVersion)
        return self.loadPlugin(pluginName)
