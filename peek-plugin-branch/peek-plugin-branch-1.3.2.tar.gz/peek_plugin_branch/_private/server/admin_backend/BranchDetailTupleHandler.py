import logging

from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler
from vortex.sqla_orm.OrmCrudHandler import OrmCrudHandler, OrmCrudHandlerExtension

from peek_plugin_branch._private.PluginNames import branchFilt
from peek_plugin_branch.tuples.BranchDetailTuple import BranchDetailTuple

logger = logging.getLogger(__name__)

# This dict matches the definition in the Admin angular app.
filtKey = {"key": "admin.Edit.BranchDetailTuple"}
filtKey.update(branchFilt)


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
        selector = {}
        # Copy any filter values into the selector
        # selector["lookupName"] = payloadFilt["lookupName"]
        tupleSelector = TupleSelector(BranchDetailTuple.tupleName(),
                                      selector)
        self._tupleDataObserver.notifyOfTupleUpdate(tupleSelector)
        return True

    afterUpdateCommit = _tellObserver
    afterDeleteCommit = _tellObserver


# This method creates an instance of the handler class.
def makeBranchDetailTupleHandler(tupleObservable, dbSessionCreator):
    handler = __CrudHandler(dbSessionCreator, BranchDetailTuple,
                            filtKey, retreiveAll=True)

    logger.debug("Started")
    handler.addExtension(BranchDetailTuple, __ExtUpdateObservable(tupleObservable))
    return handler
