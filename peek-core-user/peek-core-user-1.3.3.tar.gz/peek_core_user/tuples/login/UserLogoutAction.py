from typing import List

from vortex.TupleAction import TupleActionABC

from peek_core_user._private.PluginNames import userPluginTuplePrefix
from vortex.Tuple import addTupleType, Tuple, TupleField


@addTupleType
class UserLogoutAction(TupleActionABC):
    __tupleType__ = userPluginTuplePrefix + "UserLogoutAction"
    userName: str = TupleField()
    deviceToken: str = TupleField()

    #: A list of accepted warning keys
    # If any server side warnings occur and they are in this list then the logoff
    # continues.
    acceptedWarningKeys: List[str] = TupleField()
