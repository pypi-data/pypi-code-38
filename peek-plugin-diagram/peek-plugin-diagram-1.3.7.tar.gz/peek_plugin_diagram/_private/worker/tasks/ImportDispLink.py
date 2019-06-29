import ujson as json
import logging
from datetime import datetime
from typing import List, Dict

import pytz
from peek_plugin_base.storage.DbConnection import pgCopyInsert

from peek_plugin_base.worker import CeleryDbConn
from peek_plugin_base.worker.CeleryDbConn import prefetchDeclarativeIds
from peek_plugin_diagram._private.storage.LiveDbDispLink import LiveDbDispLink, \
    LIVE_DB_KEY_DATA_TYPE_BY_DISP_ATTR
from peek_plugin_diagram._private.storage.ModelSet import ModelCoordSet
from peek_plugin_diagram.tuples.model.ImportLiveDbDispLinkTuple import \
    ImportLiveDbDispLinkTuple
from peek_plugin_livedb.tuples.ImportLiveDbItemTuple import ImportLiveDbItemTuple

logger = logging.getLogger(__name__)


def importDispLinks(coordSet: ModelCoordSet,
                    importGroupHash: str,
                    importDispLinks: List[ImportLiveDbDispLinkTuple]
                    ) -> List[ImportLiveDbItemTuple]:
    """ Import Disps Links

    1) Drop all disps with matching importGroupHash

    2) set the  coordSetId

    :param coordSet:
    :param importGroupHash:
    :param importDispLinks: An array of import LiveDB Disp Links to import
    :return:
    """
    dispLinkTable = LiveDbDispLink.__table__
    dispLinkIdIterator = prefetchDeclarativeIds(LiveDbDispLink, len(importDispLinks))

    startTime = datetime.now(pytz.utc)

    ormSession = CeleryDbConn.getDbSession()
    try:

        ormSession.execute(dispLinkTable
                           .delete()
                           .where(dispLinkTable.c.importGroupHash == importGroupHash))

        if not importDispLinks:
            return []

        liveDbItemsToImportByKey = {}

        dispLinkInserts = []

        for importDispLink in importDispLinks:
            dispLink = _convertImportDispLinkTuple(coordSet, importDispLink)
            dispLink.id = next(dispLinkIdIterator)

            liveDbItem = _makeImportLiveDbItem(
                importDispLink, liveDbItemsToImportByKey
            )

            dispLink.liveDbKey = liveDbItem.key
            dispLinkInserts.append(dispLink.tupleToSqlaBulkInsertDict())

        # if dispLinkInserts:
        #     ormSession.execute(LiveDbDispLink.__table__.insert(), dispLinkInserts)

        ormSession.commit()

        if dispLinkInserts:
            # This commits it's self
            rawConn = CeleryDbConn.getDbEngine().raw_connection()
            pgCopyInsert(rawConn, LiveDbDispLink.__table__, dispLinkInserts)
            rawConn.commit()

        logger.info(
            "Inserted %s LiveDbDispLinks in %s",
            len(dispLinkInserts), (datetime.now(pytz.utc) - startTime)
        )

        return list(liveDbItemsToImportByKey.values())

    finally:
        ormSession.close()


def _convertImportDispLinkTuple(coordSet: ModelCoordSet,
                                importDispLink: ImportLiveDbDispLinkTuple
                                ) -> LiveDbDispLink:
    return LiveDbDispLink(
        dispId=importDispLink.internalDispId,  # Dynamically added in DispImportController
        coordSetId=coordSet.id,
        dispAttrName=importDispLink.dispAttrName,
        liveDbKey=importDispLink.liveDbKey,
        importGroupHash=importDispLink.importGroupHash,
        propsJson=json.dumps(importDispLink.props)
    )


def _makeImportLiveDbItem(importDispLink: ImportLiveDbDispLinkTuple,
                          liveDbItemsToImportByKey: Dict):
    if importDispLink.liveDbKey in liveDbItemsToImportByKey:
        return liveDbItemsToImportByKey[importDispLink.liveDbKey]

    dataType = LIVE_DB_KEY_DATA_TYPE_BY_DISP_ATTR[importDispLink.dispAttrName]

    # These are not defined on the tuple, they are added in DispImportController
    rawValue = importDispLink.internalRawValue
    displayValue = importDispLink.internalDisplayValue

    newLiveDbKey = ImportLiveDbItemTuple(dataType=dataType,
                                         rawValue=rawValue,
                                         displayValue=displayValue,
                                         key=importDispLink.liveDbKey)

    liveDbItemsToImportByKey[importDispLink.liveDbKey] = newLiveDbKey

    return newLiveDbKey
