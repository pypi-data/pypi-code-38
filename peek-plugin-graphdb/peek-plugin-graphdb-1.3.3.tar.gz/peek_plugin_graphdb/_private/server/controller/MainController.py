import logging

from twisted.internet.defer import Deferred, inlineCallbacks
from vortex.TupleAction import TupleActionABC
from vortex.handler.TupleActionProcessor import TupleActionProcessorDelegateABC
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

logger = logging.getLogger(__name__)


class MainController(TupleActionProcessorDelegateABC):
    def __init__(self, dbSessionCreator, tupleObservable: TupleDataObservableHandler):
        self._dbSessionCreator = dbSessionCreator
        self._tupleObservable = tupleObservable
        self._readApi = None

        self._graphsByModelSetKey = {}

    @inlineCallbacks
    def start(self, readApi) -> Deferred:

        self._readApi = readApi

    def shutdown(self):
        self._readApi = False

    def processTupleAction(self, tupleAction: TupleActionABC) -> Deferred:
        raise NotImplementedError(tupleAction.tupleName())

