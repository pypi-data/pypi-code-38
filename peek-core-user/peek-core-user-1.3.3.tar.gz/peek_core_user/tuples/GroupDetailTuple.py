from peek_core_user._private.PluginNames import userPluginTuplePrefix
from vortex.Tuple import addTupleType, Tuple, TupleField


@addTupleType
class GroupDetailTuple(Tuple):
    __tupleType__ = userPluginTuplePrefix + "GroupDetailTuple"

    #:  ID
    id: int = TupleField()

    #:  The name of the group, EG C917
    groupName: str = TupleField()

    #:  The title of the group, EG 'Chief Wiggum'
    groupTitle: str = TupleField()
