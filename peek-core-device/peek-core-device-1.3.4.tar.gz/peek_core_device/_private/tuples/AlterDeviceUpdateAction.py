from typing import Optional

from peek_core_device._private.PluginNames import deviceTuplePrefix
from vortex.Tuple import addTupleType, TupleField
from vortex.TupleAction import TupleActionABC


# I'm using the word Alter here, because UpdateUpdate is confusing.
@addTupleType
class AlterDeviceUpdateAction(TupleActionABC):
    """ Alter Device Update Tuple

    This action tuple applies changes to the Update from the admin UI.

    """
    __tupleType__ = deviceTuplePrefix + 'AlterDeviceUpdateAction'

    #:  the ID of the DeviceUpdateTuple
    updateId: int = TupleField()

    #: Set the enabled property of the update
    isEnabled: Optional[bool] = TupleField()

    #: Delete the update from the database
    remove: bool = TupleField(False)