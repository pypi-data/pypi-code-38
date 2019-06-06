import logging

from peek_plugin_base.client.PluginClientEntryHookABC import PluginClientEntryHookABC
from peek_core_user._private.client.TupleActionProcessorProxy import \
    makeTupleActionProcessorProxy
from peek_core_user._private.client.TupleDataObservableProxy import \
    makeTupleDataObservableProxy

logger = logging.getLogger(__name__)


class PluginClientEntryHook(PluginClientEntryHookABC):
    def __init__(self, *args, **kwargs):
        PluginClientEntryHookABC.__init__(self, *args, **kwargs)

        self._handlers = []

    def load(self):
        # Load the tuples, so that Payload can parse them
        from peek_core_user._private.tuples import loadPrivateTuples
        loadPrivateTuples()

        from peek_core_user._private.storage.DeclarativeBase import loadStorageTuples
        loadStorageTuples()

        from peek_core_user.tuples import loadPublicTuples
        loadPublicTuples()

        logger.debug("loaded")

    def start(self):
        self._handlers.append(makeTupleDataObservableProxy())
        self._handlers.append(makeTupleActionProcessorProxy())

        logger.debug("starting")

    def stop(self):
        for handler in self._handlers:
            handler.shutdown()

        logger.debug("stopped")

    def unload(self):
        logger.debug("unloaded")

