from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_core_search._private.PluginNames import searchFilt
from peek_core_search._private.PluginNames import searchActionProcessorName
from vortex.handler.TupleActionProcessorProxy import TupleActionProcessorProxy


def makeTupleActionProcessorProxy():
    return TupleActionProcessorProxy(
                tupleActionProcessorName=searchActionProcessorName,
                proxyToVortexName=peekServerName,
                additionalFilt=searchFilt)
