import logging

from peek_plugin_docdb._private.PluginNames import docDbFilt
from peek_plugin_docdb._private.storage.DocDbPropertyTuple import DocDbPropertyTuple
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler
from vortex.sqla_orm.OrmCrudHandler import OrmCrudHandler, OrmCrudHandlerExtension

logger = logging.getLogger(__name__)

# This dict matches the definition in the Admin angular app.
filtKey = {"key": "admin.Edit.DocDbPropertyTuple"}
filtKey.update(docDbFilt)


# This is the CRUD hander‰
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
            TupleSelector(DocDbPropertyTuple.tupleName(), {})
        )
        return True

    afterUpdateCommit = _tellObserver
    afterDeleteCommit = _tellObserver


# This method creates an instance of the handler class.
def makeDocumentPropertyHandler(tupleObservable, dbSessionCreator):
    handler = __CrudHandler(dbSessionCreator, DocDbPropertyTuple,
                            filtKey, retreiveAll=True)

    logger.debug("Started")
    handler.addExtension(DocDbPropertyTuple, __ExtUpdateObservable(tupleObservable))
    return handler
