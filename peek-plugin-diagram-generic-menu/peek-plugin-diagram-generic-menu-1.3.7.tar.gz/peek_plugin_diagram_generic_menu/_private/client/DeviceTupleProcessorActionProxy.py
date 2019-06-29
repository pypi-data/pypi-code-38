from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_diagram_generic_menu._private.PluginNames import diagramGenericMenuFilt
from peek_plugin_diagram_generic_menu._private.PluginNames import diagramGenericMenuActionProcessorName
from vortex.handler.TupleActionProcessorProxy import TupleActionProcessorProxy


def makeTupleActionProcessorProxy():
    return TupleActionProcessorProxy(
                tupleActionProcessorName=diagramGenericMenuActionProcessorName,
                proxyToVortexName=peekServerName,
                additionalFilt=diagramGenericMenuFilt)
