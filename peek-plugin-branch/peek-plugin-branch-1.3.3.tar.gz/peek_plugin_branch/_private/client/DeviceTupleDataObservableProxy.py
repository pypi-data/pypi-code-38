from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_branch._private.PluginNames import branchFilt
from peek_plugin_branch._private.PluginNames import branchObservableName
from vortex.handler.TupleDataObservableProxyHandler import TupleDataObservableProxyHandler


def makeDeviceTupleDataObservableProxy():
    return TupleDataObservableProxyHandler(observableName=branchObservableName,
                                           proxyToVortexName=peekServerName,
                                           additionalFilt=branchFilt)
