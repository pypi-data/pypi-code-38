from peek_core_device._private.PluginNames import deviceTuplePrefix
from vortex.Tuple import addTupleType, TupleField
from vortex.TupleAction import TupleActionABC


@addTupleType
class UpdateEnrollmentAction(TupleActionABC):
    """ Authorise Enrolment Action

    This action authorises a device to enroll in this peek environment.

    """
    __tupleType__ = deviceTuplePrefix + 'UpdateEnrollmentAction'

    #:  The device info id to authorise
    deviceInfoId: int = TupleField()
    unenroll:bool = TupleField(False)
    remove:bool = TupleField(False)
