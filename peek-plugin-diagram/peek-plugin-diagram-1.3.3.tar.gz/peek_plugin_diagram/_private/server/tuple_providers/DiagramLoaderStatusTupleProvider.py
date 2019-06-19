import logging
from typing import Union

from twisted.internet.defer import Deferred, inlineCallbacks

from peek_plugin_diagram._private.server.controller.StatusController import \
    StatusController
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class DiagramLoaderStatusTupleProvider(TuplesProviderABC):
    def __init__(self, statusController: StatusController):
        self._statusController = statusController

    @inlineCallbacks
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        tuples = [self._statusController.status]

        payloadEnvelope = yield Payload(filt, tuples=tuples).makePayloadEnvelopeDefer()
        vortexMsg = yield payloadEnvelope.toVortexMsgDefer()
        return vortexMsg
