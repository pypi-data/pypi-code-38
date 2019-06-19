from peek_plugin_docdb._private.PluginNames import docDbTuplePrefix
from vortex.Tuple import addTupleType, TupleField, Tuple


@addTupleType
class AdminStatusTuple(Tuple):
    __tupleType__ = docDbTuplePrefix + "AdminStatusTuple"

    documentCompilerQueueStatus: bool = TupleField(False)
    documentCompilerQueueSize: int = TupleField(0)
    documentCompilerQueueProcessedTotal: int = TupleField(0)
    documentCompilerQueueLastError: str = TupleField()
