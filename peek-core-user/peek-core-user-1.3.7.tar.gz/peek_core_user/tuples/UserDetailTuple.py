from typing import Optional, List, Dict

from peek_core_user._private.PluginNames import userPluginTuplePrefix
from vortex.Tuple import addTupleType, Tuple, TupleField


@addTupleType
class UserDetailTuple(Tuple):
    __tupleType__ = userPluginTuplePrefix + "UserDetailTuple"

    #:  The username / userid of the user, EG C917
    userName: str = TupleField()

    #:  The title of the user, EG 'Chief Wiggum'
    userTitle: str = TupleField()

    #:  An external system user uuid, EG 715903a7ebc14fb0afb00d432676c51c
    userUuid: Optional[str] = TupleField()

    #:  The mobile number, EG +61 419 123 456
    mobile: Optional[str] = TupleField()

    #:  The email address, EG guy@place.com
    email: Optional[str] = TupleField()

    #:  A list of group names that this user belongs to
    groupNames: List[str] = TupleField()

    #: A field for additional data
    data: Optional[Dict] = TupleField()
