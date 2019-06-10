import logging
from datetime import datetime
from typing import List

import pytz
from sqlalchemy import asc
from twisted.internet import task
from twisted.internet.defer import inlineCallbacks

from peek_plugin_index_blueprint._private.server.client_handlers.ThingIndexChunkUpdateHandler import \
    ThingIndexChunkUpdateHandler
from peek_plugin_index_blueprint._private.server.controller.ThingIndexStatusController import \
    ThingIndexStatusController
from peek_plugin_index_blueprint._private.storage.ThingIndexCompilerQueue import ThingIndexCompilerQueue
from vortex.DeferUtil import deferToThreadWrapWithLogger, vortexLogFailure

logger = logging.getLogger(__name__)


class ThingIndexCompilerController:
    """ ThingIndexChunkCompilerQueueController

    Compile the disp items into the grid data

    1) Query for queue
    2) Process queue
    3) Delete from queue

    """

    FETCH_SIZE = 10
    PERIOD = 1.000

    QUEUE_MAX = 20
    QUEUE_MIN = 0

    def __init__(self, dbSessionCreator,
                 statusController: ThingIndexStatusController,
                 clientUpdateHandler: ThingIndexChunkUpdateHandler):
        self._dbSessionCreator = dbSessionCreator
        self._statusController: ThingIndexStatusController = statusController
        self._clientUpdateHandler: ThingIndexChunkUpdateHandler = clientUpdateHandler

        self._pollLoopingCall = task.LoopingCall(self._poll)
        self._lastQueueId = -1
        self._queueCount = 0

    def start(self):
        self._statusController.setCompilerStatus(True, self._queueCount)
        d = self._pollLoopingCall.start(self.PERIOD, now=False)
        d.addCallbacks(self._timerCallback, self._timerErrback)

    def _timerErrback(self, failure):
        vortexLogFailure(failure, logger)
        self._statusController.setCompilerStatus(False, self._queueCount)
        self._statusController.setCompilerError(str(failure.value))

    def _timerCallback(self, _):
        self._statusController.setCompilerStatus(False, self._queueCount)

    def stop(self):
        self._pollLoopingCall.stop()

    def shutdown(self):
        self.stop()

    @inlineCallbacks
    def _poll(self):
        from peek_plugin_index_blueprint._private.worker.tasks.ThingIndexCompiler import \
            compileThingIndexChunk

        # We queue the grids in bursts, reducing the work we have to do.
        if self._queueCount > self.QUEUE_MIN:
            return

        # Check for queued items
        queueItems = yield self._grabQueueChunk()
        if not queueItems:
            return

        # De duplicated queued grid keys
        # This is the reason why we don't just queue all the celery tasks in one go.
        # If we keep them in the DB queue, we can remove the duplicates
        # and there are lots of them
        queueIdsToDelete = []

        indexBlueprintIndexChunkKeys = set()
        for i in queueItems:
            if i.chunkKey in indexBlueprintIndexChunkKeys:
                queueIdsToDelete.append(i.id)
            else:
                indexBlueprintIndexChunkKeys.add(i.chunkKey)

        if queueIdsToDelete:
            # Delete the duplicates and requery for our new list
            yield self._deleteDuplicateQueueItems(queueIdsToDelete)
            queueItems = yield self._grabQueueChunk()

        # Send the tasks to the peek worker
        for start in range(0, len(queueItems), self.FETCH_SIZE):

            items = queueItems[start: start + self.FETCH_SIZE]

            # Set the watermark
            self._lastQueueId = items[-1].id

            d = compileThingIndexChunk.delay(items)
            d.addCallback(self._pollCallback, datetime.now(pytz.utc), len(items))
            d.addErrback(self._pollErrback, datetime.now(pytz.utc))

            self._queueCount += 1
            if self._queueCount >= self.QUEUE_MAX:
                break

    @deferToThreadWrapWithLogger(logger)
    def _grabQueueChunk(self):
        session = self._dbSessionCreator()
        try:
            qry = (session.query(ThingIndexCompilerQueue)
                   .order_by(asc(ThingIndexCompilerQueue.id))
                   .filter(ThingIndexCompilerQueue.id > self._lastQueueId)
                   .yield_per(500)
                   # .limit(self.FETCH_SIZE)
                   )

            queueItems = qry.all()
            session.expunge_all()

            return queueItems

        finally:
            session.close()

    @deferToThreadWrapWithLogger(logger)
    def _deleteDuplicateQueueItems(self, itemIds):
        session = self._dbSessionCreator()
        table = ThingIndexCompilerQueue.__table__
        try:
            SIZE = 1000
            for start in range(0, len(itemIds), SIZE):
                chunkIds = itemIds[start: start + SIZE]

                session.execute(table.delete(table.c.id.in_(chunkIds)))

            session.commit()
        finally:
            session.close()

    def _pollCallback(self, chunkKeys: List[str], startTime, processedCount):
        self._queueCount -= 1
        logger.debug("Time Taken = %s" % (datetime.now(pytz.utc) - startTime))
        self._clientUpdateHandler.sendChunks(chunkKeys)
        self._statusController.addToCompilerTotal(processedCount)
        self._statusController.setCompilerStatus(True, self._queueCount)

    def _pollErrback(self, failure, startTime):
        self._queueCount -= 1
        self._statusController.setCompilerError(str(failure.value))
        self._statusController.setCompilerStatus(True, self._queueCount)
        logger.debug("Time Taken = %s" % (datetime.now(pytz.utc) - startTime))
        vortexLogFailure(failure, logger)
