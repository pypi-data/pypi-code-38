import logging

from peek_platform import PeekPlatformConfig
from peek_platform.sw_install.PeekSwInstallManagerABC import PeekSwInstallManagerABC

__author__ = 'synerty'

logger = logging.getLogger(__name__)


class PeekSwInstallManager(PeekSwInstallManagerABC):

    def __init__(self):
        PeekSwInstallManagerABC.__init__(self)
        self._restarting  = False

    def _stopCode(self):
        PeekPlatformConfig.pluginLoader.unloadAllPlugins()

    def _upgradeCode(self):
        pass

    def _startCode(self):
        PeekPlatformConfig.pluginLoader.loadAllPlugins()

    def restartProcess(self):
        # When we receive this signal, the processes have already been instructed
        # to shutdown

        self._restarting = True

        logger.info("Shutting down celery workers")
        from peek_worker.CeleryApp import celeryApp
        celeryApp.control.broadcast('shutdown')


    @property
    def restartTriggered(self):
        return self._restarting

    def realyRestartProcess(self):
        PeekSwInstallManagerABC.restartProcess(self)


