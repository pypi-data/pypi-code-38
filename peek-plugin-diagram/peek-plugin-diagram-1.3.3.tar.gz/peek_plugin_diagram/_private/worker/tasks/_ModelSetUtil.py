from collections import defaultdict

import logging
import typing
from sqlalchemy import select
from typing import List, Dict

from peek_plugin_base.worker import CeleryDbConn
from peek_plugin_diagram._private.storage.ModelSet import \
    ModelSet, ModelCoordSet

logger = logging.getLogger(__name__)

_modelSetTable = ModelSet.__table__
_coordSetTable = ModelCoordSet.__table__


def getModelSetIdCoordSetId(modelSetKeyCoordSetKey: List[typing.Tuple[str, str]]
                            ) -> Dict[typing.Tuple[str, str], typing.Tuple[int, int]]:
    """ Get Coord Set Ids

    Given a tuple of (ModelSet.key, CoordSet.key), return with that as the key
    and the CoordSet.id as the value

    """

    results: Dict[typing.Tuple[str, str], typing.Tuple[int, int]] = {}

    coordSetKeysByModelSetKey = defaultdict(list)
    for modelSetKey, coordSetKey in modelSetKeyCoordSetKey:
        coordSetKeysByModelSetKey[modelSetKey].append(coordSetKey)

    modelSetIdByKey = _loadModelSets()

    for modelSetKey, coordSetKeys in coordSetKeysByModelSetKey.items():
        modelSetId = modelSetIdByKey.get(modelSetKey)
        if modelSetId is None:
            modelSetId = _makeModelSet(modelSetKey)
            modelSetIdByKey[modelSetKey] = modelSetId

        coordSetIdByKey = _loadCoordSets(modelSetId)

        for coordSetKey in coordSetKeys:
            coordSetId = modelSetIdByKey.get(coordSetKey)
            if coordSetId is None:
                coordSetId = _makeCoordSet(modelSetId, coordSetKey)
                coordSetIdByKey[coordSetKey] = coordSetId

            results[(modelSetKey, coordSetKey)] = (modelSetId, coordSetId)

    return results


def _loadModelSets() -> Dict[str, int]:
    # Get the model set
    engine = CeleryDbConn.getDbEngine()
    conn = engine.connect()
    try:
        results = list(conn.execute(select(
            columns=[_modelSetTable.c.id, _modelSetTable.c.key]
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


def _loadCoordSets(modelSetId: int) -> Dict[str, int]:
    # Get the model set
    engine = CeleryDbConn.getDbEngine()
    conn = engine.connect()
    try:
        results = list(conn.execute(select(
            columns=[_coordSetTable.c.id, _coordSetTable.c.key],
            whereclause=_coordSetTable.c.modelSetId == modelSetId
        )))
        coordSetIdByKey = {o.key: o.id for o in results}
        del results

    finally:
        conn.close()

    return coordSetIdByKey


def _makeCoordSet(modelSetId: int, coordSetKey: str) -> int:
    # Make a coord set
    dbSession = CeleryDbConn.getDbSession()
    try:
        newItem = ModelCoordSet(modelSetId=modelSetId,
                                key=coordSetKey,
                                name=coordSetKey)
        dbSession.add(newItem)
        dbSession.commit()
        return newItem.id

    finally:
        dbSession.close()
