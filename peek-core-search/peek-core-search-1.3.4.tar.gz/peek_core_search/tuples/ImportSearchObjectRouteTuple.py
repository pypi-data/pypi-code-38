from peek_core_search._private.PluginNames import searchTuplePrefix
from vortex.Tuple import Tuple, addTupleType, TupleField


@addTupleType
class ImportSearchObjectRouteTuple(Tuple):
    """ Import Search Object Route

    This tuple is used to import object routes into the search plugin

    """
    __tupleType__ = searchTuplePrefix + 'ImportSearchObjectRouteTuple'

    #:  A unique string describing this group being imported
    # This can be used for deleting as well
    importGroupHash: str = TupleField()

    #:  The title of the route, that the user will see
    routeTitle: str = TupleField()

    #:  The route that the angular app will route to
    routePath: str = TupleField()
