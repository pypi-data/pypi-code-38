import logging
from datetime import datetime
from typing import List

import pytz
from sqlalchemy.sql.expression import select
from txcelery.defer import DeferrableTask

from peek_plugin_base.storage.StorageUtil import makeCoreValuesSubqueryCondition
from peek_plugin_base.worker import CeleryDbConn
from peek_plugin_livedb._private.storage.LiveDbItem import LiveDbItem
from peek_plugin_livedb._private.storage.LiveDbModelSet import getOrCreateLiveDbModelSet
from peek_plugin_livedb._private.worker.CeleryApp import celeryApp
from peek_plugin_livedb.tuples.ImportLiveDbItemTuple import ImportLiveDbItemTuple

logger = logging.getLogger(__name__)


@DeferrableTask
@celeryApp.task(bind=True)
def importLiveDbItems(self, modelSetName: str,
                      newItems: List[ImportLiveDbItemTuple]) -> List[str]:
    """ Compile Grids Task

    :param self: A celery reference to this task
    :param modelSetName: The model set name
    :param newItems: The list of new items
    :returns: A list of grid keys that have been updated.
    """

    startTime = datetime.now(pytz.utc)

    session = CeleryDbConn.getDbSession()
    engine = CeleryDbConn.getDbEngine()
    conn = engine.connect()
    transaction = conn.begin()

    liveDbTable = LiveDbItem.__table__
    try:

        liveDbModelSet = getOrCreateLiveDbModelSet(session, modelSetName)

        # This will remove duplicates
        itemsByKey = {i.key: i for i in newItems}

        allKeys = list(itemsByKey)
        existingKeys = set()

        # Query for existing keys, in 1000 chinks
        chunkSize = 1000
        offset = 0
        while True:
            chunk = allKeys[offset:offset + chunkSize]
            if not chunk:
                break
            offset += chunkSize
            stmt = (select([liveDbTable.c.key])
                    .where(liveDbTable.c.modelSetId == liveDbModelSet.id)
            .where(makeCoreValuesSubqueryCondition(
                engine, liveDbTable.c.key, chunk
            ))
            )

            result = conn.execute(stmt)

            existingKeys.update([o[0] for o in result.fetchall()])

        inserts = []
        newKeys = []

        for newItem in itemsByKey.values():
            if newItem.key in existingKeys:
                continue

            inserts.append(dict(
                modelSetId=liveDbModelSet.id,
                key=newItem.key,
                dataType=newItem.dataType,
                rawValue=newItem.rawValue,
                displayValue=newItem.displayValue,
                importHash=newItem.importHash
            ))

            newKeys.append(newItem.key)

        if not inserts:
            return []

        conn.execute(LiveDbItem.__table__.insert(), inserts)

        transaction.commit()
        logger.info("Inserted %s LiveDbItems, %s already existed, in %s",
                    len(inserts), len(existingKeys), (datetime.now(pytz.utc) - startTime))

        return newKeys

    except Exception as e:
        transaction.rollback()
        logger.warning("Task failed, but it will retry. %s", e)
        raise self.retry(exc=e, countdown=10)

    finally:
        conn.close()
        session.close()
