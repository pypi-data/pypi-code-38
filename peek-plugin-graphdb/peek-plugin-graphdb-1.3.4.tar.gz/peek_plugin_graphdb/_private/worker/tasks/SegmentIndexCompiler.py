import hashlib
import json
import logging
from base64 import b64encode
from collections import defaultdict
from datetime import datetime
from typing import List, Dict

import pytz
from sqlalchemy import select
from txcelery.defer import DeferrableTask

from peek_plugin_base.worker import CeleryDbConn
from peek_plugin_graphdb._private.storage.GraphDbCompilerQueue import \
    GraphDbCompilerQueue
from peek_plugin_graphdb._private.storage.GraphDbSegment import GraphDbSegment
from peek_plugin_graphdb._private.storage.GraphDbEncodedChunk import \
    GraphDbEncodedChunk
from peek_plugin_graphdb._private.worker.CeleryApp import celeryApp
from vortex.Payload import Payload

logger = logging.getLogger(__name__)

""" GraphDb Index Compiler

Compile the graphDb indexes

1) Query for queue
2) Process queue
3) Delete from queue
"""


@DeferrableTask
@celeryApp.task(bind=True)
def compileSegmentChunk(self, queueItems) -> List[int]:
    """ Compile GraphDb Index Task

    :param queueItems: An encoded payload containing the queue tuples.
    :returns: A list of grid keys that have been updated.
    """
    try:
        queueItemsByModelSetId = defaultdict(list)

        for queueItem in queueItems:
            queueItemsByModelSetId[queueItem.modelSetId].append(queueItem)

        for modelSetId, modelSetQueueItems in queueItemsByModelSetId.items():
            _compileSegmentChunk(modelSetId, modelSetQueueItems)


    except Exception as e:
        logger.debug("RETRYING task - %s", e)
        raise self.retry(exc=e, countdown=1)

    return list(set([i.chunkKey for i in queueItems]))


def _compileSegmentChunk(modelSetId: int,
                          queueItems: List[GraphDbCompilerQueue]) -> None:
    chunkKeys = list(set([i.chunkKey for i in queueItems]))

    queueTable = GraphDbCompilerQueue.__table__
    compiledTable = GraphDbEncodedChunk.__table__
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
        encKwPayloadByChunkKey = _buildIndex(chunkKeys)
        chunksToDelete = []

        inserts = []
        for chunkKey, graphDbIndexChunkEncodedPayload in encKwPayloadByChunkKey.items():
            m = hashlib.sha256()
            m.update(graphDbIndexChunkEncodedPayload)
            encodedHash = b64encode(m.digest()).decode()

            # Compare the hash, AND delete the chunk key
            if chunkKey in existingHashes:
                # At this point we could decide to do an update instead,
                # but inserts are quicker
                if encodedHash == existingHashes.pop(chunkKey):
                    continue

            chunksToDelete.append(chunkKey)
            inserts.append(dict(
                modelSetId=modelSetId,
                chunkKey=chunkKey,
                encodedData=graphDbIndexChunkEncodedPayload,
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
            newIdGen = CeleryDbConn.prefetchDeclarativeIds(GraphDbSegment, len(inserts))
            for insert in inserts:
                insert["id"] = next(newIdGen)

        transaction.commit()
        transaction = conn.begin()

        if inserts:
            conn.execute(compiledTable.insert(), inserts)

        logger.debug("Compiled %s Segments, %s missing, in %s",
                     len(inserts),
                     len(chunkKeys) - len(inserts), (datetime.now(pytz.utc) - startTime))

        total += len(inserts)

        queueItemIds = [o.id for o in queueItems]
        conn.execute(queueTable.delete(queueTable.c.id.in_(queueItemIds)))

        transaction.commit()
        logger.debug("Compiled and Committed %s EncodedSegmentChunks in %s",
                     total, (datetime.now(pytz.utc) - startTime))


    except Exception:
        transaction.rollback()
        raise

    finally:
        conn.close()


def _loadExistingHashes(conn, chunkKeys: List[str]) -> Dict[str, str]:
    compiledTable = GraphDbEncodedChunk.__table__

    results = conn.execute(select(
        columns=[compiledTable.c.chunkKey, compiledTable.c.encodedHash],
        whereclause=compiledTable.c.chunkKey.in_(chunkKeys)
    )).fetchall()

    return {result[0]: result[1] for result in results}


def _buildIndex(chunkKeys) -> Dict[str, bytes]:
    session = CeleryDbConn.getDbSession()

    try:
        indexQry = (
            session.query(GraphDbSegment.chunkKey, GraphDbSegment.key,
                          GraphDbSegment.segmentJson)
                .filter(GraphDbSegment.chunkKey.in_(chunkKeys))
                .order_by(GraphDbSegment.key)
                .yield_per(1000)
                .all()
        )

        # Create the ChunkKey -> {id -> packedJson, id -> packedJson, ....]
        packagedJsonByObjIdByChunkKey = defaultdict(dict)

        for item in indexQry:
            packagedJsonByObjIdByChunkKey[item.chunkKey][item.key] = item.segmentJson

        encPayloadByChunkKey = {}

        # Sort each bucket by the key
        for chunkKey, packedJsonByKey in packagedJsonByObjIdByChunkKey.items():
            tuples = json.dumps(packedJsonByKey, sort_keys=True)

            # Create the blob data for this index.
            # It will be graphDbed by a binary sort
            encPayloadByChunkKey[chunkKey] = Payload(tuples=tuples).toEncodedPayload()

        return encPayloadByChunkKey

    finally:
        session.close()
