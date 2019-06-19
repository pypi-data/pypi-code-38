__version__ = '1.3.3'


from peek_plugin_base.server.PluginServerEntryHookABC import PluginServerEntryHookABC
from typing import Type

from peek_plugin_base.client.PluginClientEntryHookABC import PluginClientEntryHookABC


def peekClientEntryHook() -> Type[PluginClientEntryHookABC]:
    from ._private.client.ClientEntryHook import ClientEntryHook
    return ClientEntryHook


def peekServerEntryHook() -> Type[PluginServerEntryHookABC]:
    from ._private.server.ServerEntryHook import ServerEntryHook
    return ServerEntryHook
