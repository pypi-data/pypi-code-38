import logging
import pytz
from datetime import datetime
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from vortex.TupleAction import TupleActionABC
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleActionProcessor import TupleActionProcessorDelegateABC
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_plugin_diagram._private.tuples.DiagramImporterStatusTuple import \
    DiagramImporterStatusTuple

logger = logging.getLogger(__name__)


class StatusController(TupleActionProcessorDelegateABC):
    NOTIFY_PERIOD = 2.0

    def __init__(self):
        self._status = DiagramImporterStatusTuple()
        self._tupleObservable = None
        self._notifyPending = False
        self._lastNotifyDatetime = datetime.now(pytz.utc)

    def setTupleObservable(self, tupleObserver: TupleDataObservableHandler):
        self._tupleObserver = tupleObserver

    def shutdown(self):
        self._tupleObserver = None

    def processTupleAction(self, tupleAction: TupleActionABC) -> Deferred:
        # if isinstance(tupleAction, AddIntValueActionTuple):
        #     return self._processAddIntValue(tupleAction)

        raise NotImplementedError(tupleAction.tupleName())

    @property
    def status(self):
        return self._status

    # ---------------
    # Display Compiler Methods

    def setDisplayCompilerStatus(self, state: bool, queueSize: int):
        self._status.displayCompilerQueueStatus = state
        self._status.displayCompilerQueueSize = queueSize
        self._notify()

    def addToDisplayCompilerTotal(self, delta: int):
        self._status.displayCompilerProcessedTotal += delta
        self._notify()

    def setDisplayCompilerError(self, error: str):
        self._status.displayCompilerLastError = error
        self._notify()

    # ---------------
    # Grid Compiler Methods

    def setGridCompilerStatus(self, state: bool, queueSize: int):
        self._status.gridCompilerQueueStatus = state
        self._status.gridCompilerQueueSize = queueSize
        self._notify()

    def addToGridCompilerTotal(self, delta: int):
        self._status.gridCompilerProcessedTotal += delta
        self._notify()

    def setGridCompilerError(self, error: str):
        self._status.gridCompilerLastError = error
        self._notify()

    # ---------------
    # Disp Key Index Compiler Methods

    def setLocationIndexCompilerStatus(self, state: bool, queueSize: int):
        self._status.locationIndexCompilerQueueStatus = state
        self._status.locationIndexCompilerQueueSize = queueSize
        self._notify()

    def addToLocationIndexCompilerTotal(self, delta: int):
        self._status.locationIndexCompilerProcessedTotal += delta
        self._notify()

    def setLocationIndexCompilerError(self, error: str):
        self._status.locationIndexCompilerLastError = error
        self._notify()

    # ---------------
    # Disp Key Index Compiler Methods

    def setBranchIndexCompilerStatus(self, state: bool, queueSize: int):
        self._status.branchIndexCompilerQueueStatus = state
        self._status.branchIndexCompilerQueueSize = queueSize
        self._notify()

    def addToBranchIndexCompilerTotal(self, delta: int):
        self._status.branchIndexCompilerProcessedTotal += delta
        self._notify()

    def setBranchIndexCompilerError(self, error: str):
        self._status.branchIndexCompilerLastError = error
        self._notify()

    # ---------------
    # Notify Methods

    def _notify(self):
        if self._notifyPending:
            return

        self._notifyPending = True

        deltaSeconds = (datetime.now(pytz.utc) - self._lastNotifyDatetime).seconds
        if deltaSeconds >= self.NOTIFY_PERIOD:
            self._sendNotify()
        else:
            reactor.callLater(self.NOTIFY_PERIOD - deltaSeconds, self._sendNotify)

    def _sendNotify(self):
        self._notifyPending = False
        self._lastNotifyDatetime = datetime.now(pytz.utc)
        self._tupleObserver.notifyOfTupleUpdate(
            TupleSelector(DiagramImporterStatusTuple.tupleType(), {})
        )
