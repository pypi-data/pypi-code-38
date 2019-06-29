from peek_plugin_livedb._private.PluginNames import livedbTuplePrefix

from vortex.Tuple import Tuple, addTupleType


@addTupleType
class LiveDbRawValueTuple(Tuple):
    """ Live DB Raw Value Tuple

    This tuple represents a raw key / value pair in the Live Db

    """
    __tupleType__ = livedbTuplePrefix + 'LiveDbRawValueTuple'
    __slots__ = ("id", "key", "rawValue")

    def __init__(self, id=None, key=None, rawValue=None):
        # DON'T CALL SUPER INIT
        self.id = id
        self.key = key
        self.rawValue = rawValue
