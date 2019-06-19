import logging

from peek_plugin_base.client.PluginClientEntryHookABC import PluginClientEntryHookABC
from peek_plugin_livedb._private.storage.DeclarativeBase import loadStorageTuples
from peek_plugin_livedb.tuples import loadPublicTuples

logger = logging.getLogger(__name__)


class ClientEntryHook(PluginClientEntryHookABC):
    def load(self) -> None:
        loadStorageTuples()
        # loadPrivateTuples()
        loadPublicTuples()

        logger.debug("Loaded")

    def start(self):
        logger.debug("Started")

    def stop(self):
        logger.debug("Stopped")

    def unload(self):
        logger.debug("Unloaded")
