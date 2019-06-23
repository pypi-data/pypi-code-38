from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from vortex.Tuple import addTupleType, TupleField, Tuple


@addTupleType
class ServerStatusTuple(Tuple):
    __tupleType__ = graphDbTuplePrefix + "ServerStatusTuple"

    segmentCompilerQueueStatus: bool = TupleField(False)
    segmentCompilerQueueSize: int = TupleField(0)
    segmentCompilerQueueProcessedTotal: int = TupleField(0)
    segmentCompilerQueueLastError: str = TupleField()

    itemKeyIndexCompilerQueueStatus: bool = TupleField(False)
    itemKeyIndexCompilerQueueSize: int = TupleField(0)
    itemKeyIndexCompilerQueueProcessedTotal: int = TupleField(0)
    itemKeyIndexCompilerQueueLastError: str = TupleField()
