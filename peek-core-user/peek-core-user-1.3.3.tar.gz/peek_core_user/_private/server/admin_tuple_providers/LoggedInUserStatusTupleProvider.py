import logging

from twisted.internet.defer import Deferred, inlineCallbacks
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_core_device.server.DeviceApiABC import DeviceApiABC
from peek_core_user._private.storage.InternalUserTuple import InternalUserTuple
from peek_core_user._private.storage.UserLoggedIn import UserLoggedIn
from peek_core_user._private.tuples.LoggedInUserStatusTuple import \
    LoggedInUserStatusTuple

logger = logging.getLogger(__name__)


class LoggedInUserStatusTupleProvider(TuplesProviderABC):
    def __init__(self, dbSessionCreator,
                 deviceApi: DeviceApiABC):
        self._dbSessionCreator = dbSessionCreator
        self._deviceApi = deviceApi

        assert isinstance(self._deviceApi, DeviceApiABC), (
            "We didn't get a DeviceApiABC")

    @inlineCallbacks
    def makeVortexMsg(self, filt: dict, tupleSelector: TupleSelector) -> Deferred:

        tuples = yield self._loadLoggedInTuples()
        tuplesByDeviceToken = {t.deviceToken: t for t in tuples}

        deviceTokens = list(tuplesByDeviceToken)

        deviceDetails = yield self._deviceApi.deviceDetails(deviceTokens)

        for deviceDetail in deviceDetails:
            tuple_ = tuplesByDeviceToken[deviceDetail.deviceToken]
            tuple_.deviceIsOnline = deviceDetail.isOnline
            tuple_.deviceLastOnline = deviceDetail.lastOnline
            tuple_.deviceType = deviceDetail.deviceType
            tuple_.deviceDescription = deviceDetail.description

        payloadEnvelope = yield Payload(filt=filt, tuples=tuples) \
            .makePayloadEnvelopeDefer()
        vortexMsg = yield payloadEnvelope.toVortexMsgDefer()
        return vortexMsg

    @deferToThreadWrapWithLogger(logger)
    def _loadLoggedInTuples(self) -> Deferred:
        dbSession = self._dbSessionCreator()
        try:
            tuples = [
                LoggedInUserStatusTuple(
                    userName=u.userName,
                    userTitle=u.userTitle,
                    loginDate=u.loggedInDateTime,
                    vehicle=u.vehicle,
                    deviceToken=u.deviceToken
                )
                for u in dbSession.query(UserLoggedIn.userName,
                                         UserLoggedIn.loggedInDateTime,
                                         UserLoggedIn.deviceToken,
                                         UserLoggedIn.vehicle,
                                         InternalUserTuple.userTitle)
                    .join(InternalUserTuple,
                          UserLoggedIn.userName == InternalUserTuple.userName)
            ]

            return tuples

        finally:
            dbSession.close()
