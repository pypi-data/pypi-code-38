import logging

import sys
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.trial import unittest

from .AgentPluginLoader import AgentPluginLoader

logger = logging.getLogger(__name__)

PLUGIN_NOOP = "plugin_noop"


class AgentPluginLoaderTest(unittest.TestCase):
    def testLoadAll(self):
        AgentPluginLoader.loadCorePlugins()
        AgentPluginLoader.loadOptionalPlugins()

        AgentPluginLoader.startCorePlugins()
        AgentPluginLoader.startOptionalPlugins()


        logger.info(AgentPluginLoader.listPlugins())

        for plugin in list(AgentPluginLoader._loadedPlugins.values()):
            logger.info("configUrl = %s", plugin.configUrl())

        d = Deferred()
        reactor.callLater(5.0, d.callback, True)
        return d

    def testUnregister(self):
        loadedModuleBefore = set(sys.modules)

        AgentPluginLoader.loadPlugin(PLUGIN_NOOP)
        self.assertTrue(PLUGIN_NOOP in sys.modules)

        AgentPluginLoader.unloadPlugin(PLUGIN_NOOP)

        loadedModuleNow = set(sys.modules) - loadedModuleBefore

        # Ensure that none of the modules contain the plugin_name
        for modName in loadedModuleNow:
            self.assertFalse(PLUGIN_NOOP in modName)

    def testReRegister(self):
        AgentPluginLoader.loadPlugin(PLUGIN_NOOP)
        AgentPluginLoader.loadPlugin(PLUGIN_NOOP)

        for plugin in list(AgentPluginLoader._loadedPlugins.values()):
            logger.info("configUrl = %s", plugin.configUrl())

        d = Deferred()
        reactor.callLater(5.0, d.callback, True)
        return d
