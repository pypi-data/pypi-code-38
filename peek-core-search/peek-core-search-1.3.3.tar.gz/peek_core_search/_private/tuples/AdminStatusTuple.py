from peek_core_search._private.PluginNames import searchTuplePrefix
from vortex.Tuple import addTupleType, TupleField, Tuple


@addTupleType
class AdminStatusTuple(Tuple):
    __tupleType__ = searchTuplePrefix + "AdminStatusTuple"

    searchIndexCompilerQueueStatus: bool = TupleField(False)
    searchIndexCompilerQueueSize: int = TupleField(0)
    searchIndexCompilerQueueProcessedTotal: int = TupleField(0)
    searchIndexCompilerQueueLastError: str = TupleField()


    searchObjectCompilerQueueStatus: bool = TupleField(False)
    searchObjectCompilerQueueSize: int = TupleField(0)
    searchObjectCompilerQueueProcessedTotal: int = TupleField(0)
    searchObjectCompilerQueueLastError: str = TupleField()
