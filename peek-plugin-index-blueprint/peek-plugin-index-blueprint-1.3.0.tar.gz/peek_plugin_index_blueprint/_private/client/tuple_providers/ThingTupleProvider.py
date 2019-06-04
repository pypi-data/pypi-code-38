import json
import logging
from collections import defaultdict
from typing import Union, List

from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_plugin_index_blueprint._private.client.controller.ThingIndexCacheController import \
    ThingIndexCacheController
from peek_plugin_index_blueprint._private.storage.ThingIndexEncodedChunk import \
    ThingIndexEncodedChunk
from peek_plugin_index_blueprint._private.worker.tasks._ThingIndexCalcChunkKey import \
    makeChunkKey
from peek_plugin_index_blueprint.tuples.ThingTuple import ThingTuple

logger = logging.getLogger(__name__)


class ThingTupleProvider(TuplesProviderABC):
    def __init__(self, cacheHandler: ThingIndexCacheController):
        self._cacheHandler = cacheHandler

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        modelSetKey = tupleSelector.selector["modelSetKey"]
        keys = tupleSelector.selector["keys"]

        keysByChunkKey = defaultdict(list)

        results: List[ThingTuple] = []

        for key in keys:
            keysByChunkKey[makeChunkKey(modelSetKey, key)].append(key)

        for chunkKey, subKeys in keysByChunkKey.items():
            chunk: ThingIndexEncodedChunk = self._cacheHandler.thingIndexChunk(chunkKey)

            if not chunk:
                logger.warning("ThingIndex chunk %s is missing from cache", chunkKey)
                continue

            resultsByKeyStr = Payload().fromEncodedPayload(chunk.encodedData).tuples[0]
            resultsByKey = json.loads(resultsByKeyStr)

            for subKey in subKeys:
                if subKey not in resultsByKey:
                    logger.warning(
                        "Thing %s is missing from index, chunkKey %s",
                        subKey, chunkKey
                    )
                    continue

                packedJson = resultsByKey[subKey]

                results.append(ThingTuple.unpackJson(subKey, packedJson))

        # Create the vortex message
        return Payload(filt, tuples=results).makePayloadEnvelope().toVortexMsg()
