import logging
from typing import Union

from twisted.internet.defer import Deferred, inlineCallbacks

from peek_plugin_diagram._private.client.controller.LocationIndexCacheController import \
    LocationIndexCacheController
from peek_plugin_diagram._private.tuples.location_index.LocationIndexUpdateDateTuple import \
    LocationIndexUpdateDateTuple
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class ClientLocationIndexUpdateDateTupleProvider(TuplesProviderABC):
    def __init__(self, cacheHandler: LocationIndexCacheController):
        self._cacheHandler = cacheHandler

    @inlineCallbacks
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        tuple_ = LocationIndexUpdateDateTuple()
        tuple_.updateDateByChunkKey = {
            key:self._cacheHandler.locationIndex(key).lastUpdate
            for key in self._cacheHandler.locationIndexKeys()
        }
        payload = Payload(filt, tuples=[tuple_])
        payloadEnvelope = yield payload.makePayloadEnvelopeDefer()
        vortexMsg = yield payloadEnvelope.toVortexMsg()
        return vortexMsg
