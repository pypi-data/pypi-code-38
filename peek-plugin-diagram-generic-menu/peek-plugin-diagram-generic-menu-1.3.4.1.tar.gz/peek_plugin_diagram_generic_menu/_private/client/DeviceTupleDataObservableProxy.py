from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_diagram_generic_menu._private.PluginNames import diagramGenericMenuFilt
from peek_plugin_diagram_generic_menu._private.PluginNames import diagramGenericMenuObservableName
from vortex.handler.TupleDataObservableProxyHandler import TupleDataObservableProxyHandler


def makeDeviceTupleDataObservableProxy():
    return TupleDataObservableProxyHandler(observableName=diagramGenericMenuObservableName,
                                           proxyToVortexName=peekServerName,
                                           additionalFilt=diagramGenericMenuFilt)
