import logging
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Set, Tuple

import pytz
from peek_plugin_base.worker import CeleryDbConn
from sqlalchemy import select, bindparam, and_
from txcelery.defer import DeferrableTask
from vortex.Payload import Payload

from peek_plugin_index_blueprint._private.storage.ModelSet import \
    ModelSet
from peek_plugin_index_blueprint._private.storage.ThingIndex import \
    ThingIndex
from peek_plugin_index_blueprint._private.storage.ThingIndexCompilerQueue import \
    ThingIndexCompilerQueue
from peek_plugin_index_blueprint._private.storage.ThingType import \
    ThingType
from peek_plugin_index_blueprint._private.worker.CeleryApp import celeryApp
from peek_plugin_index_blueprint._private.worker.tasks._ThingIndexCalcChunkKey import \
    makeChunkKey
from peek_plugin_index_blueprint.tuples.ThingImportTuple import ThingImportTuple
from peek_plugin_index_blueprint.tuples.ThingTuple import ThingTuple

logger = logging.getLogger(__name__)


@DeferrableTask
@celeryApp.task(bind=True)
def createOrUpdateThings(self, thingsEncodedPayload: bytes) -> None:
    # Decode arguments
    newThings: List[ThingImportTuple] = (
        Payload().fromEncodedPayload(thingsEncodedPayload).tuples
    )

    _validateNewThingIndexs(newThings)

    modelSetIdByKey = _loadModelSets()

    # Do the import
    try:

        thingIndexByModelKey = defaultdict(list)
        for thingIndex in newThings:
            thingIndexByModelKey[thingIndex.modelSetKey].append(thingIndex)

        for modelSetKey, thingIndexs in thingIndexByModelKey.items():
            modelSetId = modelSetIdByKey.get(modelSetKey)
            if modelSetId is None:
                modelSetId = _makeModelSet(modelSetKey)
                modelSetIdByKey[modelSetKey] = modelSetId

            thingTypeIdsByName = _prepareLookups(thingIndexs, modelSetId)
            _insertOrUpdateObjects(thingIndexs, modelSetId, thingTypeIdsByName)

    except Exception as e:
        logger.debug("Retrying import index-blueprintobjects, %s", e)
        raise self.retry(exc=e, countdown=3)


def _validateNewThingIndexs(newThings: List[ThingImportTuple]) -> None:
    for thingIndex in newThings:
        if not thingIndex.key:
            raise Exception("key is empty for %s" % thingIndex)

        if not thingIndex.modelSetKey:
            raise Exception("modelSetKey is empty for %s" % thingIndex)

        if not thingIndex.thingTypeKey:
            raise Exception("thingTypeKey is empty for %s" % thingIndex)

        # if not thingIndex.thingIndex:
        #     raise Exception("thingIndex is empty for %s" % thingIndex)


def _loadModelSets() -> Dict[str, int]:
    # Get the model set
    engine = CeleryDbConn.getDbEngine()
    conn = engine.connect()
    try:
        modelSetTable = ModelSet.__table__
        results = list(conn.execute(select(
            columns=[modelSetTable.c.id, modelSetTable.c.key]
        )))
        modelSetIdByKey = {o.key: o.id for o in results}
        del results

    finally:
        conn.close()
    return modelSetIdByKey


def _makeModelSet(modelSetKey: str) -> int:
    # Get the model set
    dbSession = CeleryDbConn.getDbSession()
    try:
        newItem = ModelSet(key=modelSetKey, name=modelSetKey)
        dbSession.add(newItem)
        dbSession.commit()
        return newItem.id

    finally:
        dbSession.close()


def _prepareLookups(newThings: List[ThingImportTuple], modelSetId: int
                    ) -> Dict[str, int]:
    """ Check Or Insert Things

    """

    dbSession = CeleryDbConn.getDbSession()

    startTime = datetime.now(pytz.utc)

    try:

        thingTypeKeys = set()

        for o in newThings:
            o.thingTypeKey = o.thingTypeKey.lower()
            thingTypeKeys.add(o.thingTypeKey)

        # Prepare Object Types
        thingTypes = (
            dbSession.query(ThingType)
                .filter(ThingType.modelSetId == modelSetId)
                .all()
        )
        thingTypeKeys -= set([o.key for o in thingTypes])

        if not thingTypeKeys:
            thingTypeIdsByKey = {o.key: o.id for o in thingTypes}

        else:
            for newType in thingTypeKeys:
                dbSession.add(ThingType(
                    key=newType, name=newType, modelSetId=modelSetId
                ))

            dbSession.commit()

            thingTypes = dbSession.query(ThingType).all()
            thingTypeIdsByKey = {o.key: o.id for o in thingTypes}

        logger.debug("Prepared lookups in %s", (datetime.now(pytz.utc) - startTime))

        return thingTypeIdsByKey

    except Exception as e:
        dbSession.rollback()
        raise

    finally:
        dbSession.close()


