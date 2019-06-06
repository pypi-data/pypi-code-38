import logging
from datetime import datetime

from vortex.Tuple import addTupleType, Tuple, TupleField

from peek_core_user._private.PluginNames import userPluginTuplePrefix

logger = logging.getLogger(__name__)


@addTupleType
class LoggedInUserStatusTuple(Tuple):
    """ Logged In User Status Tuple

      This tuple is used by the "Managed LoggedIn User"

      If the device receives this tuple and the deviceToken doesn't match the current
      device, then the user is logged off.

    """
    __tupleType__ = userPluginTuplePrefix + "LoggedInUserStatusTuple"

    userName: str = TupleField()

    #:  The title of the user, EG 'Chief Wiggum'
    userTitle: str = TupleField()

    #:  The vehicle the user is logged in with
    vehicle: str = TupleField()

    #:  The date that the user logged in
    loginDate: datetime = TupleField()

    #:  The device that the user is logged into From peek-core-device
    deviceToken: str = TupleField()

    #:  Is the device online now
    deviceIsOnline: bool = TupleField()

    #:  The last time the user was online
    deviceLastOnline: datetime = TupleField()

    #:  The device type
    deviceType: str = TupleField()

    #:  The device description
    deviceDescription: str = TupleField()
