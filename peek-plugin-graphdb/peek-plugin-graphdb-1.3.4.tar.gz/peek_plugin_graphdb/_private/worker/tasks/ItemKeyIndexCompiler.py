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
from vortex.Payload import Payload

from peek_plugin_base.worker import CeleryDbConn
from peek_plugin_graphdb._private.storage.ItemKeyIndex import ItemKeyIndex
from peek_plugin_graphdb._private.storage.ItemKeyIndexCompilerQueue import \
    ItemKeyIndexCompilerQueue
from peek_plugin_graphdb._private.storage.ItemKeyIndexEncodedChunk import \
    ItemKeyIndexEncodedChunk
from peek_plugin_graphdb._private.worker.CeleryApp import celeryApp

logger = logging.getLogger(__name__)

""" ItemKeyIndex Index Compiler

Compile the graphdbindexes

1) Query for queue
2) Process queue
3) Delete from queue
"""


@DeferrableTask
@celeryApp.task(bind=True)
def compileItemKeyIndexChunk(self, queueItems) -> List[int]:
    """ Compile ItemKeyIndex Index Task

    :param queueItems: An encoded payload containing the queue tuples.
    :returns: A list of grid keys that have been updated.
    """
    try:
        queueItemsByModelSetId = defaultdict(list)

        for queueItem in queueItems:
            queueItemsByModelSetId[queueItem.modelSetId].append(queueItem)

        for modelSetId, modelSetQueueItems in queueItemsByModelSetId.items():
            _compileItemKeyIndexChunk(modelSetId, modelSetQueueItems)


    except Exception as e:
        logger.debug("RETRYING task - %s", e)
        raise self.retry(exc=e, countdown=1)

    return list(set([i.chunkKey for i in queueItems]))


def _compileItemKeyIndexChunk(modelSetId: int,
                              queueItems: List[ItemKeyIndexCompilerQueue]) -> None:
    chunkKeys = list(set([i.chunkKey for i in queueItems]))

    queueTable = ItemKeyIndexCompilerQueue.__table__
    compiledTable = ItemKeyIndexEncodedChunk.__table__
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
            newIdGen = CeleryDbConn.prefetchDeclarativeIds(ItemKeyIndex, len(inserts))
            for insert in inserts:
                insert["id"] = next(newIdGen)

        transaction.commit()
        transaction = conn.begin()

        if inserts:
            conn.execute(compiledTable.insert(), inserts)

        logger.debug("Compiled %s ItemKeyIndexs, %s missing, in %s",
                     len(inserts),
                     len(chunkKeys) - len(inserts), (datetime.now(pytz.utc) - startTime))

        total += len(inserts)

        queueItemIds = [o.id for o in queueItems]
        conn.execute(queueTable.delete(queueTable.c.id.in_(queueItemIds)))

        transaction.commit()
        logger.debug("Compiled and Committed %s EncodedItemKeyIndexChunks in %s",
                     total, (datetime.now(pytz.utc) - startTime))


    except Exception:
        transaction.rollback()
        raise

    finally:
        conn.close()


def _loadExistingHashes(conn, chunkKeys: List[str]) -> Dict[str, str]:
    compiledTable = ItemKeyIndexEncodedChunk.__table__

    results = conn.execute(select(
        columns=[compiledTable.c.chunkKey, compiledTable.c.encodedHash],
        whereclause=compiledTable.c.chunkKey.in_(chunkKeys)
    )).fetchall()

    return {result[0]: result[1] for result in results}


def _buildIndex(chunkKeys) -> Dict[str, bytes]:
    session = CeleryDbConn.getDbSession()

    try:
        indexQry = (
            session.query(ItemKeyIndex.chunkKey, ItemKeyIndex.itemKey,
                          ItemKeyIndex.itemKey,
                          # ItemKeyIndex.itemType,
                          ItemKeyIndex.segmentKey)
                .filter(ItemKeyIndex.chunkKey.in_(chunkKeys))
                .order_by(ItemKeyIndex.itemKey, ItemKeyIndex.segmentKey)
                .yield_per(1000)
                .all()
        )

        # Create the ChunkKey -> {id -> packedJson, id -> packedJson, ....]
        packagedJsonByObjIdByChunkKey = defaultdict(lambda: defaultdict(list))

        for item in indexQry:
            (
                packagedJsonByObjIdByChunkKey[item.chunkKey][item.itemKey]
                    .append(item.segmentKey)
            )


        encPayloadByChunkKey = {}

        # Sort each bucket by the key
        for chunkKey, segmentKeysByItemKey in packagedJsonByObjIdByChunkKey.items():
            # Convert the list to a json string, this reduces the memory footprint when
            # searching the index.
            packedJsonByKey = {
                itemKey: json.dumps(segmentKeys)
                for itemKey, segmentKeys in segmentKeysByItemKey.items()
            }

            tuples = json.dumps(packedJsonByKey, sort_keys=True)

            # Create the blob data for this index.
            # It could/will be found by a binary sort
            encPayloadByChunkKey[chunkKey] = Payload(tuples=tuples).toEncodedPayload()

        return encPayloadByChunkKey

    finally:
        session.close()
