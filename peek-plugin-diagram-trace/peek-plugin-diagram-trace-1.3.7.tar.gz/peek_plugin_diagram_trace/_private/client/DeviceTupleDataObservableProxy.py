from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_diagram_trace._private.PluginNames import diagramTraceFilt
from peek_plugin_diagram_trace._private.PluginNames import diagramTraceObservableName
from vortex.handler.TupleDataObservableProxyHandler import TupleDataObservableProxyHandler


def makeDeviceTupleDataObservableProxy():
    return TupleDataObservableProxyHandler(observableName=diagramTraceObservableName,
                                           proxyToVortexName=peekServerName,
                                           additionalFilt=diagramTraceFilt)
