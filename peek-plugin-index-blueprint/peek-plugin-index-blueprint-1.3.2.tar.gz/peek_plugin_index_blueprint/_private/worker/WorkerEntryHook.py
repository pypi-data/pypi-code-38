import logging

from peek_plugin_base.worker.PluginWorkerEntryHookABC import PluginWorkerEntryHookABC
from peek_plugin_index_blueprint._private.storage.DeclarativeBase import loadStorageTuples
from peek_plugin_index_blueprint._private.tuples import loadPrivateTuples
from peek_plugin_index_blueprint._private.worker.tasks import ThingIndexCompiler, ThingIndexImporter
from peek_plugin_index_blueprint.tuples import loadPublicTuples

logger = logging.getLogger(__name__)


class WorkerEntryHook(PluginWorkerEntryHookABC):
    def load(self):
        loadPrivateTuples()
        loadStorageTuples()
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
        return [ThingIndexImporter.__name__,
                ThingIndexCompiler.__name__]

    @property
    def celeryApp(self):
        from .CeleryApp import celeryApp
        return celeryApp
