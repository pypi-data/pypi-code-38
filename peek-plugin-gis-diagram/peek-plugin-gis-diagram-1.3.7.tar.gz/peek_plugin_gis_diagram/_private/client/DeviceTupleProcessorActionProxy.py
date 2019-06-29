from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_gis_diagram._private.PluginNames import gisDiagramFilt
from peek_plugin_gis_diagram._private.PluginNames import gisDiagramActionProcessorName
from vortex.handler.TupleActionProcessorProxy import TupleActionProcessorProxy


def makeTupleActionProcessorProxy():
    return TupleActionProcessorProxy(
                tupleActionProcessorName=gisDiagramActionProcessorName,
                proxyToVortexName=peekServerName,
                additionalFilt=gisDiagramFilt)
