import logging
from collections import namedtuple
from datetime import datetime
from typing import List, Set, Tuple

import pytz
from sqlalchemy import select, and_

from peek_plugin_base.worker import CeleryDbConn
from peek_plugin_graphdb._private.storage.ItemKeyIndex import \
    ItemKeyIndex
from peek_plugin_graphdb._private.storage.ItemKeyIndexCompilerQueue import \
    ItemKeyIndexCompilerQueue
from peek_plugin_graphdb._private.worker.tasks._ItemKeyIndexCalcChunkKey import \
    makeChunkKeyForItemKey

logger = logging.getLogger(__name__)

ItemKeyImportTuple = namedtuple(
    "ItemKeyImportTuple",
    ["importGroupHash", "itemKey", "itemType", "segmentKey"]
)


def loadItemKeys(conn,
                 newItemKeys: List[ItemKeyImportTuple],
                 modelSetId: int, modelSetKey: str) -> None:
    """ Insert or Update Objects

    1) Find objects and update them
    2) Insert object if the are missing

    """

    itemKeyIndexTable = ItemKeyIndex.__table__
    queueTable = ItemKeyIndexCompilerQueue.__table__

    startTime = datetime.now(pytz.utc)

    importHashSet = set()

    chunkKeysForQueue: Set[Tuple[int, str]] = set()

    # Get the IDs that we need
    newIdGen = CeleryDbConn.prefetchDeclarativeIds(ItemKeyIndex, len(newItemKeys))

    # Create state arrays
    inserts = []

    # Work out which objects have been updated or need inserting
    for importItemKey in newItemKeys:
        importHashSet.add(importItemKey.importGroupHash)

        # Work out if we need to update the object type

        id_ = next(newIdGen)
        insertObject = ItemKeyIndex(
            id=id_,
            modelSetId=modelSetId,
            importGroupHash=importItemKey.importGroupHash,
            itemType=importItemKey.itemType,
            itemKey=importItemKey.itemKey,
            segmentKey=importItemKey.segmentKey,
            chunkKey=makeChunkKeyForItemKey(modelSetKey, importItemKey.itemKey)
        )
        inserts.append(insertObject.tupleToSqlaBulkInsertDict())

        chunkKeysForQueue.add((modelSetId, insertObject.chunkKey))

    if importHashSet:
        conn.execute(
            itemKeyIndexTable
                .delete(itemKeyIndexTable.c.importGroupHash.in_(importHashSet))
        )

    # Insert the ItemKeyIndex Objects
    if inserts:
        conn.execute(itemKeyIndexTable.insert(), inserts)

    if chunkKeysForQueue:
        conn.execute(
            queueTable.insert(),
            [dict(modelSetId=m, chunkKey=c) for m, c in chunkKeysForQueue]
        )

    logger.debug("Inserted %s ItemKeys queued %s chunks in %s",
                 len(inserts), len(chunkKeysForQueue),
                 (datetime.now(pytz.utc) - startTime))


def deleteItemKeys(conn, modelSetId: int, importGroupHashes: List[str]) -> None:
    startTime = datetime.now(pytz.utc)

    itemKeyIndexTable = ItemKeyIndex.__table__
    queueTable = ItemKeyIndexCompilerQueue.__table__

    chunkKeys = conn.execute(
        select([itemKeyIndexTable.c.modelSetId, itemKeyIndexTable.c.chunkKey],
               and_(itemKeyIndexTable.c.importGroupHash.in_(importGroupHashes),
                    itemKeyIndexTable.c.modelSetId == modelSetId))
    ).fetchall()

    if not chunkKeys:
        return

    conn.execute(
        itemKeyIndexTable.delete(
            and_(itemKeyIndexTable.c.importGroupHash.in_(importGroupHashes),
                 itemKeyIndexTable.c.modelSetId == modelSetId)
        )
    )

    conn.execute(queueTable.insert(), chunkKeys)

    logger.debug("Deleted %s, queued %s chunks in %s",
                 len(importGroupHashes), len(chunkKeys),
                 (datetime.now(pytz.utc) - startTime))
