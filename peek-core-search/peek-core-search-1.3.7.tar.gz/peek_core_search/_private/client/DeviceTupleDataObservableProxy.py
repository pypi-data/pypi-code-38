from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_core_search._private.PluginNames import searchFilt
from peek_core_search._private.PluginNames import searchObservableName
from vortex.handler.TupleDataObservableProxyHandler import TupleDataObservableProxyHandler


def makeDeviceTupleDataObservableProxy():
    return TupleDataObservableProxyHandler(observableName=searchObservableName,
                                           proxyToVortexName=peekServerName,
                                           additionalFilt=searchFilt)
