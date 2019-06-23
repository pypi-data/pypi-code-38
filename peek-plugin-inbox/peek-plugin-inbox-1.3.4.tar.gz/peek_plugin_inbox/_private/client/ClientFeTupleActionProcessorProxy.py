from vortex.handler.TupleActionProcessorProxy import TupleActionProcessorProxy

from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_inbox._private.PluginNames import inboxFilt, \
    inboxActionProcessorName


def makeTupleActionProcessorProxy():
    return TupleActionProcessorProxy(
        tupleActionProcessorName=inboxActionProcessorName,
        proxyToVortexName=peekServerName,
        additionalFilt=inboxFilt)
