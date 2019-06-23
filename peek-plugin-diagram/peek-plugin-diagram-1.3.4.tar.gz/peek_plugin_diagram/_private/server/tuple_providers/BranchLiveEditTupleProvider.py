import logging
from typing import Union

from twisted.internet.defer import Deferred, inlineCallbacks
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_plugin_diagram._private.server.controller.BranchLiveEditController import \
    BranchLiveEditController

logger = logging.getLogger(__name__)


class BranchLiveEditTupleProvider(TuplesProviderABC):
    def __init__(self, branchLiveEditController: BranchLiveEditController):
        self._controller = branchLiveEditController

    @inlineCallbacks
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        coordSetId = tupleSelector.selector.get("coordSetId")
        key = tupleSelector.selector.get("key")

        tuple = self._controller.getLiveEditTuple(coordSetId, key)
        tuples = [tuple] if tuple else []

        payloadEnvelope = yield Payload(filt, tuples=tuples).makePayloadEnvelopeDefer()
        vortexMsg = yield payloadEnvelope.toVortexMsgDefer()
        return vortexMsg
