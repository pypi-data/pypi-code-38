import logging

from twisted.internet.defer import Deferred, inlineCallbacks

from peek_core_user._private.server.api.UserApi import UserApi
from peek_core_user._private.storage.Setting import globalSetting, MOBILE_LOGIN_GROUP
from peek_core_user.tuples.UserListItemTuple import \
    UserListItemTuple
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class UserListItemTupleProvider(TuplesProviderABC):
    def __init__(self, dbSessionCreator,
                 ourApi: UserApi):
        self._dbSessionCreator = dbSessionCreator
        self._ourApi = ourApi

        from peek_core_user.server.UserApiABC import UserApiABC
        assert isinstance(self._ourApi, UserApiABC), (
            "We didn't get a UserApiABC")

    @inlineCallbacks
    def makeVortexMsg(self, filt: dict, tupleSelector: TupleSelector) -> Deferred:
        # TODO HACK - Hard coded for mobile users
        mobileGroup = yield self._mobileGroup()
        users = yield self._ourApi.infoApi.users(groupNames=[mobileGroup])

        tuples = []
        for userDetails in users:
            tuples.append(UserListItemTuple(userId=userDetails.userName,
                                            displayName=userDetails.userTitle))

        payload = Payload(filt=filt, tuples=tuples)
        paylodEnvelope = yield payload.makePayloadEnvelopeDefer()
        vortexMsg = yield paylodEnvelope.toVortexMsgDefer()
        return vortexMsg

    @deferToThreadWrapWithLogger(logger)
    def _mobileGroup(self):
        ormSession = self._dbSessionCreator()
        try:
            return globalSetting(ormSession, MOBILE_LOGIN_GROUP)
        finally:
            ormSession.close()
