from typing import Type

from peek_plugin_base.agent.PluginAgentEntryHookABC import PluginAgentEntryHookABC
from peek_plugin_base.client.PluginClientEntryHookABC import PluginClientEntryHookABC
from peek_plugin_base.server.PluginServerEntryHookABC import PluginServerEntryHookABC
from peek_plugin_base.worker.PluginWorkerEntryHookABC import PluginWorkerEntryHookABC

__version__ = '1.3.3'


def peekServerEntryHook() -> Type[PluginServerEntryHookABC]:
    from ._private.server.ServerEntryHook import ServerEntryHook
    return ServerEntryHook


def peekAgentEntryHook() -> Type[PluginAgentEntryHookABC]:
    from ._private.agent.AgentEntryHook import AgentEntryHook
    return AgentEntryHook


def peekWorkerEntryHook() -> Type[PluginWorkerEntryHookABC]:
    from ._private.worker.WorkerEntryHook import WorkerEntryHook
    return WorkerEntryHook


def peekClientEntryHook() -> Type[PluginClientEntryHookABC]:
    from ._private.client.ClientEntryHook import ClientEntryHook
    return ClientEntryHook
