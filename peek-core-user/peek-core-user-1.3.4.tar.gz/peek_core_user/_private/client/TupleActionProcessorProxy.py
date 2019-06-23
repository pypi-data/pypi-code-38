from vortex.handler.TupleActionProcessorProxy import TupleActionProcessorProxy

from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_core_user._private.PluginNames import userPluginFilt, \
    userPluginActionProcessorName


def makeTupleActionProcessorProxy():
    return TupleActionProcessorProxy(
        tupleActionProcessorName=userPluginActionProcessorName,
        proxyToVortexName=peekServerName,
        additionalFilt=userPluginFilt)
