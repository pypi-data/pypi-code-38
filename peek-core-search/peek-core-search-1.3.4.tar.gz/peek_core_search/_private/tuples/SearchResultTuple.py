from typing import List

from vortex.Tuple import Tuple, addTupleType, TupleField

from peek_core_search._private.PluginNames import searchTuplePrefix
from .SearchResultDetailTuple import SearchResultDetailTuple


@addTupleType
class SearchResultTuple(Tuple):
    """ Search Result Tuple

    This tuple represents a search result
    """
    __tupleType__ = searchTuplePrefix + 'SearchResultTuple'

    #:  The id of the object this search result is for
    objectId: str = TupleField()

    #:  The type of this object in the search result
    objectType: str = TupleField()

    #:  The details of the search result
    details: List[SearchResultDetailTuple] = TupleField(defaultValue=[])
