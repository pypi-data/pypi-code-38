import logging
from typing import Union

from sqlalchemy.orm import subqueryload
from twisted.internet.defer import Deferred

from peek_plugin_inbox._private.storage.Task import Task
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class TaskTupleProvider(TuplesProviderABC):
    def __init__(self, ormSessionCreator):
        self._ormSessionCreator = ormSessionCreator

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        userId = tupleSelector.selector["userId"]

        session = self._ormSessionCreator()
        try:
            tasks = (
                session.query(Task)
                    .filter(Task.userId == userId)
                    .options(subqueryload(Task.actions))
                    .all()
            )

            session.expunge_all()

            # Remove the data we don't want in the UI
            for task in tasks:
                task.onDeliveredPayloadEnvelope = None
                task.onCompletedPayloadEnvelope = None
                task.onDeletedPayloadEnvelope = None
                task.onDialogConfirmPayloadEnvelope = None
                for action in task.actions:
                    action.onActionPayloadEnvelope = None

            # Create the vortex message
            msg = Payload(filt, tuples=tasks).makePayloadEnvelope().toVortexMsg()


        finally:
            session.close()

        return msg
