import logging

from peek_plugin_graphdb._private.tuples.ServerStatusTuple import ServerStatusTuple
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleActionProcessor import TupleActionProcessorDelegateABC
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

logger = logging.getLogger(__name__)


class ItemKeyIndexStatusController:
    def __init__(self, status:ServerStatusTuple):
        self._status = status
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
        self._status.itemKeyIndexCompilerQueueStatus = state
        self._status.itemKeyIndexCompilerQueueSize = queueSize
        self._notify()

    def addToCompilerTotal(self, delta: int):
        self._status.itemKeyIndexCompilerQueueProcessedTotal += delta
        self._notify()

    def setCompilerError(self, error: str):
        self._status.itemKeyIndexCompilerQueueLastError = error
        self._notify()

    # ---------------
    # Notify Methods

    def _notify(self):
        self._tupleObserver.notifyOfTupleUpdate(
            TupleSelector(ServerStatusTuple.tupleType(), {})
        )
