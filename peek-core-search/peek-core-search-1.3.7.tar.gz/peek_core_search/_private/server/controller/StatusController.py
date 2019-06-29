import logging

from twisted.internet.defer import Deferred

from peek_core_search._private.tuples.AdminStatusTuple import AdminStatusTuple
from vortex.TupleAction import TupleActionABC
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleActionProcessor import TupleActionProcessorDelegateABC
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

logger = logging.getLogger(__name__)


class StatusController:
    def __init__(self):
        self._status = AdminStatusTuple()
        self._tupleObservable = None

    def setTupleObservable(self, tupleObserver: TupleDataObservableHandler):
        self._tupleObserver = tupleObserver

    def shutdown(self):
        self._tupleObserver = None

    @property
    def status(self):
        return self._status


    # ---------------
    # Search Index Compiler Methods

    def setSearchIndexCompilerStatus(self, state: bool, queueSize: int):
        self._status.searchIndexCompilerQueueStatus = state
        self._status.searchIndexCompilerQueueSize = queueSize
        self._notify()

    def addToSearchIndexCompilerTotal(self, delta: int):
        self._status.searchIndexCompilerQueueProcessedTotal += delta
        self._notify()

    def setSearchIndexCompilerError(self, error: str):
        self._status.searchIndexCompilerQueueLastError = error
        self._notify()


    # ---------------
    # Search Object Compiler Methods

    def setSearchObjectCompilerStatus(self, state: bool, queueSize: int):
        self._status.searchObjectCompilerQueueStatus = state
        self._status.searchObjectCompilerQueueSize = queueSize
        self._notify()

    def addToSearchObjectCompilerTotal(self, delta: int):
        self._status.searchObjectCompilerQueueProcessedTotal += delta
        self._notify()

    def setSearchObjectCompilerError(self, error: str):
        self._status.searchObjectCompilerQueueLastError = error
        self._notify()

    # ---------------
    # Notify Methods

    def _notify(self):
        self._tupleObserver.notifyOfTupleUpdate(
            TupleSelector(AdminStatusTuple.tupleType(), {})
        )
