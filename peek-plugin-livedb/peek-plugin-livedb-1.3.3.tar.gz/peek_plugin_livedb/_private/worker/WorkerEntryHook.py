import logging

from peek_plugin_base.worker.PluginWorkerEntryHookABC import PluginWorkerEntryHookABC
from peek_plugin_livedb._private.storage.DeclarativeBase import loadStorageTuples
from peek_plugin_livedb._private.tuples import loadPrivateTuples
from peek_plugin_livedb._private.worker.tasks import LiveDbItemImportTask, \
    LiveDbItemUpdateTask, BulkLoadChunkTask
from peek_plugin_livedb.tuples import loadPublicTuples

logger = logging.getLogger(__name__)


class WorkerEntryHook(PluginWorkerEntryHookABC):
    def load(self):
        loadStorageTuples()
        loadPrivateTuples()
        loadPublicTuples()

        logger.debug("loaded")

    def start(self):
        logger.debug("started")

    def stop(self):
        logger.debug("stopped")

    def unload(self):
        logger.debug("unloaded")

    @property
    def celeryAppIncludes(self):
        return [LiveDbItemImportTask.__name__,
                LiveDbItemUpdateTask.__name__,
                BulkLoadChunkTask.__name__]

    @property
    def celeryApp(self):
        from .CeleryApp import celeryApp
        return celeryApp
