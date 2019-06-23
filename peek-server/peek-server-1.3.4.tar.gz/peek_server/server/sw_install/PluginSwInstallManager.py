from peek_platform import PeekPlatformConfig
from peek_platform.sw_install.PluginSwInstallManagerABC import PluginSwInstallManagerABC


class PluginSwInstallManager(PluginSwInstallManagerABC):
    def notifyOfPluginVersionUpdate(self, pluginName, targetVersion):
        PeekPlatformConfig.pluginLoader.loadPlugin(pluginName)
        PeekPlatformConfig.pluginLoader.buildFrontend()

