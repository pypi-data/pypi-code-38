from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_docdb._private.PluginNames import docDbFilt
from peek_plugin_docdb._private.PluginNames import docDbActionProcessorName
from vortex.handler.TupleActionProcessorProxy import TupleActionProcessorProxy


def makeTupleActionProcessorProxy():
    return TupleActionProcessorProxy(
                tupleActionProcessorName=docDbActionProcessorName,
                proxyToVortexName=peekServerName,
                additionalFilt=docDbFilt)
