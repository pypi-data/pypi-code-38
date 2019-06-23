from peek_core_search._private.PluginNames import searchTuplePrefix
from vortex.Tuple import Tuple, addTupleType, TupleField


@addTupleType
class SearchResultObjectRouteTuple(Tuple):
    """ Import Search Object Route

    This tuple is used to import object routes into the search plugin

    """
    __tupleType__ = searchTuplePrefix + 'SearchResultObjectRouteTuple'

    #:  The title of the route, that the user will see
    title: str = TupleField()

    #:  The route that the angular app will route to
    path: str = TupleField()
