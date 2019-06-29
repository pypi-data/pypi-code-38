import logging

from vortex.Tuple import addTupleType, Tuple, TupleField

from peek_core_user._private.PluginNames import userPluginTuplePrefix

logger = logging.getLogger(__name__)


@addTupleType
class UserLoginUiSettingTuple(Tuple):
    """ User Login UI Setting

      This tuple is sent to the devices to control the appearance of the UI

    """
    __tupleType__ = userPluginTuplePrefix + "UserLoginUiSettingTuple"

    showUsersAsList: bool = TupleField()
    showVehicleInput: bool = TupleField()
