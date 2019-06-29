from vortex.Tuple import addTupleType, TupleField
from vortex.TupleAction import TupleActionABC

from peek_core_device._private.PluginNames import deviceTuplePrefix


@addTupleType
class UpdateDeviceOnlineAction(TupleActionABC):
    __tupleType__ = deviceTuplePrefix + "UpdateDeviceOnlineAction"

    deviceId: str = TupleField()
    isOnline: bool = TupleField()