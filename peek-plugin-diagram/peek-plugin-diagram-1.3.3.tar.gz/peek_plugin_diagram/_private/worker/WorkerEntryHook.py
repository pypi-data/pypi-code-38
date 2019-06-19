import logging
from peek_plugin_base.worker.PluginWorkerEntryHookABC import PluginWorkerEntryHookABC

from peek_plugin_diagram._private.worker.tasks import GridCompilerTask, \
    ImportDispTask, LiveDbDisplayValueConverterTask, DispCompilerTask, \
    LocationIndexCompilerTask
from peek_plugin_diagram._private.worker.tasks.branch import BranchIndexCompiler, \
    BranchIndexImporter, BranchIndexUpdater

logger = logging.getLogger(__name__)


class WorkerEntryHook(PluginWorkerEntryHookABC):
    def load(self):
        logger.debug("loaded")

    def start(self):
        logger.debug("started")

    def stop(self):
        logger.debug("stopped")

    def unload(self):
        logger.debug("unloaded")

    @property
    def celeryAppIncludes(self):
        return [BranchIndexUpdater.__name__,
                BranchIndexCompiler.__name__,
                BranchIndexImporter.__name__,
                DispCompilerTask.__name__,
                GridCompilerTask.__name__,
                LiveDbDisplayValueConverterTask.__name__,
                ImportDispTask.__name__,
                LocationIndexCompilerTask.__name__]

    @property
    def celeryApp(self):
        from .CeleryApp import celeryApp
        return celeryApp
