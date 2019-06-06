import logging
from typing import Optional, List

from sqlalchemy.sql.functions import func

from peek_server.storage.PeekPluginInfo import PeekPluginInfo

logger = logging.getLogger(__name__)


def getLatestPluginVersionInfos(name: Optional[str] = None) -> List[PeekPluginInfo]:
    """ Get Latest Plugin Version Infos

    This method returns the newest c{PeekPluginInfo} object for each plugin we have
    data for.

    :param name: Optionally, the name of the plugin to get the newest info for.
    :return: An array of c{PeekPluginInfo} objects
    """
    from peek_server.storage import dbConn
    session = dbConn.ormSessionCreator()

    maxGroupedIds = (session
                     .query(func.max(PeekPluginInfo.id).label('maxId'))
                     .group_by(PeekPluginInfo.name)
                     .subquery('maxGroupedIds'))

    qry = (session
           .query(PeekPluginInfo)
           .filter(PeekPluginInfo.id == maxGroupedIds.c.maxId)
           .order_by(PeekPluginInfo.name, PeekPluginInfo.id)
           )

    if name:
        qry = qry.filter(PeekPluginInfo.name == name)

    tuples: List[PeekPluginInfo] = []

    try:
        tuples = qry.all()
        session.expunge_all()

    except Exception as e:
        logger.info("There are no plugin updates")
        # logger.exception(e)

    finally:
        session.close()

    return tuples
