from vortex.Tuple import addTupleType, TupleField
from vortex.TupleAction import TupleActionABC

from peek_plugin_tutorial._private.PluginNames import tutorialTuplePrefix


@addTupleType
class StringCapToggleActionTuple(TupleActionABC):
    __tupleType__ = tutorialTuplePrefix + "StringCapToggleActionTuple"

    stringIntId = TupleField()
