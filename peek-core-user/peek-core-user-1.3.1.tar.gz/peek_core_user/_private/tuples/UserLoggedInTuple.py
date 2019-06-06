import logging
from typing import List

from peek_core_user._private.PluginNames import userPluginTuplePrefix
from vortex.Tuple import addTupleType, Tuple, TupleField

logger = logging.getLogger(__name__)


@addTupleType
class UserLoggedInTuple(Tuple):
    """ User Logged In Tuple

      This tuple is sent to the devices when a user logs in.

      If the device receives this tuple and the deviceToken doesn't match the current
      device, then the user is logged off.

    """
    __tupleType__ = userPluginTuplePrefix + "UserLoggedInTuple"

    userName: str = TupleField()
    deviceToken: str = TupleField()

