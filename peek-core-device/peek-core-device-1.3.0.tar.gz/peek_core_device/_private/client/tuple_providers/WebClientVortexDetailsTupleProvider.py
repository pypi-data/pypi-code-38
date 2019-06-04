import logging
from typing import Union

from twisted.internet.defer import Deferred

from peek_core_device._private.tuples.WebClientVortexDetailsTuple import \
    WebClientVortexDetailsTuple
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)

class WebClientVortexDetailsTupleProvider(TuplesProviderABC):
    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        from peek_platform import PeekPlatformConfig


        tuple = WebClientVortexDetailsTuple()
        tuple.websocketPort = PeekPlatformConfig.config.webSocketPort

        # Create the vortex message
        return Payload(filt, tuples=[tuple]).makePayloadEnvelope().toVortexMsg()
