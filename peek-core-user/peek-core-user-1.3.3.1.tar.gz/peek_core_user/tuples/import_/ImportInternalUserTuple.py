import logging
from typing import List, Optional

from peek_core_user._private.PluginNames import userPluginTuplePrefix
from vortex.Tuple import addTupleType, Tuple, TupleField

logger = logging.getLogger(__name__)


@addTupleType
class ImportInternalUserTuple(Tuple):
    __tupleType__ = userPluginTuplePrefix + "ImportInternalUserTuple"

    #: The unique name of the user
    userName: str = TupleField()

    #: The unique uuid of the user
    userUuid: str = TupleField()

    #: The nice name of the user
    userTitle: str = TupleField()

    #: The password for the user, null if it's managed in the peek_user_plugin
    password: Optional[str] = TupleField()

    #: Group Keys
    groupKeys: Optional[List[str]] = TupleField()

    #: The mobile phone number of the user
    mobile: Optional[str] = TupleField()

    #: The email address of the user
    email: Optional[str] = TupleField()
