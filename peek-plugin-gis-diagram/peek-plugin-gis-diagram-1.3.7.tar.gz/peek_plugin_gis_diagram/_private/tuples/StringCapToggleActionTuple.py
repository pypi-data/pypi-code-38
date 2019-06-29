from vortex.Tuple import addTupleType, TupleField
from vortex.TupleAction import TupleActionABC

from peek_plugin_gis_diagram._private.PluginNames import gisDiagramTuplePrefix


@addTupleType
class StringCapToggleActionTuple(TupleActionABC):
    __tupleType__ = gisDiagramTuplePrefix + "StringCapToggleActionTuple"

    stringIntId = TupleField()
