from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from .EditThingTypeHandler import makeThingTypeHandler


def makeAdminBackendHandlers(tupleObservable: TupleDataObservableHandler,
                             dbSessionCreator):

    yield makeThingTypeHandler(tupleObservable, dbSessionCreator)

