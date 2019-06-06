from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_index_blueprint._private.PluginNames import indexBlueprintFilt
from peek_plugin_index_blueprint._private.PluginNames import indexBlueprintActionProcessorName
from vortex.handler.TupleActionProcessorProxy import TupleActionProcessorProxy


def makeTupleActionProcessorProxy():
    return TupleActionProcessorProxy(
                tupleActionProcessorName=indexBlueprintActionProcessorName,
                proxyToVortexName=peekServerName,
                additionalFilt=indexBlueprintFilt)
