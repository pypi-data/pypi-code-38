from abc import abstractproperty

from celery.app.base import Celery
from peek_plugin_base.PluginCommonEntryHookABC import PluginCommonEntryHookABC
from peek_plugin_base.worker.PeekWorkerPlatformHookABC import PeekWorkerPlatformHookABC


class PluginWorkerEntryHookABC(PluginCommonEntryHookABC):
    def __init__(self, pluginName: str, pluginRootDir: str,
                 platform: PeekWorkerPlatformHookABC):
        PluginCommonEntryHookABC.__init__(self, pluginName=pluginName,
                                          pluginRootDir=pluginRootDir)
        self._platform = platform

    @property
    def platform(self) -> PeekWorkerPlatformHookABC:
        return self._platform

    @abstractproperty
    def celeryAppIncludes(self) -> [str]:
        """ Celery App Includes

        This property returns the absolout package paths to the modules with the tasks
        :Example: ["plugin_noop.worker.NoopWorkerTask"]

        :return: A list of package+module names that Celery should import.

        """

    @abstractproperty
    def celeryApp(self) -> Celery:
        """ Celery App

        Return the workers instance of the celery app.

        This will be configured with the platforms celery setup.

        """

        # There are no APIs
        # The worker threads can't access this.
