from datetime import datetime

from peek_plugin_diagram._private.PluginNames import diagramTuplePrefix
from vortex.Tuple import addTupleType, TupleField, Tuple


@addTupleType
class EncodedGridTuple(Tuple):
    """ Encoded Grid Tuple

    This tuple stores a pre-encoded version of a GridTuple

    """
    __tupleType__ = diagramTuplePrefix + "EncodedGridTuple"

    gridKey: str = TupleField()

    # A GridTuple, already encoded and ready for storage in the clients cache
    encodedGridTuple: str = TupleField()

    lastUpdate: datetime = TupleField()