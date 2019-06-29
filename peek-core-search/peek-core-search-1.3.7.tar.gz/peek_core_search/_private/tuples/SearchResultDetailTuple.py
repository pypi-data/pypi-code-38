from peek_core_search._private.PluginNames import searchTuplePrefix
from vortex.Tuple import Tuple, addTupleType, TupleField


@addTupleType
class SearchResultDetailTuple(Tuple):
    """ Search Result Detail Tuple

    This tuple represents the details of a search result.
    """
    __tupleType__ = searchTuplePrefix + 'SearchResultDetailTuple'

    #:  The name of the detail
    name: str = TupleField()

    #:  The value of the detail
    value: str = TupleField()
