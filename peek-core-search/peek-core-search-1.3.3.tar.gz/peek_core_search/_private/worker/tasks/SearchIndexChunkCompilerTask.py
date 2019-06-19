import hashlib
import json
import logging
from _collections import defaultdict
from base64 import b64encode
from datetime import datetime
from functools import cmp_to_key
from typing import List, Dict

import pytz
from sqlalchemy import select
from txcelery.defer import DeferrableTask

from peek_plugin_base.worker import CeleryDbConn
from peek_core_search._private.storage.EncodedSearchIndexChunk import \
    EncodedSearchIndexChunk
from peek_core_search._private.storage.SearchIndex import SearchIndex
from peek_core_search._private.storage.SearchIndexCompilerQueue import \
    SearchIndexCompilerQueue
from peek_core_search._private.worker.CeleryApp import celeryApp
from vortex.Payload import Payload

logger = logging.getLogger(__name__)

""" Search Index Compiler

Compile the search indexes

1) Query for queue
2) Process queue
3) Delete from queue
"""


@DeferrableTask
@celeryApp.task(bind=True)
def compileSearchIndexChunk(self, queueItems) -> List[str]:
    """ Compile Search Index Task

    :param self: A celery reference to this task
    :param queueItems: An encoded payload containing the queue tuples.
    :returns: A list of grid keys that have been updated.
    """
    chunkKeys = list(set([i.chunkKey for i in queueItems]))

    queueTable = SearchIndexCompilerQueue.__table__
    compiledTable = EncodedSearchIndexChunk.__table__
    lastUpdate = datetime.now(pytz.utc).isoformat()

    startTime = datetime.now(pytz.utc)

    engine = CeleryDbConn.getDbEngine()
    conn = engine.connect()
    transaction = conn.begin()
    try:

        logger.debug("Staring compile of %s queueItems in %s",
                     len(queueItems), (datetime.now(pytz.utc) - startTime))

        # Get Model Sets

        total = 0
        existingHashes = _loadExistingHashes(conn, chunkKeys)
        encKwPayloadByChunkKey = _buildIndex(conn, chunkKeys)
        chunksToDelete = []

        inserts = []
        for chunkKey, searchIndexChunkEncodedPayload in encKwPayloadByChunkKey.items():
            m = hashlib.sha256()
            m.update(searchIndexChunkEncodedPayload)
            encodedHash = b64encode(m.digest()).decode()

            # Compare the hash, AND delete the chunk key
            if chunkKey in existingHashes:
                # At this point we could decide to do an update instead,
                # but inserts are quicker
                if encodedHash == existingHashes.pop(chunkKey):
                    continue

            chunksToDelete.append(chunkKey)
            inserts.append(dict(
                chunkKey=chunkKey,
                encodedData=searchIndexChunkEncodedPayload,
                encodedHash=encodedHash,
                lastUpdate=lastUpdate))

        # Add any chnuks that we need to delete that we don't have new data for, here
        chunksToDelete.extend(list(existingHashes))

        if chunksToDelete:
            # Delete the old chunks
            conn.execute(
                compiledTable.delete(compiledTable.c.chunkKey.in_(chunksToDelete))
            )

        if inserts:
            newIdGen = CeleryDbConn.prefetchDeclarativeIds(SearchIndex, len(inserts))
            for insert in inserts:
                insert["id"] = next(newIdGen)

        transaction.commit()
        transaction = conn.begin()

        if inserts:
            conn.execute(compiledTable.insert(), inserts)

        logger.debug("Compiled %s SearchIndexes, %s missing, in %s",
                     len(inserts),
                     len(chunkKeys) - len(inserts), (datetime.now(pytz.utc) - startTime))

        total += len(inserts)

        queueItemIds = [o.id for o in queueItems]
        conn.execute(queueTable.delete(queueTable.c.id.in_(queueItemIds)))

        transaction.commit()
        logger.debug("Compiled and Committed %s EncodedSearchIndexChunks in %s",
                     total, (datetime.now(pytz.utc) - startTime))

        return chunkKeys

    except Exception as e:
        transaction.rollback()
        # logger.warning(e)  # Just a warning, it will retry
        logger.exception(e)
        raise self.retry(exc=e, countdown=10)

    finally:
        conn.close()


def _loadExistingHashes(conn, chunkKeys: List[str]) -> Dict[str, str]:
    compiledTable = EncodedSearchIndexChunk.__table__

    results = conn.execute(select(
        columns=[compiledTable.c.chunkKey, compiledTable.c.encodedHash],
        whereclause=compiledTable.c.chunkKey.in_(chunkKeys)
    )).fetchall()

    return {result[0]: result[1] for result in results}


def _buildIndex(conn, chunkKeys) -> Dict[str, bytes]:
    indexTable = SearchIndex.__table__

    results = conn.execute(select(
        columns=[indexTable.c.chunkKey, indexTable.c.keyword,
                 indexTable.c.propertyName, indexTable.c.objectId],
        whereclause=indexTable.c.chunkKey.in_(chunkKeys)
    ))

    encKwPayloadByChunkKey = {}

    # Create the SearchTerm -> SearchProperty -> [objectIds, objectIds, ....] structure
    objIdsByPropByKwByChunkKey = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )

    for item in results:
        (
            objIdsByPropByKwByChunkKey
            [item.chunkKey]
            [item.keyword]
            [item.propertyName]
                .append(item.objectId)
        )

    def _sortSearchIndex(o1, o2):
        if o1[0] < o2[0]: return -1
        if o1[0] > o2[0]: return 1
        if o1[1] < o2[1]: return -1
        if o1[1] > o2[1]: return 1
        return 0

    # Sort each bucket by the key
    for chunkKey, objIdsByPropByKw in objIdsByPropByKwByChunkKey.items():
        compileSearchIndexChunks = []

        for keyword, objIdsByProp in objIdsByPropByKw.items():
            for propertyName, objectIds in objIdsByProp.items():
                compileSearchIndexChunks.append(
                    [keyword, propertyName, json.dumps(list(sorted(objectIds)))]
                )

        compileSearchIndexChunks.sort(key=cmp_to_key(_sortSearchIndex))

        # Create the blob data for this index.
        # It will be searched by a binary sort
        encKwPayloadByChunkKey[chunkKey] = Payload(
            tuples=compileSearchIndexChunks).toEncodedPayload()

    return encKwPayloadByChunkKey
