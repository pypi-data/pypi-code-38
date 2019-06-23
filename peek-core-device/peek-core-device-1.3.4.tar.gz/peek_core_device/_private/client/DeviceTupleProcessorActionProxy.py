from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_core_device._private.PluginNames import deviceFilt
from peek_core_device._private.PluginNames import deviceActionProcessorName
from vortex.handler.TupleActionProcessorProxy import TupleActionProcessorProxy


def makeTupleActionProcessorProxy():
    return TupleActionProcessorProxy(
                tupleActionProcessorName=deviceActionProcessorName,
                proxyToVortexName=peekServerName,
                additionalFilt=deviceFilt)
