from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_tutorial._private.PluginNames import tutorialFilt
from peek_plugin_tutorial._private.PluginNames import tutorialActionProcessorName
from vortex.handler.TupleActionProcessorProxy import TupleActionProcessorProxy


def makeTupleActionProcessorProxy():
    return TupleActionProcessorProxy(
                tupleActionProcessorName=tutorialActionProcessorName,
                proxyToVortexName=peekServerName,
                additionalFilt=tutorialFilt)
