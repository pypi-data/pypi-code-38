import logging
from typing import Union

from twisted.internet.defer import Deferred, inlineCallbacks

from peek_plugin_docdb._private.client.controller.DocumentCacheController import \
    DocumentCacheController
from peek_plugin_docdb._private.tuples.DocumentUpdateDateTuple import \
    DocumentUpdateDateTuple
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class ClientDocumentUpdateDateTupleProvider(TuplesProviderABC):
    def __init__(self, cacheHandler: DocumentCacheController):
        self._cacheHandler = cacheHandler

    @inlineCallbacks
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        tuple_ = DocumentUpdateDateTuple()
        tuple_.updateDateByChunkKey = {
            key:self._cacheHandler.documentChunk(key).lastUpdate
            for key in self._cacheHandler.documentKeys()
        }
        payload = Payload(filt, tuples=[tuple_])
        payloadEnvelope = yield payload.makePayloadEnvelopeDefer()
        vortexMsg = yield payloadEnvelope.toVortexMsg()
        return vortexMsg
