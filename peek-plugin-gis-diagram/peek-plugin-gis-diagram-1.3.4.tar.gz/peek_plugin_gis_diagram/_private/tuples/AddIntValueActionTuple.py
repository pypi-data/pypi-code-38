from vortex.Tuple import addTupleType, TupleField
from vortex.TupleAction import TupleActionABC

from peek_plugin_gis_diagram._private.PluginNames import gisDiagramTuplePrefix


@addTupleType
class AddIntValueActionTuple(TupleActionABC):
    __tupleType__ = gisDiagramTuplePrefix + "AddIntValueActionTuple"

    stringIntId = TupleField()
    offset = TupleField()
