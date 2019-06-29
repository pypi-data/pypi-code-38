from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_chat._private.PluginNames import chatFilt
from peek_plugin_chat._private.PluginNames import chatActionProcessorName
from vortex.handler.TupleActionProcessorProxy import TupleActionProcessorProxy


def makeTupleActionProcessorProxy():
    return TupleActionProcessorProxy(
                tupleActionProcessorName=chatActionProcessorName,
                proxyToVortexName=peekServerName,
                additionalFilt=chatFilt)