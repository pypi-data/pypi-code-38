from vortex.Tuple import addTupleType, TupleField
from vortex.TupleAction import TupleActionABC

from peek_core_device._private.PluginNames import deviceTuplePrefix


@addTupleType
class EnrolDeviceAction(TupleActionABC):
    __tupleType__ = deviceTuplePrefix + "EnrolDeviceAction"

    description:str = TupleField()
    deviceId: str = TupleField()
    deviceType: str = TupleField()
    appVersion: str = TupleField()