import logging
from typing import Union

from twisted.internet.defer import Deferred, inlineCallbacks

from peek_plugin_diagram._private.client.controller.BranchIndexCacheController import \
    BranchIndexCacheController
from peek_plugin_diagram._private.tuples.branch.BranchIndexUpdateDateTuple import \
    BranchIndexUpdateDateTuple
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class BranchIndexUpdateDateTupleProvider(TuplesProviderABC):
    def __init__(self, cacheHandler: BranchIndexCacheController):
        self._cacheHandler = cacheHandler

    @inlineCallbacks
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        tuple_ = BranchIndexUpdateDateTuple()
        tuple_.updateDateByChunkKey = {
            key:self._cacheHandler.branchIndexChunk(key).lastUpdate
            for key in self._cacheHandler.branchIndexKeys()
        }
        payload = Payload(filt, tuples=[tuple_])
        payloadEnvelope = yield payload.makePayloadEnvelopeDefer()
        vortexMsg = yield payloadEnvelope.toVortexMsg()
        return vortexMsg
