from peek_plugin_livedb._private.PluginNames import livedbTuplePrefix

from vortex.Tuple import Tuple, addTupleType


@addTupleType
class LiveDbDisplayValueUpdateTuple(Tuple):
    """ Live DB Display Value Update

    This tuple represents an update to the display value for a live db item

    """
    __tupleType__ = livedbTuplePrefix + 'LiveDbDisplayValueUpdateTuple'
    __slots__ = ("key", "displayValue")
