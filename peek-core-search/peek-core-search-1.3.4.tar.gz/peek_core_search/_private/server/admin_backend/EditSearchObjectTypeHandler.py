import logging

from peek_core_search._private.PluginNames import searchFilt
from peek_core_search._private.storage.SearchObjectTypeTuple import \
    SearchObjectTypeTuple
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler
from vortex.sqla_orm.OrmCrudHandler import OrmCrudHandler, OrmCrudHandlerExtension

logger = logging.getLogger(__name__)

# This dict matches the definition in the Admin angular app.
filtKey = {"key": "admin.Edit.SearchObjectTypeTuple"}
filtKey.update(searchFilt)


# This is the CRUD hander
class __CrudHandler(OrmCrudHandler):
    pass


class __ExtUpdateObservable(OrmCrudHandlerExtension):
    """ Update Observable ORM Crud Extension

    This extension is called after events that will alter data,
    it then notifies the observer.

    """

    def __init__(self, tupleDataObserver: TupleDataObservableHandler):
        self._tupleDataObserver = tupleDataObserver

    def _tellObserver(self, tuple_, tuples, session, payloadFilt):
        self._tupleDataObserver.notifyOfTupleUpdate(
            TupleSelector(SearchObjectTypeTuple.tupleName(), {})
        )
        return True

    afterUpdateCommit = _tellObserver
    afterDeleteCommit = _tellObserver


# This method creates an instance of the handler class.
def makeSearchObjectTypeHandler(tupleObservable, dbSessionCreator):
    handler = __CrudHandler(dbSessionCreator, SearchObjectTypeTuple,
                            filtKey, retreiveAll=True)

    logger.debug("Started")
    handler.addExtension(SearchObjectTypeTuple, __ExtUpdateObservable(tupleObservable))
    return handler
