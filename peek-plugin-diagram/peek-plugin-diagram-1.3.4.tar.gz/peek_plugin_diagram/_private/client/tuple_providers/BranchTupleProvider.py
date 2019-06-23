import ujson as json
import logging
from collections import defaultdict
from typing import Union, List

from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_plugin_diagram._private.client.controller.BranchIndexCacheController import \
    BranchIndexCacheController
from peek_plugin_diagram._private.storage.branch.BranchIndexEncodedChunk import \
    BranchIndexEncodedChunk
from peek_plugin_diagram._private.worker.tasks.branch._BranchIndexCalcChunkKey import \
    makeChunkKeyForBranchIndex
from peek_plugin_diagram._private.tuples.branch.BranchTuple import BranchTuple

logger = logging.getLogger(__name__)


class BranchTupleProvider(TuplesProviderABC):
    def __init__(self, cacheHandler: BranchIndexCacheController):
        self._cacheHandler = cacheHandler

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        modelSetKey = tupleSelector.selector["modelSetKey"]
        coordSetId = tupleSelector.selector["coordSetId"]
        keys = tupleSelector.selector["keys"]

        keysByChunkKey = defaultdict(list)

        results: List[BranchTuple] = []

        for key in keys:
            keysByChunkKey[makeChunkKeyForBranchIndex(modelSetKey, key)].append(key)

        for chunkKey, branchKeys in keysByChunkKey.items():
            chunk: BranchIndexEncodedChunk = self._cacheHandler.branchIndexChunk(chunkKey)

            if not chunk:
                logger.warning("BranchIndex chunk %s is missing from cache", chunkKey)
                continue

            resultsByKeyStr = Payload().fromEncodedPayload(chunk.encodedData).tuples[0]
            resultsByKey = json.loads(resultsByKeyStr)

            for branchKey in branchKeys:
                if branchKey not in resultsByKey:
                    logger.warning(
                        "Branch %s is missing from index, chunkKey %s",
                        branchKey, chunkKey
                    )
                    continue

                packedJsons = resultsByKey[branchKey]

                for packedJson  in packedJsons:
                    result = BranchTuple.loadFromJson(packedJson, None, None)
                    if result.coordSetId == coordSetId or coordSetId is None:
                        results.append(result)

        # Create the vortex message
        return Payload(filt, tuples=results).makePayloadEnvelope().toVortexMsg()
