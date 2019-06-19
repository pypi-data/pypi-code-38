import logging
import typing
from datetime import datetime
from typing import List

import pytz
import ujson as json
from peek_plugin_base.worker import CeleryDbConn
from peek_plugin_diagram._private.storage.Display import DispBase
from peek_plugin_diagram._private.storage.GridKeyIndex import GridKeyCompilerQueue, \
    GridKeyIndex
from peek_plugin_diagram._private.tuples.branch.BranchTuple import \
    BranchTuple
from peek_plugin_diagram._private.worker.tasks.DispCompilerTask import _packDispJson
from sqlalchemy import select
from vortex.Tuple import Tuple

logger = logging.getLogger(__name__)


def _deleteBranchDisps(conn, branchIds: List[int]) -> None:
    """ Queue Grids for Removed Branch Disps

    This method queues grids for compile that contain disps that are removed.

    NOTE: The branches will be removed by a cascading constraint, we only have
    to queue the grids for recompile.

    """
    if not branchIds:
        return

    for branchId in branchIds:
        if branchId is None:
            raise Exception("BranchID is None, it shouldn't be")

    dispBaseTable = DispBase.__table__
    gridKeyIndexTable = GridKeyIndex.__table__

    queueTable = GridKeyCompilerQueue.__table__

    results = conn.execute(
        select(distinct=True,
               columns=[gridKeyIndexTable.c.gridKey, gridKeyIndexTable.c.coordSetId],
               whereclause=dispBaseTable.c.branchId.in_(branchIds))
            .select_from(gridKeyIndexTable.join(dispBaseTable))
    ).fetchall()

    if results:
        conn.execute(
            queueTable.insert(),
            [dict(coordSetId=item.coordSetId, gridKey=item.gridKey) for item in results]
        )

    # Delete existing Disps
    logger.info("Deleting disps with branchId %s" % branchIds)
    conn.execute(
        dispBaseTable.delete(dispBaseTable.c.branchId.in_(branchIds))
    )


def _convertBranchDisps(newBranches: List[BranchTuple]) -> typing.Tuple[List, List]:
    """ Insert Disps for Branch

    1) Insert new Disps
    2) Queue disps for recompile

    """
    startTime = datetime.now(pytz.utc)
    # Create state arrays
    newDisps = []
    dispIdsToCompile = []

    # Convert the branch disps into database disps
    for newBranch in newBranches:

        branchDisps = _convertJsonDispsToTuples(newBranch)

        if not branchDisps:
            continue

        # Create the map from the UI temp ID to the DB ID
        oldDispIdMap = {}

        # Set the IDs of the new Disps
        newIdGen = CeleryDbConn.prefetchDeclarativeIds(DispBase, len(branchDisps))
        for disp in branchDisps:
            oldDispId = disp.id
            disp.id = next(newIdGen)
            oldDispIdMap[oldDispId] = disp.id
            dispIdsToCompile.append(disp.id)

            newDisps.append(disp)

        # Update the group IDs
        for disp in branchDisps:
            if disp.groupId in oldDispIdMap:
                disp.groupId = oldDispIdMap[disp.groupId]

        # Recreate the branch disp json as per the structure from the DispBase tables
        # Just to be clear, this is converting it one way and then converting it back.
        # It ensures the data is consistent. (Which it should be if all was right)
        # It also sets the "hashId"

        # Create the map from the UI temp ID to the DB ID
        oldDispHashIdMap = {}
        newBranchDispItems = []

        newBranch.disps = []
        for disp in branchDisps:
            oldDispHashId = disp.hashId
            # This assigns the hashId to the jsonDict and disp
            newJsonDict = _packDispJson(disp, disp.tupleToSmallJsonDict())
            newBranch.disps.append(newJsonDict)

            oldDispHashIdMap[oldDispHashId] = disp.hashId
            newBranchDispItems.append((disp, newJsonDict))

        for disp, jsonDict in newBranchDispItems:
            if disp.replacesHashId in oldDispHashIdMap:
                disp.replacesHashId = oldDispHashIdMap.get(disp.replacesHashId)
                jsonDict['rid'] = disp.replacesHashId

            disp.dispJson = json.dumps(jsonDict)

            # AFTER the json has been dumped to the disp, convert it for storage
            # in the branch as geom JSON is not stored as a string in the branch
            # Because it's stored in the Disp Tuple/Table "geom" field as a string
            if 'g' in jsonDict:
                jsonDict['g'] = json.loads(jsonDict['g'])

        del newBranchDispItems

    logger.debug("Converted %s disps for %s branches in %s",
                 len(newDisps), len(newBranches),
                 (datetime.now(pytz.utc) - startTime))

    return newDisps, dispIdsToCompile

    # TODO: Something with the LiveDB links


def _convertJsonDispsToTuples(branchTuple: BranchTuple) -> List:
    """ Convert Json Disps to Tuples

     """
    disps: List = []
    for jsonDisp in branchTuple.disps:
        disp = Tuple.smallJsonDictToTuple(jsonDisp)
        disp.coordSetId = branchTuple.coordSetId
        disp.branchId = branchTuple.id
        if hasattr(disp, "geomJson"):
            disp.geomJson = json.dumps(disp.geomJson)
        disps.append(disp)
    return disps
