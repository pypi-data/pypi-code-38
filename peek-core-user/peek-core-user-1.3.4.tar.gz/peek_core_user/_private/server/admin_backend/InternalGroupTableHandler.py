import logging

from peek_core_user._private.PluginNames import userPluginFilt
from peek_core_user._private.storage.InternalGroupTuple import InternalGroupTuple
from peek_core_user.tuples.GroupDetailTuple import GroupDetailTuple
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler
from vortex.sqla_orm.OrmCrudHandler import OrmCrudHandler, OrmCrudHandlerExtension

logger = logging.getLogger(__name__)

# This dict matches the definition in the Admin angular app.
filtKey = {"key": "admin.Edit.InternalGroupTuple"}
filtKey.update(userPluginFilt)


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
            TupleSelector(InternalGroupTuple.tupleName(), {})
        )
        self._tupleDataObserver.notifyOfTupleUpdate(
            TupleSelector(GroupDetailTuple.tupleName(), {})
        )
        return True

    afterUpdateCommit = _tellObserver
    afterDeleteCommit = _tellObserver


# This method creates an instance of the handler class.
def makeInternalGroupTableHandler(tupleObservable, dbSessionCreator):
    handler = __CrudHandler(dbSessionCreator, InternalGroupTuple,
                            filtKey, retreiveAll=True)

    logger.debug("Started")
    handler.addExtension(InternalGroupTuple, __ExtUpdateObservable(tupleObservable))
    return handler
