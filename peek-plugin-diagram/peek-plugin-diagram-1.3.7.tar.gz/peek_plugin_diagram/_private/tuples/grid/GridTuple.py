from datetime import datetime

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from vortex.Tuple import addTupleType, TupleField, Tuple


@addTupleType
class GridTuple(Tuple):
    __tupleType__ = diagramTuplePrefix + "GridTuple"

    gridKey: str = TupleField()
    dispJsonStr: str = TupleField()
    lastUpdate: datetime = TupleField()