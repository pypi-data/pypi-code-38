import logging

from peek_core_user._private.PluginNames import userPluginTuplePrefix
from vortex.Tuple import addTupleType, Tuple, TupleField

logger = logging.getLogger(__name__)


@addTupleType
class ImportInternalGroupTuple(Tuple):
    __tupleType__ = userPluginTuplePrefix + "ImportInternalGroupTuple"

    #: The unique name of this group
    groupName: str = TupleField()

    #: The nice name of this group
    groupTitle: str = TupleField()
