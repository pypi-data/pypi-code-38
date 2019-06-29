import logging

from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.TupleAction import TupleActionABC
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleActionProcessor import TupleActionProcessorDelegateABC
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_plugin_branch._private.storage.BranchDetailTable import BranchDetailTable
from peek_plugin_branch._private.tuples.CreateBranchActionTuple import \
    CreateBranchActionTuple
from peek_plugin_branch.tuples.BranchDetailTuple import BranchDetailTuple

logger = logging.getLogger(__name__)


class MainController(TupleActionProcessorDelegateABC):
    def __init__(self, dbSessionCreator, tupleObservable: TupleDataObservableHandler):
        self._dbSessionCreator = dbSessionCreator
        self._tupleObservable = tupleObservable

    def shutdown(self):
        pass

    def processTupleAction(self, tupleAction: TupleActionABC) -> Deferred:

        if isinstance(tupleAction, CreateBranchActionTuple):
            return self._processCreateBranch(tupleAction)

        raise NotImplementedError(tupleAction.tupleName())

    @deferToThreadWrapWithLogger(logger)
    def _processCreateBranch(self, action: CreateBranchActionTuple):
        try:
            # Perform update using SQLALchemy
            dbSession = self._dbSessionCreator()

            dbItem = None
            mergeItem = BranchDetailTable.fromTuple(action.branchDetail)

            if action.branchDetail.id is not None:
                rows = dbSession.query(BranchDetailTable) \
                    .filter(BranchDetailTable.id == action.branchDetailId) \
                    .all()
                if rows:
                    dbItem = rows[0]
                    dbItem.merge(mergeItem)

            if not dbItem:
                newItem = BranchDetailTable.fromTuple(action.branchDetail)
                dbSession.add(newItem)

            dbSession.commit()

            # Notify the observer of the update
            # This tuple selector must exactly match what the UI observes
            tupleSelector = TupleSelector(BranchDetailTuple.tupleName(), dict(
                modelSetKey=newItem.modelSetKey
            ))
            self._tupleObservable.notifyOfTupleUpdate(tupleSelector)

        except Exception as e:
            logger.exception(e)

        finally:
            # Always close the dbSession after we create it
            dbSession.close()
