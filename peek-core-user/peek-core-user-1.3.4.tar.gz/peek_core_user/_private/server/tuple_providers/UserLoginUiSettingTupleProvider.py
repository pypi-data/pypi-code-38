import logging

from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_core_user._private.storage.Setting import globalSetting, SHOW_LOGIN_AS_LIST, \
    SHOW_VEHICLE_INPUT
from peek_core_user._private.tuples.UserLoginUiSettingTuple import UserLoginUiSettingTuple
from peek_plugin_base.storage.DbConnection import DbSessionCreator

logger = logging.getLogger(__name__)


class UserLoginUiSettingTupleProvider(TuplesProviderABC):
    def __init__(self, dbSessionCreator: DbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict, tupleSelector: TupleSelector) -> Deferred:
        tuple_ = UserLoginUiSettingTuple()

        dbSession = self._dbSessionCreator()
        try:
            tuple_.showUsersAsList = globalSetting(dbSession, SHOW_LOGIN_AS_LIST)
            tuple_.showVehicleInput = globalSetting(dbSession, SHOW_VEHICLE_INPUT)

        finally:
            dbSession.close()

        payloadEnvelope = Payload(filt=filt, tuples=[tuple_]).makePayloadEnvelope()
        vortexMsg = payloadEnvelope.toVortexMsg()
        return vortexMsg
