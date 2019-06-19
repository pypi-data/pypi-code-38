from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_graphdb._private.PluginNames import graphDbFilt
from peek_plugin_graphdb._private.PluginNames import graphDbActionProcessorName
from vortex.handler.TupleActionProcessorProxy import TupleActionProcessorProxy


def makeTupleActionProcessorProxy():
    return TupleActionProcessorProxy(
                tupleActionProcessorName=graphDbActionProcessorName,
                proxyToVortexName=peekServerName,
                additionalFilt=graphDbFilt)