def _insertOrUpdateObjects(newThings: List[ThingImportTuple],
                           modelSetId: int,
                           thingTypeIdsByName: Dict[str, int]) -> None:
    """ Insert or Update Objects

    1) Find objects and update them
    2) Insert object if the are missing

    """

    thingIndexTable = ThingIndex.__table__
    queueTable = ThingIndexCompilerQueue.__table__

    startTime = datetime.now(pytz.utc)

    engine = CeleryDbConn.getDbEngine()
    conn = engine.connect()
    transaction = conn.begin()

    try:
        importHashSet = set()
        dontDeleteObjectIds = []
        objectIdByKey: Dict[str, int] = {}

        objectKeys = [o.key for o in newThings]
        chunkKeysForQueue: Set[Tuple[int, str]] = set()

        # Query existing objects
        results = list(conn.execute(select(
            columns=[thingIndexTable.c.id, thingIndexTable.c.key,
                     thingIndexTable.c.chunkKey, thingIndexTable.c.packedJson],
            whereclause=and_(thingIndexTable.c.key.in_(objectKeys),
                             thingIndexTable.c.modelSetId == modelSetId)
        )))

        foundObjectByKey = {o.key: o for o in results}
        del results

        # Get the IDs that we need
        newIdGen = CeleryDbConn.prefetchDeclarativeIds(
            ThingIndex, len(newThings) - len(foundObjectByKey)
        )

        # Create state arrays
        inserts = []
        updates = []

        # Work out which objects have been updated or need inserting
        for thingImportTuple in newThings:
            importHashSet.add(thingImportTuple.importGroupHash)

            existingObject = foundObjectByKey.get(thingImportTuple.key)
            importThingTypeId = thingTypeIdsByName[
                thingImportTuple.thingTypeKey]

            packedJson = ThingTuple.packJson(thingImportTuple,
                                             modelSetId, importThingTypeId)

            # Work out if we need to update the object type
            if existingObject:
                updates.append(
                    dict(b_id=existingObject.id,
                         b_typeId=importThingTypeId,
                         b_packedJson=packedJson)
                )
                dontDeleteObjectIds.append(existingObject.id)

            else:
                id_ = next(newIdGen)
                existingObject = ThingIndex(
                    id=id_,
                    modelSetId=modelSetId,
                    thingTypeId=importThingTypeId,
                    key=thingImportTuple.key,
                    importGroupHash=thingImportTuple.importGroupHash,
                    chunkKey=makeChunkKey(thingImportTuple.modelSetKey,
                                          thingImportTuple.key),
                    packedJson=packedJson
                )
                inserts.append(existingObject.tupleToSqlaBulkInsertDict())

            objectIdByKey[existingObject.key] = existingObject.id
            chunkKeysForQueue.add((modelSetId, existingObject.chunkKey))

        if importHashSet:
            conn.execute(
                thingIndexTable
                    .delete(and_(~thingIndexTable.c.id.in_(dontDeleteObjectIds),
                                 thingIndexTable.c.importGroupHash.in_(importHashSet)))
            )

        # Insert the ThingIndex Objects
        if inserts:
            conn.execute(thingIndexTable.insert(), inserts)

        if updates:
            stmt = (
                thingIndexTable.update()
                    .where(thingIndexTable.c.id == bindparam('b_id'))
                    .values(thingTypeId=bindparam('b_typeId'),
                            packedJson=bindparam('b_packedJson'))
            )
            conn.execute(stmt, updates)

        if chunkKeysForQueue:
            conn.execute(
                queueTable.insert(),
                [dict(modelSetId=m, chunkKey=c) for m, c in chunkKeysForQueue]
            )

        if inserts or updates or chunkKeysForQueue:
            transaction.commit()
        else:
            transaction.rollback()

        logger.debug("Inserted %s updated %s queued %s chunks in %s",
                     len(inserts), len(updates), len(chunkKeysForQueue),
                     (datetime.now(pytz.utc) - startTime))

    except Exception:
        transaction.rollback()
        raise

    finally:
        conn.close()
