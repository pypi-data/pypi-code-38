import logging
from typing import List

from peek_core_user._private.PluginNames import userPluginTuplePrefix
from vortex.Tuple import addTupleType, Tuple, TupleField

logger = logging.getLogger(__name__)


@addTupleType
class InternalGroupImportResultTuple(Tuple):
    __tupleType__ = userPluginTuplePrefix + "InternalGroupImportResultTuple"

    addedIds: List[int] = TupleField()
    updatedIds: List[int] = TupleField()
    deletedIds: List[int] = TupleField()
    sameCount: int = TupleField()
    errors: List[str] = TupleField()
