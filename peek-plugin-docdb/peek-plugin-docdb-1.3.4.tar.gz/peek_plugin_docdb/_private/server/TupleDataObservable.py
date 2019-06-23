from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_docdb._private.PluginNames import docDbFilt
from peek_plugin_docdb._private.PluginNames import docDbObservableName
from peek_plugin_docdb._private.server.tuple_providers.DocumentPropertyTupleProvider import \
    DocumentPropertyTupleProvider
from peek_plugin_docdb._private.server.tuple_providers.DocumentTypeTupleProvider import \
    DocumentTypeTupleProvider
from peek_plugin_docdb._private.server.tuple_providers.ModelSetTupleProvider import \
    ModelSetTupleProvider
from peek_plugin_docdb._private.storage.DocDbDocument import DocDbDocument
from peek_plugin_docdb._private.storage.DocDbDocumentTypeTuple import \
    DocDbDocumentTypeTuple
from peek_plugin_docdb._private.storage.DocDbModelSet import DocDbModelSet
from peek_plugin_docdb._private.storage.DocDbPropertyTuple import DocDbPropertyTuple
from peek_plugin_docdb._private.tuples.AdminStatusTuple import AdminStatusTuple
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler
from .controller.StatusController import StatusController
from .tuple_providers.AdminStatusTupleProvider import AdminStatusTupleProvider
from .tuple_providers.DocumentTupleProvider import DocumentTupleProvider


def makeTupleDataObservableHandler(dbSessionCreator: DbSessionCreator,
                                   statusController: StatusController):
    """" Make Tuple Data Observable Handler

    This method creates the observable object, registers the tuple providers and then
    returns it.

    :param dbSessionCreator: A function that returns a SQLAlchemy session when called
    :param statusController:

    :return: An instance of :code:`TupleDataObservableHandler`

    """
    tupleObservable = TupleDataObservableHandler(
        observableName=docDbObservableName,
        additionalFilt=docDbFilt)

    # Register TupleProviders here
    tupleObservable.addTupleProvider(DocDbDocument.tupleName(),
                                     DocumentTupleProvider(dbSessionCreator))

    # Admin status tuple
    tupleObservable.addTupleProvider(AdminStatusTuple.tupleName(),
                                     AdminStatusTupleProvider(statusController))

    # Document Type Tuple
    tupleObservable.addTupleProvider(DocDbDocumentTypeTuple.tupleName(),
                                     DocumentTypeTupleProvider(dbSessionCreator))

    # Document Property Tuple
    tupleObservable.addTupleProvider(DocDbPropertyTuple.tupleName(),
                                     DocumentPropertyTupleProvider(dbSessionCreator))

    # Model Set Tuple
    tupleObservable.addTupleProvider(DocDbModelSet.tupleName(),
                                     ModelSetTupleProvider(dbSessionCreator))

    return tupleObservable
