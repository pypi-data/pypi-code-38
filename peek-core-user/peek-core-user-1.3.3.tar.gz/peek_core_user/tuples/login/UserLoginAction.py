from typing import List

from vortex.Tuple import addTupleType, TupleField
from vortex.TupleAction import TupleActionABC

from peek_core_user._private.PluginNames import userPluginTuplePrefix


@addTupleType
class UserLoginAction(TupleActionABC):
    __tupleType__ = userPluginTuplePrefix + "UserLoginAction"
    userName: str = TupleField()
    password: str = TupleField()
    deviceToken: str = TupleField()
    vehicleId: str = TupleField()

    #: A list of accepted warning keys
    # If any server side warnings occur and they are in this list then the logon
    # continues.
    acceptedWarningKeys: List[str] = TupleField()
