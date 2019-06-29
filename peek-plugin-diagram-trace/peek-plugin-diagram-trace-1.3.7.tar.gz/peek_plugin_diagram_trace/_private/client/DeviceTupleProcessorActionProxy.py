from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_diagram_trace._private.PluginNames import diagramTraceFilt
from peek_plugin_diagram_trace._private.PluginNames import diagramTraceActionProcessorName
from vortex.handler.TupleActionProcessorProxy import TupleActionProcessorProxy


def makeTupleActionProcessorProxy():
    return TupleActionProcessorProxy(
                tupleActionProcessorName=diagramTraceActionProcessorName,
                proxyToVortexName=peekServerName,
                additionalFilt=diagramTraceFilt)
