import logging
import typing
from collections import defaultdict
from datetime import datetime
from typing import List, Dict

import pytz
from peek_plugin_base.worker import CeleryDbConn
from peek_plugin_diagram._private.server.controller.DispCompilerQueueController import \
    DispCompilerQueueController
from peek_plugin_diagram._private.tuples.branch.BranchTuple import BranchTuple
from peek_plugin_diagram._private.worker.CeleryApp import celeryApp
from peek_plugin_diagram._private.worker.tasks.ImportDispTask import _bulkInsertDisps
from peek_plugin_diagram._private.worker.tasks.LookupHashConverter import \
    LookupHashConverter
from peek_plugin_diagram._private.worker.tasks._ModelSetUtil import \
    getModelSetIdCoordSetId
from peek_plugin_diagram._private.worker.tasks.branch.BranchDispUpdater import \
    _convertBranchDisps
from peek_plugin_diagram._private.worker.tasks.branch.BranchIndexUpdater import \
    _insertOrUpdateBranches
from peek_plugin_diagram.tuples.branches.ImportBranchTuple import ImportBranchTuple
from txcelery.defer import DeferrableTask
from vortex.Payload import Payload

logger = logging.getLogger(__name__)


@DeferrableTask
@celeryApp.task(bind=True)
def createOrUpdateBranches(self, importBranchesEncodedPayload: bytes) -> None:
    """ Convert Import Branch Tuples

    This method takes import branch tuples, and converts them to
    branch format used throughout the diagram plugin.

    (Thats the packed JSON wrapped by an accessor class)

    """
    # Decode importBranches payload
    importBranches: List[ImportBranchTuple] = (
        Payload().fromEncodedPayload(importBranchesEncodedPayload).tuples
    )

    # Validate the input importBranches
    _validateNewBranchIndexs(importBranches)

    # Do the import
    groupedBranches = _convertImportBranchTuples(importBranches)

    startTime = datetime.now(pytz.utc)

    dbSession = CeleryDbConn.getDbSession()

    engine = CeleryDbConn.getDbEngine()
    conn = engine.connect()
    transaction = conn.begin()

    try:
        for (modelSetKey, modelSetId, coordSetId), branches in groupedBranches.items():
            _insertOrUpdateBranches(conn, modelSetKey, modelSetId, branches)

            newDisps, dispIdsToCompile = _convertBranchDisps(branches)

            # NO TRANSACTION
            # Bulk load the Disps
            _bulkInsertDisps(engine, newDisps)

            # Queue the compiler
            DispCompilerQueueController.queueDispIdsToCompileWithSession(
                dispIdsToCompile, conn
            )

            transaction.commit()
            dbSession.commit()

            logger.debug("Completed importing %s branches for coordSetId %s in %s",
                         len(branches),
                         coordSetId,
                         (datetime.now(pytz.utc) - startTime))

    except Exception as e:
        dbSession.rollback()
        transaction.rollback()
        logger.debug("Retrying createOrUpdateBranches, %s", e)
        logger.exception(e)
        raise self.retry(exc=e, countdown=3)

    finally:
        dbSession.close()
        conn.close()


def _convertImportBranchTuples(importBranches: List[ImportBranchTuple]
                               ) -> Dict[typing.Tuple[str, int, int], List[BranchTuple]]:
    """ Convert Import Branch Tuples

    This method takes import branch tuples, and converts them to
    branch format used throughout the diagram plugin.

    (Thats the packed JSON wrapped by an accessor class)

    """

    # Get a map for the coordSetIds
    modelKeyCoordKeyTuples = [(b.modelSetKey, b.coordSetKey) for b in importBranches]

    coordSetIdByModelKeyCoordKeyTuple = getModelSetIdCoordSetId(modelKeyCoordKeyTuples)

    # Sort out the importBranches by coordSetKey
    branchByModelKeyByCoordKey = defaultdict(lambda: defaultdict(list))
    for importBranch in importBranches:
        branchByModelKeyByCoordKey[importBranch.modelSetKey][importBranch.coordSetKey] \
            .append(importBranch)

    # Define the converted importBranches
    convertedBranchesByCoordSetId: Dict[typing.Tuple[str, int, int], List[BranchTuple]] \
        = {}

    # Get the model set
    dbSession = CeleryDbConn.getDbSession()
    try:
        # Iterate through the importBranches and convert them
        for modelSetKey, item in branchByModelKeyByCoordKey.items():
            for coordSetKey, importBranches in item:
                modelSetId, coordSetId = coordSetIdByModelKeyCoordKeyTuple[
                    (modelSetKey, coordSetKey)]

                lookupHashConverter = LookupHashConverter(
                    dbSession, modelSetId, coordSetId
                )

                convertedBranches = []
                for importBranch in importBranches:
                    branch = BranchTuple.loadFromImportTuple(
                        importBranch, coordSetId,
                        lookupHashConverter=lookupHashConverter
                    )
                    convertedBranches.append(branch)

                convertedBranchesByCoordSetId[(modelSetKey, modelSetId, coordSetId)] \
                    = convertedBranches

    finally:
        dbSession.close()

    return convertedBranchesByCoordSetId


def _validateNewBranchIndexs(newBranches: List[ImportBranchTuple]) -> None:
    for branchIndex in newBranches:
        if not branchIndex.key:
            raise Exception("key is empty for %s" % branchIndex)

        if not branchIndex.modelSetKey:
            raise Exception("modelSetKey is empty for %s" % branchIndex)

        if not branchIndex.coordSetKey:
            raise Exception("coordSetKey is empty for %s" % branchIndex)
