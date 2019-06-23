from peek_plugin_docdb._private.client.controller.DocumentCacheController import \
    DocumentCacheController
from peek_plugin_docdb._private.client.tuple_providers.ClientDocumentTupleProvider import \
    ClientDocumentTupleProvider
from peek_plugin_docdb._private.client.tuple_providers.ClientDocumentUpdateDateTupleProvider import \
    ClientDocumentUpdateDateTupleProvider
from peek_plugin_docdb._private.tuples.DocumentUpdateDateTuple import \
    DocumentUpdateDateTuple
from peek_plugin_docdb.tuples.DocumentTuple import DocumentTuple
from vortex.handler.TupleDataObservableProxyHandler import TupleDataObservableProxyHandler


def makeClientTupleDataObservableHandler(
        tupleObservable: TupleDataObservableProxyHandler,
        cacheHandler: DocumentCacheController):
    """" Make CLIENT Tuple Data Observable Handler

    This method registers the tuple providers for the proxy, that are served locally.

    :param cacheHandler:
    :param tupleObservable: The tuple observable proxy

    """

    tupleObservable.addTupleProvider(DocumentTuple.tupleName(),
                                     ClientDocumentTupleProvider(cacheHandler))

    tupleObservable.addTupleProvider(DocumentUpdateDateTuple.tupleName(),
                                     ClientDocumentUpdateDateTupleProvider(cacheHandler))
