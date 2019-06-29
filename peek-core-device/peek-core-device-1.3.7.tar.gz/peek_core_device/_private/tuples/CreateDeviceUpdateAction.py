from peek_core_device._private.storage.DeviceUpdateTuple import DeviceUpdateTuple
from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_core_device._private.PluginNames import deviceTuplePrefix
from vortex.TupleAction import TupleActionABC


@addTupleType
class CreateDeviceUpdateAction(TupleActionABC):
    """ Create Update Action

    Create a new device update entry, this will be accompanied by an upload.

    """
    __tupleType__ = deviceTuplePrefix + 'CreateDeviceUpdateAction'

    #:  Description of date1
    newUpdate:DeviceUpdateTuple = TupleField()