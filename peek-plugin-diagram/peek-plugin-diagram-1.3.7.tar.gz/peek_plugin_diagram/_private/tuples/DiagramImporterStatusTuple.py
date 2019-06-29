from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from vortex.Tuple import addTupleType, TupleField, Tuple


@addTupleType
class DiagramImporterStatusTuple(Tuple):
    __tupleType__ = diagramTuplePrefix + "DiagramImporterStatusTuple"

    displayCompilerQueueStatus: bool = TupleField(False)
    displayCompilerQueueSize: int = TupleField(0)
    displayCompilerProcessedTotal: int = TupleField(0)
    displayCompilerLastError: str = TupleField()

    gridCompilerQueueStatus: bool = TupleField(False)
    gridCompilerQueueSize: int = TupleField(0)
    gridCompilerProcessedTotal: int = TupleField(0)
    gridCompilerLastError: str = TupleField()

    locationIndexCompilerQueueStatus: bool = TupleField(False)
    locationIndexCompilerQueueSize: int = TupleField(0)
    locationIndexCompilerProcessedTotal: int = TupleField(0)
    locationIndexCompilerLastError: str = TupleField()

    branchIndexCompilerQueueStatus: bool = TupleField(False)
    branchIndexCompilerQueueSize: int = TupleField(0)
    branchIndexCompilerProcessedTotal: int = TupleField(0)
    branchIndexCompilerLastError: str = TupleField()
