import logging
from typing import List

from sqlalchemy import select
from txcelery.defer import DeferrableTask

from peek_plugin_base.worker import CeleryDbConn
from peek_plugin_livedb._private.storage.LiveDbItem import LiveDbItem
from peek_plugin_livedb._private.worker.CeleryApp import celeryApp
from peek_plugin_livedb.tuples.LiveDbDisplayValueTuple import LiveDbDisplayValueTuple

logger = logging.getLogger(__name__)


@DeferrableTask
@celeryApp.task(bind=True)
def qryChunkInWorker(self, offset, limit) -> List[LiveDbDisplayValueTuple]:
    """ Query Chunk

    This returns a chunk of LiveDB items from the database

    :param self: A celery reference to this task
    :param offset: The offset of the chunk
    :param limit: An encoded payload containing the updates
    :returns: List[LiveDbDisplayValueTuple] serialised in a payload json
    """

    table = LiveDbItem.__table__
    cols = [table.c.key, table.c.dataType, table.c.rawValue, table.c.displayValue]

    session = CeleryDbConn.getDbSession()
    try:
        result = session.execute(select(cols)
                                 .order_by(table.c.id)
                                 .offset(offset)
                                 .limit(limit))

        return [LiveDbDisplayValueTuple(
            key=o.key, dataType=o.dataType,
            rawValue=o.rawValue, displayValue=o.displayValue) for o in result.fetchall()]

    finally:
        session.close()
