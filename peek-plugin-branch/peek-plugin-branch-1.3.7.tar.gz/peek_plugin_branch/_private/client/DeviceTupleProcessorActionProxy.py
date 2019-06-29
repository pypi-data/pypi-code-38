from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_branch._private.PluginNames import branchFilt
from peek_plugin_branch._private.PluginNames import branchActionProcessorName
from vortex.handler.TupleActionProcessorProxy import TupleActionProcessorProxy


def makeTupleActionProcessorProxy():
    return TupleActionProcessorProxy(
                tupleActionProcessorName=branchActionProcessorName,
                proxyToVortexName=peekServerName,
                additionalFilt=branchFilt)
