import logging
from typing import Dict, List

from twisted.internet.defer import inlineCallbacks

from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.server.client_handlers.BranchIndexChunkLoadRpc import \
    BranchIndexChunkLoadRpc
from peek_plugin_diagram._private.storage.branch.BranchIndexEncodedChunk import \
    BranchIndexEncodedChunk
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadEnvelope import PayloadEnvelope

logger = logging.getLogger(__name__)

clientBranchIndexUpdateFromServerFilt = dict(key="clientBranchIndexUpdateFromServer")
clientBranchIndexUpdateFromServerFilt.update(diagramFilt)


class BranchIndexCacheController:
    """ BranchIndex Cache Controller

    The BranchIndex cache controller stores all the chunks in memory,
    allowing fast access from the mobile and desktop devices.

    """

    LOAD_CHUNK = 32

    def __init__(self, clientId: str):
        self._clientId = clientId
        self._webAppHandler = None

        #: This stores the cache of branchIndex data for the clients
        self._cache: Dict[int, BranchIndexEncodedChunk] = {}

        self._endpoint = PayloadEndpoint(clientBranchIndexUpdateFromServerFilt,
                                         self._processBranchIndexPayload)

    def setBranchIndexCacheHandler(self, handler):
        self._webAppHandler = handler

    @inlineCallbacks
    def start(self):
        yield self.reloadCache()

    def shutdown(self):
        self._tupleObservable = None

        self._endpoint.shutdown()
        self._endpoint = None

        self._cache = {}

    @inlineCallbacks
    def reloadCache(self):
        self._cache = {}

        offset = 0
        while True:
            logger.info(
                "Loading BranchIndexChunk %s to %s" % (offset, offset + self.LOAD_CHUNK))
            encodedChunkTuples: List[BranchIndexEncodedChunk] = (
                yield BranchIndexChunkLoadRpc.loadBranchIndexChunks(offset, self.LOAD_CHUNK)
            )

            if not encodedChunkTuples:
                break

            self._loadBranchIndexIntoCache(encodedChunkTuples)

            offset += self.LOAD_CHUNK

    @inlineCallbacks
    def _processBranchIndexPayload(self, payloadEnvelope: PayloadEnvelope, **kwargs):
        paylod = yield payloadEnvelope.decodePayloadDefer()
        branchIndexTuples: List[BranchIndexEncodedChunk] = paylod.tuples
        self._loadBranchIndexIntoCache(branchIndexTuples)

    def _loadBranchIndexIntoCache(self,
                                  encodedChunkTuples: List[BranchIndexEncodedChunk]):
        chunkKeysUpdated: List[str] = []

        for t in encodedChunkTuples:
            if (not t.chunkKey in self._cache or
                    self._cache[t.chunkKey].lastUpdate != t.lastUpdate):
                self._cache[t.chunkKey] = t
                chunkKeysUpdated.append(t.chunkKey)

        logger.debug("Received %s grids from server,"
                     " %s had changed ",
                     len(encodedChunkTuples), len(chunkKeysUpdated))

        self._webAppHandler.notifyOfBranchIndexUpdate(chunkKeysUpdated)

    def branchIndexChunk(self, chunkKey) -> BranchIndexEncodedChunk:
        return self._cache.get(chunkKey)

    def branchIndexKeys(self) -> List[int]:
        return list(self._cache)
