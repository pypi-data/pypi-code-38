from typing import Type

from peek_plugin_base.agent.PluginAgentEntryHookABC import PluginAgentEntryHookABC
from peek_plugin_base.client.PluginClientEntryHookABC import PluginClientEntryHookABC
from peek_plugin_base.server.PluginServerEntryHookABC import PluginServerEntryHookABC
from peek_plugin_base.worker.PluginWorkerEntryHookABC import PluginWorkerEntryHookABC

__version__ = '1.3.1'


def peekClientEntryHook() -> Type[PluginClientEntryHookABC]:
    from peek_core_user._private.client.PluginClientEntryHook import \
        PluginClientEntryHook
    return PluginClientEntryHook


def peekAgentEntryHook() -> Type[PluginAgentEntryHookABC]:
    from ._private.agent.AgentEntryHook import AgentEntryHook
    return AgentEntryHook


def peekServerEntryHook() -> Type[PluginServerEntryHookABC]:
    from peek_core_user._private.server.PluginServerEntryHook import \
        PluginServerEntryHook
    return PluginServerEntryHook


def peekWorkerEntryHook() -> Type[PluginWorkerEntryHookABC]:
    from ._private.worker.WorkerEntryHook import WorkerEntryHook
    return WorkerEntryHook
