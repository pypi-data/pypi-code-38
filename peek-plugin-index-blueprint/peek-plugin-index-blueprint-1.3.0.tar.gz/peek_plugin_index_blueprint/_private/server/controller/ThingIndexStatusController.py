import logging

from peek_plugin_index_blueprint._private.tuples.ThingIndexServerStatusTuple import ThingIndexServerStatusTuple
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleActionProcessor import TupleActionProcessorDelegateABC
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

logger = logging.getLogger(__name__)


class ThingIndexStatusController:
    def __init__(self):
        self._status = ThingIndexServerStatusTuple()
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
        self._status.thingIndexCompilerQueueStatus = state
        self._status.thingIndexCompilerQueueSize = queueSize
        self._notify()

    def addToCompilerTotal(self, delta: int):
        self._status.thingIndexCompilerQueueProcessedTotal += delta
        self._notify()

    def setCompilerError(self, error: str):
        self._status.thingIndexCompilerQueueLastError = error
        self._notify()

    # ---------------
    # Notify Methods

    def _notify(self):
        self._tupleObserver.notifyOfTupleUpdate(
            TupleSelector(ThingIndexServerStatusTuple.tupleType(), {})
        )
