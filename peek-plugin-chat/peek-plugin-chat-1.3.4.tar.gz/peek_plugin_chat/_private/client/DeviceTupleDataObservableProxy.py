from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_chat._private.PluginNames import chatFilt
from peek_plugin_chat._private.PluginNames import chatObservableName
from vortex.handler.TupleDataObservableProxyHandler import TupleDataObservableProxyHandler


def makeDeviceTupleDataObservableProxy():
    return TupleDataObservableProxyHandler(observableName=chatObservableName,
                                           proxyToVortexName=peekServerName,
                                           additionalFilt=chatFilt)