import logging
from typing import Union

from twisted.internet.defer import Deferred, inlineCallbacks

from peek_core_search._private.client.controller.SearchIndexCacheController import \
    SearchIndexCacheController
from peek_core_search._private.tuples.search_index.SearchIndexUpdateDateTuple import \
    SearchIndexUpdateDateTuple
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class ClientSearchIndexUpdateDateTupleProvider(TuplesProviderABC):
    def __init__(self, cacheHandler: SearchIndexCacheController):
        self._cacheHandler = cacheHandler

    @inlineCallbacks
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        tuple_ = SearchIndexUpdateDateTuple()
        tuple_.updateDateByChunkKey = {
            key:self._cacheHandler.searchIndex(key).lastUpdate
            for key in self._cacheHandler.searchIndexKeys()
        }
        payload = Payload(filt, tuples=[tuple_])
        payloadEnvelope = yield payload.makePayloadEnvelopeDefer()
        vortexMsg = yield payloadEnvelope.toVortexMsg()
        return vortexMsg
