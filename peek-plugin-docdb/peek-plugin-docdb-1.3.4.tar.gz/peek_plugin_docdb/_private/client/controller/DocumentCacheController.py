import logging
from collections import defaultdict
from typing import Dict, List

from twisted.internet.defer import inlineCallbacks

from peek_plugin_docdb._private.PluginNames import docDbFilt
from peek_plugin_docdb._private.server.client_handlers.ClientChunkLoadRpc import \
    ClientChunkLoadRpc
from peek_plugin_docdb._private.storage.DocDbEncodedChunk import \
    DocDbEncodedChunk
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadEnvelope import PayloadEnvelope

logger = logging.getLogger(__name__)

clientDocumentUpdateFromServerFilt = dict(key="clientDocumentUpdateFromServer")
clientDocumentUpdateFromServerFilt.update(docDbFilt)


class DocumentCacheController:
    """ Document Cache Controller

    The Document cache controller stores all the chunks in memory,
    allowing fast access from the mobile and desktop devices.

    """

    LOAD_CHUNK = 32

    def __init__(self, clientId: str):
        self._clientId = clientId
        self._webAppHandler = None

        #: This stores the cache of document data for the clients
        self._cache: Dict[int, DocDbEncodedChunk] = {}

        self._endpoint = PayloadEndpoint(clientDocumentUpdateFromServerFilt,
                                         self._processDocumentPayload)

    def setDocumentCacheHandler(self, handler):
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
                "Loading DocumentChunk %s to %s" % (offset, offset + self.LOAD_CHUNK))
            encodedChunkTuples: List[DocDbEncodedChunk] = (
                yield ClientChunkLoadRpc.loadDocumentChunks(offset, self.LOAD_CHUNK)
            )

            if not encodedChunkTuples:
                break

            self._loadDocumentIntoCache(encodedChunkTuples)

            offset += self.LOAD_CHUNK

    @inlineCallbacks
    def _processDocumentPayload(self, payloadEnvelope: PayloadEnvelope, **kwargs):
        paylod = yield payloadEnvelope.decodePayloadDefer()
        documentTuples: List[DocDbEncodedChunk] = paylod.tuples
        self._loadDocumentIntoCache(documentTuples)

    def _loadDocumentIntoCache(self,
                                  encodedChunkTuples: List[DocDbEncodedChunk]):
        chunkKeysUpdated: List[str] = []

        for t in encodedChunkTuples:

            if (not t.chunkKey in self._cache or
                    self._cache[t.chunkKey].lastUpdate != t.lastUpdate):
                self._cache[t.chunkKey] = t
                chunkKeysUpdated.append(t.chunkKey)

        logger.debug("Received document updates from server, %s", chunkKeysUpdated)

        self._webAppHandler.notifyOfDocumentUpdate(chunkKeysUpdated)

    def documentChunk(self, chunkKey) -> DocDbEncodedChunk:
        return self._cache.get(chunkKey)

    def documentKeys(self) -> List[int]:
        return list(self._cache)
