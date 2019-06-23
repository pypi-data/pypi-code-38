import logging
from collections import defaultdict
from typing import Dict, List

from twisted.internet.defer import inlineCallbacks

from peek_core_search._private.PluginNames import searchFilt
from peek_core_search._private.server.client_handlers.ClientChunkLoadRpc import \
    ClientChunkLoadRpc
from peek_core_search._private.storage.EncodedSearchObjectChunk import \
    EncodedSearchObjectChunk
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadEnvelope import PayloadEnvelope

logger = logging.getLogger(__name__)

clientSearchObjectUpdateFromServerFilt = dict(key="clientSearchObjectUpdateFromServer")
clientSearchObjectUpdateFromServerFilt.update(searchFilt)


class SearchObjectCacheController:
    """ SearchObject Cache Controller

    The SearchObject cache controller stores all the chunks in memory,
    allowing fast access from the mobile and desktop devices.

    """

    LOAD_CHUNK = 32

    def __init__(self, clientId: str):
        self._clientId = clientId
        self._webAppHandler = None

        #: This stores the cache of searchObject data for the clients
        self._cache: Dict[int, EncodedSearchObjectChunk] = {}

        self._endpoint = PayloadEndpoint(clientSearchObjectUpdateFromServerFilt,
                                         self._processSearchObjectPayload)

    def setSearchObjectCacheHandler(self, handler):
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
                "Loading SearchObjectChunk %s to %s" % (offset, offset + self.LOAD_CHUNK))
            encodedChunkTuples: List[EncodedSearchObjectChunk] = (
                yield ClientChunkLoadRpc.loadSearchObjectChunks(offset, self.LOAD_CHUNK)
            )

            if not encodedChunkTuples:
                break

            self._loadSearchObjectIntoCache(encodedChunkTuples)

            offset += self.LOAD_CHUNK

    @inlineCallbacks
    def _processSearchObjectPayload(self, payloadEnvelope: PayloadEnvelope, **kwargs):
        paylod = yield payloadEnvelope.decodePayloadDefer()
        searchObjectTuples: List[EncodedSearchObjectChunk] = paylod.tuples
        self._loadSearchObjectIntoCache(searchObjectTuples)

    def _loadSearchObjectIntoCache(self,
                                  encodedChunkTuples: List[EncodedSearchObjectChunk]):
        chunkKeysUpdated: List[str] = []

        for t in encodedChunkTuples:

            if (not t.chunkKey in self._cache or
                    self._cache[t.chunkKey].lastUpdate != t.lastUpdate):
                self._cache[t.chunkKey] = t
                chunkKeysUpdated.append(t.chunkKey)

        logger.debug("Received searchObject updates from server, %s", chunkKeysUpdated)

        self._webAppHandler.notifyOfSearchObjectUpdate(chunkKeysUpdated)

    def searchObject(self, chunkKey) -> EncodedSearchObjectChunk:
        return self._cache.get(chunkKey)

    def searchObjectKeys(self) -> List[int]:
        return list(self._cache)
