from typing import Dict, List

from peek_core_user._private.PluginNames import userPluginTuplePrefix
from vortex.Tuple import addTupleType, Tuple, TupleField


@addTupleType
class UserLogoutResponseTuple(Tuple):
    __tupleType__ = userPluginTuplePrefix + "UserLogoutResponseTuple"
    userName: str = TupleField()
    deviceToken: str = TupleField()
    deviceDescription: str = TupleField()

    succeeded: bool = TupleField(True)

    #: A list of accepted warning keys
    # If any server side warnings occur and they are in this list then the logoff
    # continues.
    acceptedWarningKeys: List[str] = TupleField()

    #: A dict of warnings from a failed logoff action.
    # key = a unique key for this warning
    # value = the description of the warning for the user
    warnings: Dict[str, str] = TupleField({})

    def setFailed(self) -> None:
        self.succeeded = False

    def addWarning(self, key: str, displayText: str) -> None:
        self.warnings[key] = displayText
