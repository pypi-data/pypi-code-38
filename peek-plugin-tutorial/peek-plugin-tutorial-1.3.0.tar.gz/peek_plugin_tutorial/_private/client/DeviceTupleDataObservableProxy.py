from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_tutorial._private.PluginNames import tutorialFilt
from peek_plugin_tutorial._private.PluginNames import tutorialObservableName
from vortex.handler.TupleDataObservableProxyHandler import TupleDataObservableProxyHandler


def makeDeviceTupleDataObservableProxy():
    return TupleDataObservableProxyHandler(observableName=tutorialObservableName,
                                           proxyToVortexName=peekServerName,
                                           additionalFilt=tutorialFilt)
