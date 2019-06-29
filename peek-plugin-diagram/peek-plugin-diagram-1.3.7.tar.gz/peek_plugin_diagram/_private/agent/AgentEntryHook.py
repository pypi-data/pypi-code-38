import logging

from peek_plugin_base.agent.PluginAgentEntryHookABC import PluginAgentEntryHookABC

# from peek_plugin_diagram._private.storage.DeclarativeBase import loadStorageTuples
# from peek_plugin_diagram._private.tuples import loadPrivateTuples
from peek_plugin_diagram.tuples import loadPublicTuples

logger = logging.getLogger(__name__)


class AgentEntryHook(PluginAgentEntryHookABC):

    def load(self) -> None:
        # loadStorageTuples()
        # loadPrivateTuples()
        loadPublicTuples()

        logger.debug("Loaded")

    def start(self):
        pass

    def stop(self):
        pass

    def unload(self):
        logger.debug("Unloaded")
