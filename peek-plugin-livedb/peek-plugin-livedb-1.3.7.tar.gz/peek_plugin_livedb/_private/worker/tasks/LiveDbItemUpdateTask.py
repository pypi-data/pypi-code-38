import logging
from datetime import datetime

import pytz
from collections import namedtuple
from sqlalchemy.sql.expression import bindparam, and_
from txcelery.defer import CeleryClient, DeferrableTask

from peek_plugin_base.worker import CeleryDbConn
from peek_plugin_livedb._private.storage.LiveDbItem import LiveDbItem
from peek_plugin_livedb._private.storage.LiveDbModelSet import getOrCreateLiveDbModelSet
from peek_plugin_livedb._private.worker.CeleryApp import celeryApp
from vortex.Payload import Payload

logger = logging.getLogger(__name__)


@DeferrableTask
@celeryApp.task(bind=True)
def updateValues(self, modelSetName, updates, raw=True):
    """ Compile Grids Task

    :param self: A celery reference to this task
    :param modelSetName: The model set name
    :param updates: An encoded payload containing the updates
    :param raw: Are the updates raw updates?
    :returns: A list of grid keys that have been updated.
    """

    startTime = datetime.now(pytz.utc)
    table = LiveDbItem.__table__

    session = CeleryDbConn.getDbSession()
    conn = CeleryDbConn.getDbEngine().connect()
    try:
        liveDbModelSet = getOrCreateLiveDbModelSet(session, modelSetName)

        sql = (table.update()
               .where(and_(table.c.key == bindparam('b_key'),
                           table.c.modelSetId == liveDbModelSet.id))
               .values({"rawValue" if raw else "displayValue": bindparam("b_value")}))

        conn.execute(sql, [
            dict(b_key=o.key, b_value=(o.rawValue if raw else o.displayValue))
            for o in updates])

        logger.debug("Updated %s %s values, in %s",
                     len(updates),
                     "raw" if raw else "display",
                     (datetime.now(pytz.utc) - startTime))

    except Exception as e:
        logger.exception(e)
        raise self.retry(exc=e, countdown=2)

    finally:
        session.close()
        conn.close()
