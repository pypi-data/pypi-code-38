import logging

from peek_plugin_inbox._private.client.ClientFeTupleActionProcessorProxy import \
    makeTupleActionProcessorProxy
from peek_plugin_inbox._private.client.ClientFeTupleDataObservableProxy import \
    makeTupleDataObservableProxy
from peek_plugin_inbox._private.storage.DeclarativeBase import loadStorageTuples
from peek_plugin_base.client.PluginClientEntryHookABC import PluginClientEntryHookABC
from peek_plugin_inbox.tuples import loadPublicTuples

logger = logging.getLogger(__name__)


class PluginClientEntryHook(PluginClientEntryHookABC):
    def __init__(self, *args, **kwargs):
        PluginClientEntryHookABC.__init__(self, *args, **kwargs)

        self._runningHandlers = []

    def load(self):
        loadStorageTuples()
        loadPublicTuples()
        logger.debug("loaded")

    def start(self):
        self._runningHandlers.append(makeTupleActionProcessorProxy())
        self._runningHandlers.append(makeTupleDataObservableProxy())
        logger.debug("started")

    def stop(self):
        while self._runningHandlers:
            self._runningHandlers.pop().shutdown()
        logger.debug("stopped")

    def unload(self):
        logger.debug("unloaded")
