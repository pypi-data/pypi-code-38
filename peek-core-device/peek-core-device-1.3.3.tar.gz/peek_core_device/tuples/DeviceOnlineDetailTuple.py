from peek_core_device._private.PluginNames import deviceTuplePrefix
from vortex.Tuple import addTupleType, Tuple, TupleField


@addTupleType
class DeviceOnlineDetailTuple(Tuple):
    __tupleType__ = deviceTuplePrefix + "DeviceOnlineDetailTuple"

    deviceId: str = TupleField()
    deviceToken: str = TupleField()
    onlineStatus: bool = TupleField()
