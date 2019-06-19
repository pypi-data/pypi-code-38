from datetime import datetime
from typing import Dict

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from vortex.Tuple import addTupleType, TupleField, Tuple


@addTupleType
class GridUpdateDateTuple(Tuple):
    __tupleType__ = diagramTuplePrefix + "GridUpdateDateTuple"

    # Improve performance of the JSON serialisation
    __rawJonableFields__ = ( 'updateDateByChunkKey',)

    updateDateByChunkKey: Dict[str, str] = TupleField()