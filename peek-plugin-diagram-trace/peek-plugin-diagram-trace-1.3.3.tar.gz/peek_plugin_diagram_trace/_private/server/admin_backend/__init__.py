from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from .SettingPropertyHandler import makeSettingPropertyHandler


def makeAdminBackendHandlers(tupleObservable: TupleDataObservableHandler,
                             dbSessionCreator):
    yield makeSettingPropertyHandler(dbSessionCreator, tupleObservable)
