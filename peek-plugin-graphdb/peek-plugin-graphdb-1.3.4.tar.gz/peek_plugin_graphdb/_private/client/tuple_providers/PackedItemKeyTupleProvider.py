import json
import logging
from collections import defaultdict
from typing import Union, List

from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_plugin_graphdb._private.client.controller.ItemKeyIndexCacheController import \
    ItemKeyIndexCacheController
from peek_plugin_graphdb._private.storage.ItemKeyIndexEncodedChunk import \
    ItemKeyIndexEncodedChunk
from peek_plugin_graphdb._private.tuples.GraphDbPackedItemKeyTuple import \
    GraphDbPackedItemKeyTuple
from peek_plugin_graphdb._private.worker.tasks._ItemKeyIndexCalcChunkKey import \
    makeChunkKeyForItemKey

logger = logging.getLogger(__name__)


class PackedItemKeyTupleProvider(TuplesProviderABC):
    def __init__(self, cacheController: ItemKeyIndexCacheController):
        self._cacheController = cacheController

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        modelSetKey = tupleSelector.selector["modelSetKey"]
        keys = tupleSelector.selector["keys"]

        keysByChunkKey = defaultdict(list)

        foundDocuments: List[GraphDbPackedItemKeyTuple] = []

        for key in keys:
            keysByChunkKey[makeChunkKeyForItemKey(modelSetKey, key)].append(key)

        for chunkKey, subKeys in keysByChunkKey.items():
            chunk: ItemKeyIndexEncodedChunk = self._cacheController.itemKeyIndexChunk(chunkKey)

            if not chunk:
                logger.warning("GraphDb ItemKey chunk %s is missing from cache", chunkKey)
                continue

            segmentsByKeyStr = Payload().fromEncodedPayload(chunk.encodedData).tuples[0]
            segmentsByKey = json.loads(segmentsByKeyStr)

            for subKey in subKeys:
                if subKey not in segmentsByKey:
                    logger.warning(
                        "ItemKey %s is missing from index, chunkKey %s",
                        subKey, chunkKey
                    )
                    continue

                # Create the new object
                foundDocuments.append(GraphDbPackedItemKeyTuple(
                    key=subKey,
                    packedJson=segmentsByKey[subKey]
                ))

        # Create the vortex message
        return Payload(filt, tuples=foundDocuments).makePayloadEnvelope().toVortexMsg()
