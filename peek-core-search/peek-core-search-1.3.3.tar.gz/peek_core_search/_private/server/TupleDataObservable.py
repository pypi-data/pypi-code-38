from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_core_search._private.PluginNames import searchFilt
from peek_core_search._private.PluginNames import searchObservableName
from peek_core_search._private.server.tuple_providers.AdminStatusTupleProvider import \
    AdminStatusTupleProvider
from peek_core_search._private.server.tuple_providers.SearchObjectTypeTupleProvider import \
    SearchObjectTypeTupleProvider
from peek_core_search._private.storage.SearchObjectTypeTuple import \
    SearchObjectTypeTuple
from peek_core_search._private.storage.SearchPropertyTuple import SearchPropertyTuple
from peek_core_search._private.tuples.AdminStatusTuple import AdminStatusTuple
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler
from .controller.StatusController import StatusController
from .tuple_providers.SearchPropertyTupleProvider import SearchPropertyTupleProvider


def makeTupleDataObservableHandler(dbSessionCreator: DbSessionCreator,
                                   statusController: StatusController):
    """" Make Tuple Data Observable Handler

    This method creates the observable object, registers the tuple providers and then
    returns it.

    :param statusController: The search status controller.
    :param dbSessionCreator: A function that returns a SQLAlchemy session when called

    :return: An instance of :code:`TupleDataObservableHandler`

    """
    tupleObservable = TupleDataObservableHandler(
        observableName=searchObservableName,
        additionalFilt=searchFilt)

    # Search Property
    tupleObservable.addTupleProvider(SearchPropertyTuple.tupleName(),
                                     SearchPropertyTupleProvider(dbSessionCreator))

    # Search Object Type
    tupleObservable.addTupleProvider(SearchObjectTypeTuple.tupleName(),
                                     SearchObjectTypeTupleProvider(dbSessionCreator))

    # Admin status tuple
    tupleObservable.addTupleProvider(AdminStatusTuple.tupleName(),
                                     AdminStatusTupleProvider(statusController))

    return tupleObservable
