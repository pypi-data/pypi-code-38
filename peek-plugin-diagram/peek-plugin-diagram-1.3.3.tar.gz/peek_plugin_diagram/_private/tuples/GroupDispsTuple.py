from typing import List, Any

from vortex.Tuple import addTupleType, TupleField, Tuple

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix


@addTupleType
class GroupDispsTuple(Tuple):
    """ Group Disps Tuple

    This tuple stores a list of DispGroups that are in the 'ID:dispgroup' grid key
    in that coord set.

    """
    __tupleType__ = diagramTuplePrefix + "GroupDispsTuple"

    coordSetId: int = TupleField()

    # A GridTuple, already encoded and ready for storage in the clients cache
    encodedGridTuple: str = TupleField()
