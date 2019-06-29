import logging

from twisted.internet.defer import Deferred

from peek_plugin_gis_diagram._private.storage.StringIntTuple import StringIntTuple
from peek_plugin_gis_diagram._private.tuples.AddIntValueActionTuple import \
    AddIntValueActionTuple
from peek_plugin_gis_diagram._private.tuples.StringCapToggleActionTuple import \
    StringCapToggleActionTuple
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.TupleAction import TupleActionABC
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleActionProcessor import TupleActionProcessorDelegateABC
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

logger = logging.getLogger(__name__)

class MainController(TupleActionProcessorDelegateABC):
    def __init__(self, dbSessionCreator, tupleObservable: TupleDataObservableHandler):
        self._dbSessionCreator = dbSessionCreator
        self._tupleObservable = tupleObservable

    def shutdown(self):
        pass

    def processTupleAction(self, tupleAction: TupleActionABC) -> Deferred:

        if isinstance(tupleAction, AddIntValueActionTuple):
            return self._processAddIntValue(tupleAction)

        if isinstance(tupleAction, StringCapToggleActionTuple):
            return self._processCapToggleString(tupleAction)

        raise NotImplementedError(tupleAction.tupleName())

    @deferToThreadWrapWithLogger(logger)
    def _processCapToggleString(self, action: StringCapToggleActionTuple):
        try:
            # Perform update using SQLALchemy
            session = self._dbSessionCreator()
            row = (session.query(StringIntTuple)
                   .filter(StringIntTuple.id == action.stringIntId)
                   .one())

            # Exit early if the string is empty
            if not row.string1:
                logger.debug("string1 for StringIntTuple.id=%s is empty")
                return

            if row.string1[0].isupper():
                row.string1 = row.string1.lower()
                logger.debug("Toggled to lower")
            else:
                row.string1 = row.string1.upper()
                logger.debug("Toggled to upper")

            session.commit()

            # Notify the observer of the update
            # This tuple selector must exactly match what the UI observes
            tupleSelector = TupleSelector(StringIntTuple.tupleName(), {})
            self._tupleObservable.notifyOfTupleUpdate(tupleSelector)

        finally:
            # Always close the session after we create it
            session.close()

    @deferToThreadWrapWithLogger(logger)
    def _processAddIntValue(self, action: AddIntValueActionTuple):
        try:
            # Perform update using SQLALchemy
            session = self._dbSessionCreator()
            row = (session.query(StringIntTuple)
                   .filter(StringIntTuple.id == action.stringIntId)
                   .one())
            row.int1 += action.offset
            session.commit()

            logger.debug("Int changed by %u", action.offset)

            # Notify the observer of the update
            # This tuple selector must exactly match what the UI observes
            tupleSelector = TupleSelector(StringIntTuple.tupleName(), {})
            self._tupleObservable.notifyOfTupleUpdate(tupleSelector)

        finally:
            # Always close the session after we create it
            session.close()

    def agentNotifiedOfUpdate(self, updateStr):
        logger.debug("Agent said : %s", updateStr)
