import logging
from datetime import datetime
from typing import List

import pytz
from sqlalchemy import asc
from twisted.internet import task
from twisted.internet.defer import inlineCallbacks

from peek_core_search._private.server.client_handlers.ClientSearchObjectChunkUpdateHandler import \
    ClientSearchObjectChunkUpdateHandler
from peek_core_search._private.server.controller.StatusController import \
    StatusController
from peek_core_search._private.storage.SearchObjectCompilerQueue import \
    SearchObjectCompilerQueue
from vortex.DeferUtil import deferToThreadWrapWithLogger, vortexLogFailure

logger = logging.getLogger(__name__)


class SearchObjectChunkCompilerQueueController:
    """ SearchChunkCompilerQueueController

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
                 statusController: StatusController,
                 clientSearchObjectUpdateHandler: ClientSearchObjectChunkUpdateHandler):
        self._dbSessionCreator = dbSessionCreator
        self._statusController: StatusController = statusController
        self._clientSearchObjectUpdateHandler: ClientSearchObjectChunkUpdateHandler = clientSearchObjectUpdateHandler

        self._pollLoopingCall = task.LoopingCall(self._poll)
        self._lastQueueId = -1
        self._queueCount = 0

    def start(self):
        self._statusController.setSearchObjectCompilerStatus(True, self._queueCount)
        d = self._pollLoopingCall.start(self.PERIOD, now=False)
        d.addCallbacks(self._timerCallback, self._timerErrback)

    def _timerErrback(self, failure):
        vortexLogFailure(failure, logger)
        self._statusController.setSearchObjectCompilerStatus(False, self._queueCount)
        self._statusController.setSearchObjectCompilerError(str(failure.value))

    def _timerCallback(self, _):
        self._statusController.setSearchObjectCompilerStatus(False, self._queueCount)

    def stop(self):
        if self._pollLoopingCall.running:
            self._pollLoopingCall.stop()

    def shutdown(self):
        self.stop()

    @inlineCallbacks
    def _poll(self):
        from peek_core_search._private.worker.tasks.SearchObjectChunkCompilerTask import \
            compileSearchObjectChunk

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

        searchIndexChunkKeys = set()
        for i in queueItems:
            if i.chunkKey in searchIndexChunkKeys:
                queueIdsToDelete.append(i.id)
            else:
                searchIndexChunkKeys.add(i.chunkKey)

        if queueIdsToDelete:
            # Delete the duplicates and requery for our new list
            yield self._deleteDuplicateQueueItems(queueIdsToDelete)
            queueItems = yield self._grabQueueChunk()

        # Send the tasks to the peek worker
        for start in range(0, len(queueItems), self.FETCH_SIZE):

            items = queueItems[start: start + self.FETCH_SIZE]

            # Set the watermark
            self._lastQueueId = items[-1].id

            d = compileSearchObjectChunk.delay(items)
            d.addCallback(self._pollCallback, datetime.now(pytz.utc), len(items))
            d.addErrback(self._pollErrback, datetime.now(pytz.utc))

            self._queueCount += 1
            if self._queueCount >= self.QUEUE_MAX:
                break

    @deferToThreadWrapWithLogger(logger)
    def _grabQueueChunk(self):
        session = self._dbSessionCreator()
        try:
            qry = (session.query(SearchObjectCompilerQueue)
                .order_by(asc(SearchObjectCompilerQueue.id))
                .filter(SearchObjectCompilerQueue.id > self._lastQueueId)
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
        table = SearchObjectCompilerQueue.__table__
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
        self._clientSearchObjectUpdateHandler.sendChunks(chunkKeys)
        self._statusController.addToSearchObjectCompilerTotal(processedCount)
        self._statusController.setSearchObjectCompilerStatus(True, self._queueCount)

    def _pollErrback(self, failure, startTime):
        self._queueCount -= 1
        self._statusController.setSearchObjectCompilerError(str(failure.value))
        self._statusController.setSearchObjectCompilerStatus(True, self._queueCount)
        logger.debug("Time Taken = %s" % (datetime.now(pytz.utc) - startTime))
        vortexLogFailure(failure, logger)

