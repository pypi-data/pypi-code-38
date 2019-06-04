from peek_plugin_index_blueprint._private.client.controller.ThingIndexCacheController import \
    ThingIndexCacheController
from peek_plugin_index_blueprint._private.client.tuple_providers.ThingTupleProvider import \
    ThingTupleProvider
from peek_plugin_index_blueprint._private.client.tuple_providers.ThingIndexUpdateDateTupleProvider import \
    ThingIndexUpdateDateTupleProvider
from peek_plugin_index_blueprint._private.tuples.ThingIndexUpdateDateTuple import \
    ThingIndexUpdateDateTuple
from peek_plugin_index_blueprint.tuples.ThingTuple import ThingTuple
from vortex.handler.TupleDataObservableProxyHandler import TupleDataObservableProxyHandler


def makeClientTupleDataObservableHandler(
        tupleObservable: TupleDataObservableProxyHandler,
        cacheHandler: ThingIndexCacheController):
    """" Make CLIENT Tuple Data Observable Handler

    This method registers the tuple providers for the proxy, that are served locally.

    :param cacheHandler:
    :param tupleObservable: The tuple observable proxy

    """

    tupleObservable.addTupleProvider(ThingTuple.tupleName(),
                                     ThingTupleProvider(cacheHandler))

    tupleObservable.addTupleProvider(ThingIndexUpdateDateTuple.tupleName(),
                                     ThingIndexUpdateDateTupleProvider(cacheHandler))
