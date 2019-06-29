# from .StringIntTableHandler import makeStringIntTableHandler
from .SettingPropertyHandler import makeSettingPropertyHandler
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler


def makeAdminBackendHandlers(tupleObservable: TupleDataObservableHandler,
                             dbSessionCreator):
    # yield makeStringIntTableHandler(tupleObservable, dbSessionCreator)

    yield makeSettingPropertyHandler(dbSessionCreator)
    pass
