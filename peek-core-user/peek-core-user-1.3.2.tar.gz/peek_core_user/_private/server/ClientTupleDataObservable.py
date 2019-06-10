import logging

from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler, \
    TuplesProviderABC

from peek_core_user._private.server.tuple_providers.UserLoginUiSettingTupleProvider import \
    UserLoginUiSettingTupleProvider
from peek_core_user._private.tuples.UserLoginUiSettingTuple import UserLoginUiSettingTuple
from peek_plugin_base.PeekVortexUtil import peekClientName
from peek_core_user._private.PluginNames import userPluginFilt, \
    userPluginObservableName
from peek_core_user._private.server.tuple_providers.GroupDetailTupleProvider import \
    GroupDetailTupleProvider
from peek_core_user._private.server.tuple_providers.UserLoggedInTupleProvider import \
    UserLoggedInTupleProvider
from peek_core_user._private.tuples.UserLoggedInTuple import UserLoggedInTuple
from peek_core_user.tuples.GroupDetailTuple import GroupDetailTuple
from peek_core_user.tuples.UserListItemTuple import \
    UserListItemTuple
from .tuple_providers.UserListItemTupleProvider import UserListItemTupleProvider

logger = logging.getLogger(__name__)


class Dummy(TuplesProviderABC):
    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict, *args):
        return Payload(filt, tuples=[]).makePayloadEnvelope().toVortexMsg()


def makeTupleDataObservableHandler(dbSessionCreator, ourApi):
    observable = TupleDataObservableHandler(observableName=userPluginObservableName,
                                            additionalFilt=userPluginFilt,
                                            acceptOnlyFromVortex=peekClientName)

    observable.addTupleProvider(GroupDetailTuple.tupleName(),
                                GroupDetailTupleProvider(ourApi))

    observable.addTupleProvider(UserListItemTuple.tupleName(),
                                UserListItemTupleProvider(dbSessionCreator, ourApi))

    observable.addTupleProvider(UserLoggedInTuple.tupleType(),
                                UserLoggedInTupleProvider(dbSessionCreator, ourApi))

    observable.addTupleProvider(UserLoginUiSettingTuple.tupleType(),
                                UserLoginUiSettingTupleProvider(dbSessionCreator))

    return observable
