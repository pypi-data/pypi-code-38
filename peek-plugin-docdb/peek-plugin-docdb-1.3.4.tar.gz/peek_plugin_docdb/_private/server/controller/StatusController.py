import logging

from peek_plugin_docdb._private.tuples.AdminStatusTuple import AdminStatusTuple
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
    # Search Object Compiler Methods

    def setCompilerStatus(self, state: bool, queueSize: int):
        self._status.documentCompilerQueueStatus = state
        self._status.documentCompilerQueueSize = queueSize
        self._notify()

    def addToCompilerTotal(self, delta: int):
        self._status.documentCompilerQueueProcessedTotal += delta
        self._notify()

    def setCompilerError(self, error: str):
        self._status.documentCompilerQueueLastError = error
        self._notify()

    # ---------------
    # Notify Methods

    def _notify(self):
        self._tupleObserver.notifyOfTupleUpdate(
            TupleSelector(AdminStatusTuple.tupleType(), {})
        )
