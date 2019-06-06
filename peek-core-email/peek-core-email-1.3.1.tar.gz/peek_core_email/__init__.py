from typing import Type

from peek_plugin_base.client.PluginClientEntryHookABC import PluginClientEntryHookABC
from peek_plugin_base.server.PluginServerEntryHookABC import PluginServerEntryHookABC

__version__ = '1.3.1'


def peekServerEntryHook() -> Type[PluginServerEntryHookABC]:
    from peek_core_email._private.server.PluginServerEntryHook import \
        PluginServerEntryHook
    return PluginServerEntryHook


def peekClientEntryHook() -> Type[PluginClientEntryHookABC]:
    from peek_core_email._private.client.PluginClientEntryHook import \
        PluginClientEntryHook
    return PluginClientEntryHook

