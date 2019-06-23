from peek_core_search._private.client.controller.SearchIndexCacheController import \
    SearchIndexCacheController
from peek_core_search._private.client.controller.SearchObjectCacheController import \
    SearchObjectCacheController
from peek_core_search._private.client.tuple_providers.ClientSearchIndexUpdateDateTupleProvider import \
    ClientSearchIndexUpdateDateTupleProvider
from peek_core_search._private.client.tuple_providers.ClientSearchObjectResultTupleProvider import \
    ClientSearchObjectResultTupleProvider
from peek_core_search._private.client.tuple_providers.ClientSearchObjectUpdateDateTupleProvider import \
    ClientSearchObjectUpdateDateTupleProvider
from peek_core_search._private.tuples.search_index.SearchIndexUpdateDateTuple import \
    SearchIndexUpdateDateTuple
from peek_core_search._private.tuples.search_object.SearchObjectUpdateDateTuple import \
    SearchObjectUpdateDateTuple
from peek_core_search._private.tuples.search_object.SearchResultObjectTuple import \
    SearchResultObjectTuple
from vortex.handler.TupleDataObservableProxyHandler import TupleDataObservableProxyHandler


def makeClientTupleDataObservableHandler(
        tupleObservable: TupleDataObservableProxyHandler,
        searchIndexCacheHandler: SearchIndexCacheController,
        searchObjectCacheHandler: SearchObjectCacheController):
    """" Make CLIENT Tuple Data Observable Handler

    This method creates the observable object, registers the tuple providers and then
    returns it.

    :param tupleObservable: The tuple observable proxy
    :param searchIndexCacheHandler: The search index cache handler
    :param searchObjectCacheHandler: The search object cache handler
    :return: An instance of :code:`TupleDataObservableHandler`

    """

    tupleObservable.addTupleProvider(
        SearchResultObjectTuple.tupleName(),
        ClientSearchObjectResultTupleProvider(searchIndexCacheHandler,
                                              searchObjectCacheHandler)
    )

    tupleObservable.addTupleProvider(
        SearchIndexUpdateDateTuple.tupleName(),
        ClientSearchIndexUpdateDateTupleProvider(searchIndexCacheHandler))

    tupleObservable.addTupleProvider(
        SearchObjectUpdateDateTuple.tupleName(),
        ClientSearchObjectUpdateDateTupleProvider(searchObjectCacheHandler))
