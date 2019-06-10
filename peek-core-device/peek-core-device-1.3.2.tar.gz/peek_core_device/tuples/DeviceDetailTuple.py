from peek_core_device._private.PluginNames import deviceTuplePrefix
from vortex.Tuple import addTupleType, Tuple, TupleField


@addTupleType
class DeviceDetailTuple(Tuple):
    __tupleType__ = deviceTuplePrefix + "DeviceDetailTuple"

    deviceToken: str = TupleField()
    deviceType: str = TupleField()
    description: str = TupleField()
    lastOnline: str = TupleField()
    isOnline: bool = TupleField()
