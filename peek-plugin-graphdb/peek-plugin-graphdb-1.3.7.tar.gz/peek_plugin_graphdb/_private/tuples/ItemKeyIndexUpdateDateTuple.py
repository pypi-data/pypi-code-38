from typing import Dict

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from vortex.Tuple import addTupleType, TupleField, Tuple


@addTupleType
class ItemKeyIndexUpdateDateTuple(Tuple):
    """ ItemKeyIndex Object Update Date Tuple

    This tuple represents the state of the chunks in the cache.
    Each chunkKey has a lastUpdateDate as a string, this is used for offline caching
    all the chunks.
    """
    __tupleType__ = graphDbTuplePrefix + "ItemKeyIndexUpdateDateTuple"

    # Improve performance of the JSON serialisation
    __rawJonableFields__ = ('initialLoadComplete', 'updateDateByChunkKey')

    initialLoadComplete: bool = TupleField()
    updateDateByChunkKey: Dict[str, str] = TupleField({})
