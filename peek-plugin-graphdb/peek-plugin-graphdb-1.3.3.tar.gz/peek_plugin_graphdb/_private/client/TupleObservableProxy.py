from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_graphdb._private.PluginNames import graphDbFilt
from peek_plugin_graphdb._private.PluginNames import graphDbObservableName
from vortex.handler.TupleDataObservableProxyHandler import TupleDataObservableProxyHandler


def makeDeviceTupleDataObservableProxy():
    return TupleDataObservableProxyHandler(observableName=graphDbObservableName,
                                           proxyToVortexName=peekServerName,
                                           additionalFilt=graphDbFilt)
