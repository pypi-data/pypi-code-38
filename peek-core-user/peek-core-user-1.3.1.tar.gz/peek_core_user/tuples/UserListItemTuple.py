import logging

from peek_core_user._private.PluginNames import userPluginTuplePrefix
from vortex.Tuple import addTupleType, Tuple, TupleField

logger = logging.getLogger(__name__)


@addTupleType
class UserListItemTuple(Tuple):
    __tupleType__ = userPluginTuplePrefix + "UserListItemTuple"

    #:  The unique ID of the user
    userId: str = TupleField()

    #:  The nice name of the user
    displayName: str = TupleField()

    @property
    def userName(self) -> str:
        return self.userId

    @property
    def userTitle(self) -> str:
        return self.displayName
