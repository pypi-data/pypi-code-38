from pathlib import Path

from peek_platform import PeekPlatformConfig
from peek_plugin_base.server.PeekPlatformServerHttpHookABC import PeekPlatformServerHttpHookABC
from peek_plugin_base.server.PeekPlatformAdminHttpHookABC import PeekPlatformAdminHttpHookABC
from peek_plugin_base.server.PeekServerPlatformHookABC import PeekServerPlatformHookABC


class PeekServerPlatformHook(PeekServerPlatformHookABC):
    def __init__(self, pluginName: str) -> None:
        PeekPlatformAdminHttpHookABC.__init__(self)
        PeekPlatformServerHttpHookABC.__init__(self)
        self._pluginName = pluginName

    @property
    def dbConnectString(self) -> str:
        from peek_platform import PeekPlatformConfig
        return PeekPlatformConfig.config.dbConnectString

    @property
    def fileStorageDirectory(self) -> Path:
        from peek_platform import PeekPlatformConfig

        return Path(PeekPlatformConfig.config.pluginDataPath(self._pluginName))

    def _getOtherPluginApi(self, pluginName):
        serverPluginLoader = PeekPlatformConfig.pluginLoader

        otherPlugin = serverPluginLoader.pluginEntryHook(pluginName)
        if not otherPlugin:
            return None

        from peek_plugin_base.server.PluginServerEntryHookABC import \
            PluginServerEntryHookABC

        assert isinstance(otherPlugin, PluginServerEntryHookABC), (
            "Not an instance of PluginServerEntryHookABC")

        return otherPlugin

    def getOtherPluginApi(self, pluginName):
        otherPlugin = self._getOtherPluginApi(pluginName)
        return otherPlugin.publishedServerApi if otherPlugin else None

    @property
    def serviceId(self) -> str:
        import socket
        return "server|" + socket.gethostname()
