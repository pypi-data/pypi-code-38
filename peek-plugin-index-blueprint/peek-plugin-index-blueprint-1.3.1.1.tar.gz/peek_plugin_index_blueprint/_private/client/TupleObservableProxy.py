from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_index_blueprint._private.PluginNames import indexBlueprintFilt
from peek_plugin_index_blueprint._private.PluginNames import indexBlueprintObservableName
from vortex.handler.TupleDataObservableProxyHandler import TupleDataObservableProxyHandler


def makeTupleObservableProxy():
    return TupleDataObservableProxyHandler(observableName=indexBlueprintObservableName,
                                           proxyToVortexName=peekServerName,
                                           additionalFilt=indexBlueprintFilt)
