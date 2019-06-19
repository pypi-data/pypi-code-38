from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler
from .SettingPropertyHandler import makeSettingPropertyHandler
from .ViewSegmentHandler import makeSegmentTableHandler


def makeAdminBackendHandlers(tupleObservable: TupleDataObservableHandler,
                             dbSessionCreator):
    yield makeSegmentTableHandler(tupleObservable, dbSessionCreator)

    yield makeSettingPropertyHandler(dbSessionCreator)

