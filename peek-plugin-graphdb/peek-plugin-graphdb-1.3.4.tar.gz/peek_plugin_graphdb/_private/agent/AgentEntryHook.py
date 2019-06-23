import logging

from peek_plugin_base.agent.PluginAgentEntryHookABC import PluginAgentEntryHookABC
from peek_plugin_graphdb.tuples import loadPublicTuples

logger = logging.getLogger(__name__)


class AgentEntryHook(PluginAgentEntryHookABC):

    def load(self) -> None:
        # Load public tuples so they can be serialised in the agent
        loadPublicTuples()

        logger.debug("Loaded")

    def start(self):
        pass

    def stop(self):
        pass

    def unload(self):
        logger.debug("Unloaded")
