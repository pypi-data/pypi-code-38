import hashlib
import logging
from base64 import b64encode
from collections import defaultdict
from datetime import datetime
from typing import List, Dict

import pytz
import ujson as json
from sqlalchemy import select
from txcelery.defer import DeferrableTask
from vortex.Payload import Payload

from peek_plugin_base.worker import CeleryDbConn
from peek_plugin_diagram._private.storage.branch.BranchIndex import BranchIndex
from peek_plugin_diagram._private.storage.branch.BranchIndexCompilerQueue import \
    BranchIndexCompilerQueue
from peek_plugin_diagram._private.storage.branch.BranchIndexEncodedChunk import \
    BranchIndexEncodedChunk
from peek_plugin_diagram._private.worker.CeleryApp import celeryApp

logger = logging.getLogger(__name__)

""" BranchIndex Index Compiler

Compile the index-blueprintindexes

1) Query for queue
2) Process queue
3) Delete from queue
"""


@DeferrableTask
@celeryApp.task(bind=True)
def compileBranchIndexChunk(self, queueItems) -> List[int]:
    """ Compile BranchIndex Index Task

    :param self: A bound parameter from celery
    :param queueItems: An encoded payload containing the queue tuples.
    :returns: A list of grid keys that have been updated.
    """
    try:
        queueItemsByModelSetId = defaultdict(list)

        for queueItem in queueItems:
            queueItemsByModelSetId[queueItem.modelSetId].append(queueItem)

        for modelSetId, modelSetQueueItems in queueItemsByModelSetId.items():
            _compileBranchIndexChunk(modelSetId, modelSetQueueItems)


    except Exception as e:
        logger.debug("RETRYING task - %s", e)
        logger.exception(e)
        raise self.retry(exc=e, countdown=2)

    return list(set([i.chunkKey for i in queueItems]))


def _compileBranchIndexChunk(modelSetId: int,
                             queueItems: List[BranchIndexCompilerQueue]) -> None:
    chunkKeys = list(set([i.chunkKey for i in queueItems]))

    queueTable = BranchIndexCompilerQueue.__table__
    compiledTable = BranchIndexEncodedChunk.__table__
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
        for chunkKey, diagramIndexChunkEncodedPayload in encKwPayloadByChunkKey.items():
            m = hashlib.sha256()
            m.update(diagramIndexChunkEncodedPayload)
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
                encodedData=diagramIndexChunkEncodedPayload,
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
            newIdGen = CeleryDbConn.prefetchDeclarativeIds(BranchIndex, len(inserts))
            for insert in inserts:
                insert["id"] = next(newIdGen)

        transaction.commit()
        transaction = conn.begin()

        if inserts:
            conn.execute(compiledTable.insert(), inserts)

        logger.debug("Compiled %s BranchIndexs, %s missing, in %s",
                     len(inserts),
                     len(chunkKeys) - len(inserts), (datetime.now(pytz.utc) - startTime))

        total += len(inserts)

        queueItemIds = [o.id for o in queueItems]
        conn.execute(queueTable.delete(queueTable.c.id.in_(queueItemIds)))

        transaction.commit()
        logger.debug("Compiled and Committed %s EncodedBranchIndexChunks in %s",
                     total, (datetime.now(pytz.utc) - startTime))


    except Exception:
        transaction.rollback()
        raise

    finally:
        conn.close()


def _loadExistingHashes(conn, chunkKeys: List[str]) -> Dict[str, str]:
    compiledTable = BranchIndexEncodedChunk.__table__

    results = conn.execute(select(
        columns=[compiledTable.c.chunkKey, compiledTable.c.encodedHash],
        whereclause=compiledTable.c.chunkKey.in_(chunkKeys)
    )).fetchall()

    return {result[0]: result[1] for result in results}


def _buildIndex(chunkKeys) -> Dict[str, bytes]:
    session = CeleryDbConn.getDbSession()

    try:
        indexQry = (
            session.query(BranchIndex.chunkKey, BranchIndex.key,
                          BranchIndex.packedJson)
                .filter(BranchIndex.chunkKey.in_(chunkKeys))
                .order_by(BranchIndex.key)
                .yield_per(1000)
                .all()
        )

        # Create the ChunkKey -> {key -> packedJson, key -> packedJson, ....]
        packagedJsonsByObjKeyByChunkKey = defaultdict(lambda: defaultdict(list))

        for item in indexQry:
            packagedJsonsByObjKeyByChunkKey[item.chunkKey][item.key].append(item.packedJson)

        encPayloadByChunkKey = {}

        # Sort each bucket by the key
        for chunkKey, packedJsonsByKey in packagedJsonsByObjKeyByChunkKey.items():
            tuples = json.dumps(packedJsonsByKey, sort_keys=True)

            # Create the blob data for this index.
            # It will be index-blueprint by a binary sort
            encPayloadByChunkKey[chunkKey] = Payload(tuples=tuples).toEncodedPayload()

        return encPayloadByChunkKey

    finally:
        session.close()
