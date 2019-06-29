from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_inbox._private.PluginNames import inboxFilt, \
    inboxObservableName
from vortex.handler.TupleDataObservableProxyHandler import TupleDataObservableProxyHandler


def makeTupleDataObservableProxy():
    return TupleDataObservableProxyHandler(observableName=inboxObservableName,
                                           proxyToVortexName=peekServerName,
                                           additionalFilt=inboxFilt)

