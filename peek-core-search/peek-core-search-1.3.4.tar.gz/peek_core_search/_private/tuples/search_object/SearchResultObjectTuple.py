from typing import List, Dict

from peek_core_search._private.PluginNames import searchTuplePrefix
from peek_core_search._private.storage.SearchObjectTypeTuple import \
    SearchObjectTypeTuple
from peek_core_search.tuples.ImportSearchObjectRouteTuple import \
    ImportSearchObjectRouteTuple
from vortex.Tuple import Tuple, addTupleType, TupleField


@addTupleType
class SearchResultObjectTuple(Tuple):
    """ Import Search Object

    This tuple is used by other plugins to load objects into the search index.

    """
    __tupleType__ = searchTuplePrefix + 'SearchResultObjectTuple'

    # The id of the object this search result is for
    id: int = TupleField()

    #:  The unique key for this object
    key: str = TupleField()

    #:  The type of this object
    objectType: SearchObjectTypeTuple = TupleField()

    #:  The details to index.
    # Do not include "key", it will be indexed anyway.
    # The key of the property will match of create a new "SearchProperty"
    properties: Dict[str, str] = TupleField({})

    #:  The color
    routes: List[ImportSearchObjectRouteTuple] = TupleField([])
