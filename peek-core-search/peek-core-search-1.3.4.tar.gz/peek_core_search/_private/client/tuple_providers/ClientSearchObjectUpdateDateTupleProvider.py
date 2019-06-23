import logging
from typing import Union

from twisted.internet.defer import Deferred, inlineCallbacks

from peek_core_search._private.client.controller.SearchObjectCacheController import \
    SearchObjectCacheController
from peek_core_search._private.tuples.search_object.SearchObjectUpdateDateTuple import \
    SearchObjectUpdateDateTuple
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class ClientSearchObjectUpdateDateTupleProvider(TuplesProviderABC):
    def __init__(self, cacheHandler: SearchObjectCacheController):
        self._cacheHandler = cacheHandler

    @inlineCallbacks
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        tuple_ = SearchObjectUpdateDateTuple()
        tuple_.updateDateByChunkKey = {
            key:self._cacheHandler.searchObject(key).lastUpdate
            for key in self._cacheHandler.searchObjectKeys()
        }
        payload = Payload(filt, tuples=[tuple_])
        payloadEnvelope = yield payload.makePayloadEnvelopeDefer()
        vortexMsg = yield payloadEnvelope.toVortexMsg()
        return vortexMsg
