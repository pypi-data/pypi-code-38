import logging

from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_core_device.server.DeviceApiABC import DeviceApiABC
from peek_plugin_base.PeekVortexUtil import peekAdminName
from peek_core_user._private.PluginNames import userPluginFilt, \
    userPluginObservableName
from peek_core_user._private.server.admin_tuple_providers.LoggedInUserStatusTupleProvider import \
    LoggedInUserStatusTupleProvider
from peek_core_user._private.server.tuple_providers.GroupDetailTupleProvider import \
    GroupDetailTupleProvider
from peek_core_user._private.server.tuple_providers.UserListItemTupleProvider import \
    UserListItemTupleProvider
from peek_core_user._private.server.tuple_providers.UserLoggedInTupleProvider import \
    UserLoggedInTupleProvider
from peek_core_user._private.tuples.LoggedInUserStatusTuple import \
    LoggedInUserStatusTuple
from peek_core_user._private.tuples.UserLoggedInTuple import UserLoggedInTuple
from peek_core_user.tuples.GroupDetailTuple import GroupDetailTuple
from peek_core_user.tuples.UserListItemTuple import UserListItemTuple

logger = logging.getLogger(__name__)


def makeAdminTupleDataObservableHandler(dbSessionCreator, deviceApi: DeviceApiABC, ourApi):
    observable = TupleDataObservableHandler(observableName=userPluginObservableName,
                                            additionalFilt=userPluginFilt,
                                            acceptOnlyFromVortex=peekAdminName)

    observable.addTupleProvider(
        LoggedInUserStatusTuple.tupleName(),
        LoggedInUserStatusTupleProvider(dbSessionCreator, deviceApi)
    )

    observable.addTupleProvider(GroupDetailTuple.tupleName(),
                                GroupDetailTupleProvider(ourApi))

    observable.addTupleProvider(UserListItemTuple.tupleName(),
                                UserListItemTupleProvider(dbSessionCreator, ourApi))

    observable.addTupleProvider(UserLoggedInTuple.tupleType(),
                                UserLoggedInTupleProvider(dbSessionCreator, ourApi))

    return observable
