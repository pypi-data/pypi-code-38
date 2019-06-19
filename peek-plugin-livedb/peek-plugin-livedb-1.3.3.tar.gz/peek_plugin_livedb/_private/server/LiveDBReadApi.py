import logging
from typing import List, Optional

from collections import defaultdict
from rx.subjects import Subject
from sqlalchemy import select
from twisted.internet.defer import Deferred

from peek_plugin_base.storage.StorageUtil import makeCoreValuesSubqueryCondition
from peek_plugin_livedb._private.server.controller.LiveDbController import \
    LiveDbController
from peek_plugin_livedb._private.storage.LiveDbItem import LiveDbItem
from peek_plugin_livedb._private.storage.LiveDbModelSet import getOrCreateLiveDbModelSet
from peek_plugin_livedb.server.LiveDBReadApiABC import LiveDBReadApiABC
from peek_plugin_livedb.tuples.LiveDbDisplayValueTuple import LiveDbDisplayValueTuple
from vortex.DeferUtil import deferToThreadWrapWithLogger

logger = logging.getLogger(__name__)


class LiveDBReadApi(LiveDBReadApiABC):
    def __init__(self, liveDbController: LiveDbController,
                 dbSessionCreator,
                 dbEngine):
        self._liveDbController = liveDbController
        self._dbSessionCreator = dbSessionCreator
        self._dbEngine = dbEngine

        self._prioritySubject = defaultdict(Subject)
        self._pollSubject = defaultdict(Subject)
        self._additionsSubject = defaultdict(Subject)
        self._deletionsSubject = defaultdict(Subject)
        self._rawValueUpdatesSubject = defaultdict(Subject)
        self._displayValueUpdatesSubject = defaultdict(Subject)

    def shutdown(self):
        pass

    def priorityKeysObservable(self, modelSetName: str) -> Subject:
        return self._prioritySubject[modelSetName]

    def pollKeysObservable(self, modelSetName: str) -> Subject:
        return self._pollSubject[modelSetName]

    def itemAdditionsObservable(self, modelSetName: str) -> Subject:
        return self._additionsSubject[modelSetName]

    def itemDeletionsObservable(self, modelSetName: str) -> Subject:
        return self._deletionsSubject[modelSetName]

    def bulkLoadDeferredGenerator(self, modelSetName: str,
                                  keyList: Optional[List[str]] = None,
                                  chunkSize: int = 2500) -> Deferred:
        offset = 0
        limit = chunkSize
        while True:
            yield qryChunk(modelSetName, offset, limit, keyList, self._dbSessionCreator)
            offset += limit

    def rawValueUpdatesObservable(self, modelSetName: str) -> Subject:
        return self._rawValueUpdatesSubject[modelSetName]

    def displayValueUpdatesObservable(self, modelSetName: str) -> Subject:
        return self._displayValueUpdatesSubject[modelSetName]


@deferToThreadWrapWithLogger(logger)
def qryChunk(modelSetName: str, offset: int, limit: int, keyList: List[str],
             dbSessionCreator) -> List[LiveDbDisplayValueTuple]:
    # If they've given us an empty key list, that is what they will get back
    if keyList is not None and not keyList:
        return []

    table = LiveDbItem.__table__
    cols = [table.c.key, table.c.dataType, table.c.rawValue, table.c.displayValue]

    session = dbSessionCreator()
    try:
        liveDbModelSet = getOrCreateLiveDbModelSet(session, modelSetName)

        stmt = (select(cols)
                .order_by(table.c.id)
                .where(table.c.modelSetId == liveDbModelSet.id))

        if keyList is not None:
            stmt = stmt.where(makeCoreValuesSubqueryCondition(
                session.bind, table.c.key, keyList
            ))

        stmt = stmt.offset(offset).limit(limit)

        result = session.execute(stmt)

        return [LiveDbDisplayValueTuple(
            key=o.key, dataType=o.dataType,
            rawValue=o.rawValue, displayValue=o.displayValue) for o in result.fetchall()]


    finally:
        session.close()
