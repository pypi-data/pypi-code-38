from peek_plugin_index_blueprint._private.PluginNames import indexBlueprintTuplePrefix
from vortex.Tuple import addTupleType, TupleField, Tuple


@addTupleType
class ThingIndexServerStatusTuple(Tuple):
    __tupleType__ = indexBlueprintTuplePrefix + "ThingIndexServerStatusTuple"

    thingIndexCompilerQueueStatus: bool = TupleField(False)
    thingIndexCompilerQueueSize: int = TupleField(0)
    thingIndexCompilerQueueProcessedTotal: int = TupleField(0)
    thingIndexCompilerQueueLastError: str = TupleField()
