from vortex.handler.TupleDataObservableProxyHandler import TupleDataObservableProxyHandler

from peek_plugin_graphdb._private.client.controller.ItemKeyIndexCacheController import \
    ItemKeyIndexCacheController
from peek_plugin_graphdb._private.client.controller.SegmentCacheController import \
    SegmentCacheController
from peek_plugin_graphdb._private.client.controller.TraceConfigCacheController import \
    TraceConfigCacheController
from peek_plugin_graphdb._private.client.controller.TracerController import \
    TracerController
from peek_plugin_graphdb._private.client.tuple_providers.ItemKeyIndexUpdateDateTupleProvider import \
    ItemKeyIndexUpdateDateTupleProvider
from peek_plugin_graphdb._private.client.tuple_providers.PackedItemKeyTupleProvider import \
    PackedItemKeyTupleProvider
from peek_plugin_graphdb._private.client.tuple_providers.PackedSegmentTupleProvider import \
    PackedSegmentTupleProvider
from peek_plugin_graphdb._private.client.tuple_providers.SegmentUpdateDateTupleProvider import \
    SegmentUpdateDateTupleProvider
from peek_plugin_graphdb._private.client.tuple_providers.TraceConfigTupleProvider import \
    TraceConfigTupleProvider
from peek_plugin_graphdb._private.client.tuple_providers.TraceResultTupleProvider import \
    TraceResultTupleProvider
from peek_plugin_graphdb._private.tuples.GraphDbPackedSegmentTuple import \
    GraphDbPackedSegmentTuple
from peek_plugin_graphdb._private.tuples.ItemKeyIndexUpdateDateTuple import \
    ItemKeyIndexUpdateDateTuple
from peek_plugin_graphdb._private.tuples.ItemKeyTuple import ItemKeyTuple
from peek_plugin_graphdb._private.tuples.SegmentIndexUpdateDateTuple import \
    SegmentIndexUpdateDateTuple
from peek_plugin_graphdb.tuples.GraphDbTraceConfigTuple import GraphDbTraceConfigTuple
from peek_plugin_graphdb.tuples.GraphDbTraceResultTuple import GraphDbTraceResultTuple


def makeClientTupleDataObservableHandler(
        tupleObservable: TupleDataObservableProxyHandler,
        segmentCacheController: SegmentCacheController,
        itemKeyCacheController: ItemKeyIndexCacheController,
        traceConfigCacheController: TraceConfigCacheController,
        tracerController: TracerController):
    """" Make CLIENT Tuple Data Observable Controller

    This method registers the tuple providers for the proxy, that are served locally.

    :param tracerController:
    :param itemKeyCacheController:
    :param segmentCacheController:
    :param traceConfigCacheController:
    :param tupleObservable: The tuple observable proxy

    """

    tupleObservable.addTupleProvider(
        GraphDbTraceResultTuple.tupleName(),
        TraceResultTupleProvider(tracerController)
    )

    tupleObservable.addTupleProvider(
        SegmentIndexUpdateDateTuple.tupleName(),
        SegmentUpdateDateTupleProvider(segmentCacheController)
    )

    tupleObservable.addTupleProvider(
        GraphDbTraceConfigTuple.tupleName(),
        TraceConfigTupleProvider(traceConfigCacheController)
    )

    tupleObservable.addTupleProvider(ItemKeyIndexUpdateDateTuple.tupleName(),
                                     ItemKeyIndexUpdateDateTupleProvider(
                                         itemKeyCacheController))

    tupleObservable.addTupleProvider(
        ItemKeyTuple.tupleName(),
        PackedItemKeyTupleProvider(itemKeyCacheController)
    )

    tupleObservable.addTupleProvider(
        GraphDbPackedSegmentTuple.tupleName(),
        PackedSegmentTupleProvider(segmentCacheController)
    )
