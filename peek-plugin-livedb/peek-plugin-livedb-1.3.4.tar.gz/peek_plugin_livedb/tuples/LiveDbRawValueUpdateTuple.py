from peek_plugin_livedb._private.PluginNames import livedbTuplePrefix

from vortex.Tuple import Tuple, addTupleType


@addTupleType
class LiveDbRawValueUpdateTuple(Tuple):
    """ Live DB Raw Value Update

    This tuple represents an update to the raw value for a live db item

    """
    __tupleType__ = livedbTuplePrefix + 'LiveDbRawValueUpdateTuple'
    __slots__ = ("key", "rawValue")
