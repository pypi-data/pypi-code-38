from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_docdb._private.PluginNames import docDbFilt
from peek_plugin_docdb._private.PluginNames import docDbObservableName
from vortex.handler.TupleDataObservableProxyHandler import TupleDataObservableProxyHandler


def makeDeviceTupleDataObservableProxy():
    return TupleDataObservableProxyHandler(observableName=docDbObservableName,
                                           proxyToVortexName=peekServerName,
                                           additionalFilt=docDbFilt)
