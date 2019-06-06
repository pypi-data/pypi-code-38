from peek_core_device._private.client.tuple_providers.WebClientVortexDetailsTupleProvider import \
    WebClientVortexDetailsTupleProvider
from peek_core_device._private.tuples.WebClientVortexDetailsTuple import \
    WebClientVortexDetailsTuple
from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_core_device._private.PluginNames import deviceFilt
from peek_core_device._private.PluginNames import deviceObservableName
from vortex.handler.TupleDataObservableProxyHandler import TupleDataObservableProxyHandler


def makeDeviceTupleDataObservableProxy():

    proxy =  TupleDataObservableProxyHandler(observableName=deviceObservableName,
                                           proxyToVortexName=peekServerName,
                                           additionalFilt=deviceFilt)

    proxy.addTupleProvider(WebClientVortexDetailsTuple.tupleType(),
                           WebClientVortexDetailsTupleProvider())

    return proxy
