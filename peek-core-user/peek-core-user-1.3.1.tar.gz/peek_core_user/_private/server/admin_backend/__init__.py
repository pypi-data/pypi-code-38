from peek_core_user._private.server.admin_backend.InternalGroupTableHandler import \
    makeInternalGroupTableHandler
from .InternalUserTableHandler import makeInternalUserTableHandler
from .SettingPropertyHandler import makeSettingPropertyHandler
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler


def makeAdminBackendHandlers(tupleObservable: TupleDataObservableHandler,
                             dbSessionCreator):
    yield makeInternalUserTableHandler(tupleObservable, dbSessionCreator)
    yield makeInternalGroupTableHandler(tupleObservable, dbSessionCreator)

    yield makeSettingPropertyHandler(dbSessionCreator)

