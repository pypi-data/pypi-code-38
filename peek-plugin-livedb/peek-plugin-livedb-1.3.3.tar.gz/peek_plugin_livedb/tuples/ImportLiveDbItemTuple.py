from peek_plugin_livedb._private.PluginNames import livedbTuplePrefix

from peek_plugin_livedb._private.storage.LiveDbItem import LiveDbItem
from vortex.Tuple import Tuple, addTupleType


@addTupleType
class ImportLiveDbItemTuple(Tuple):
    """ Live DB Display Value Tuple

    This tuple stores a value of a key in the Live DB database.

    """
    __tupleType__ = livedbTuplePrefix + 'ImportLiveDbItemTuple'
    __slots__ = ("key", "dataType", "rawValue", "displayValue", "importHash")

    DATA_TYPE_NUMBER_VALUE = LiveDbItem.NUMBER_VALUE
    DATA_TYPE_STRING_VALUE = LiveDbItem.STRING_VALUE
    DATA_TYPE_COLOR = LiveDbItem.COLOR
    DATA_TYPE_LINE_WIDTH = LiveDbItem.LINE_WIDTH
    DATA_TYPE_LINE_STYLE = LiveDbItem.LINE_STYLE
    DATA_TYPE_GROUP_PTR = LiveDbItem.GROUP_PTR
