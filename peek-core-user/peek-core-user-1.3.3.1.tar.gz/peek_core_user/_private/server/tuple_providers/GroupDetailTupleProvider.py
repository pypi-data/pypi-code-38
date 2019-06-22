import logging

from twisted.internet.defer import inlineCallbacks, Deferred

from peek_core_user._private.server.api.UserApi import UserApi
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class GroupDetailTupleProvider(TuplesProviderABC):
    def __init__(self, ourApi: UserApi):
        self._ourApi = ourApi

        from peek_core_user.server.UserApiABC import UserApiABC
        assert isinstance(self._ourApi, UserApiABC), (
            "We didn't get a UserApiABC")

    @inlineCallbacks
    def makeVortexMsg(self, filt: dict, tupleSelector: TupleSelector) -> Deferred:
        tuples = yield self._ourApi.infoApi.groups()

        payloadEnvelope = yield Payload(filt=filt, tuples=tuples).makePayloadEnvelopeDefer()
        vortexMsg = yield payloadEnvelope.toVortexMsgDefer()
        return vortexMsg
