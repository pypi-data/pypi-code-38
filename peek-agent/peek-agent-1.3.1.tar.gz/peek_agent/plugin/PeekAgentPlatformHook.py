from typing import Optional

from peek_platform import PeekPlatformConfig
from peek_plugin_base.agent.PeekAgentPlatformHookABC import PeekAgentPlatformHookABC


class PeekAgentPlatformHook(PeekAgentPlatformHookABC):
    def getOtherPluginApi(self, pluginName: str) -> Optional[object]:
        pluginLoader = PeekPlatformConfig.pluginLoader

        otherPlugin = pluginLoader.pluginEntryHook(pluginName)
        if not otherPlugin:
            return None

        from peek_plugin_base.agent.PluginAgentEntryHookABC import PluginAgentEntryHookABC
        assert isinstance(otherPlugin, PluginAgentEntryHookABC), (
            "Not an instance of PluginAgentEntryHookABC")

        return otherPlugin.publishedAgentApi

    @property
    def peekServerHttpPort(self) -> int:
        from peek_platform import PeekPlatformConfig
        return PeekPlatformConfig.config.peekServerHttpPort

    @property
    def peekServerHost(self) -> str:
        from peek_platform import PeekPlatformConfig
        return PeekPlatformConfig.config.peekServerHost

    @property
    def serviceId(self) -> str:
        import socket
        return "agent|" + socket.gethostname()
