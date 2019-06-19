from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_gis_diagram._private.PluginNames import gisDiagramFilt
from peek_plugin_gis_diagram._private.PluginNames import gisDiagramObservableName
from vortex.handler.TupleDataObservableProxyHandler import TupleDataObservableProxyHandler


def makeDeviceTupleDataObservableProxy():
    return TupleDataObservableProxyHandler(observableName=gisDiagramObservableName,
                                           proxyToVortexName=peekServerName,
                                           additionalFilt=gisDiagramFilt)
