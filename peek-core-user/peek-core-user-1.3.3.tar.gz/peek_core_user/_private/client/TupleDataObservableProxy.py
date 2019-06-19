from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_core_user._private.PluginNames import userPluginFilt, \
    userPluginObservableName
from vortex.handler.TupleDataObservableProxyHandler import TupleDataObservableProxyHandler


def makeTupleDataObservableProxy():
    return TupleDataObservableProxyHandler(observableName=userPluginObservableName,
                                           proxyToVortexName=peekServerName,
                                           additionalFilt=userPluginFilt)

