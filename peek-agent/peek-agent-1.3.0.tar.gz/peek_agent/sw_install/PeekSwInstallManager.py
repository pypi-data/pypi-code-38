from peek_platform import PeekPlatformConfig
from peek_platform.sw_install.PeekSwInstallManagerABC import PeekSwInstallManagerABC

__author__ = 'synerty'


class PeekSwInstallManager(PeekSwInstallManagerABC):

    def _stopCode(self):
        PeekPlatformConfig.pluginLoader.stopOptionalPlugins()
        PeekPlatformConfig.pluginLoader.stopCorePlugins()
        PeekPlatformConfig.pluginLoader.unloadOptionalPlugins()
        PeekPlatformConfig.pluginLoader.unloadCorePlugins()

    def _upgradeCode(self):
        pass

    def _startCode(self):
        PeekPlatformConfig.pluginLoader.loadCorePlugins()
        PeekPlatformConfig.pluginLoader.loadOptionalPlugins()

        PeekPlatformConfig.pluginLoader.startCorePlugins()
        PeekPlatformConfig.pluginLoader.startOptionalPlugins()



