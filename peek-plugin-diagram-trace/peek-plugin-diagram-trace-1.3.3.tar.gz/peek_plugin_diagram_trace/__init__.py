
from peek_plugin_base.server.PluginServerEntryHookABC import PluginServerEntryHookABC
from peek_plugin_base.client.PluginClientEntryHookABC import PluginClientEntryHookABC
from typing import Type

__version__ = '1.3.3'


def peekServerEntryHook() -> Type[PluginServerEntryHookABC]:
    from ._private.server.ServerEntryHook import ServerEntryHook
    return ServerEntryHook


def peekClientEntryHook() -> Type[PluginClientEntryHookABC]:
    from ._private.client.ClientEntryHook import ClientEntryHook
    return ClientEntryHook
