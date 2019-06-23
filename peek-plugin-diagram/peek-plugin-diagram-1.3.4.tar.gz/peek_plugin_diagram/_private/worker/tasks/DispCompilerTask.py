import logging
from _collections import defaultdict
from collections import namedtuple
from datetime import datetime
from typing import List, Dict

import pytz
import ujson as json
from peek_plugin_base.worker import CeleryDbConn
from peek_plugin_diagram._private.storage.Display import DispBase, DispTextStyle, \
    DispGroup, DispGroupPointer
from peek_plugin_diagram._private.storage.GridKeyIndex import GridKeyIndex, \
    DispIndexerQueue, GridKeyCompilerQueue
from peek_plugin_diagram._private.storage.LiveDbDispLink import LiveDbDispLink
from peek_plugin_diagram._private.storage.LocationIndex import LocationIndex, \
    LocationIndexCompilerQueue
from peek_plugin_diagram._private.storage.ModelSet import ModelCoordSet, \
    makeDispGroupGridKey
from peek_plugin_diagram._private.worker.CeleryApp import celeryApp
from peek_plugin_diagram._private.worker.tasks._CalcDisp import \
    _scaleDispGeomWithCoordSet, _scaleDispGeom, _createHashId
from peek_plugin_diagram._private.worker.tasks._CalcDispFromLiveDb import \
    _mergeInLiveDbValues
from peek_plugin_diagram._private.worker.tasks._CalcGridForDisp import makeGridKeysForDisp
from peek_plugin_diagram._private.worker.tasks._CalcLocation import makeLocationJson, \
    dispKeyHashBucket
from peek_plugin_livedb.worker.WorkerApi import WorkerApi
from sqlalchemy import select, join
from sqlalchemy.orm import subqueryload
from sqlalchemy.sql.selectable import Select
from txcelery.defer import DeferrableTask

logger = logging.getLogger(__name__)

CoordSetIdGridKeyData = namedtuple("CoordSetIdGridKeyTuple",
                                   ["coordSetId", "gridKey"])

ModelSetIdIndexBucketData = namedtuple("ModelSetIdIndexBucketTuple",
                                       ["modelSetId", "indexBucket"])

DispData = namedtuple('DispData', ['json', 'levelOrder', 'layerOrder'])

PreparedDisp = namedtuple('PreparedDisp', ['disp', 'geomArray', 'dispDict'])


@DeferrableTask
@celeryApp.task(bind=True)
def compileDisps(self, queueIds, dispIds):
    """ Compile Disps

    This function takes a list of Disp IDs and compiles them.
    The processing is as follows (more or less)

    0) Load lookups

    ----

    1) DispGroupPointers, copy disps from group to pointer

    ----

    2) Load the Disps from the DB

    3) Apply the LiveDB values to the Disp attributes

    4) Scale the Disp geomJson to match the coord set scaling

    5) DispGroups, take Disps as part of a disp group and load them into JSON in the
        DispGroup. PreparedDisp????

    6) Extract any new LocationIndex entries, of the Disp has a key

    7) Determine which grids this disp will live in, and create GridKeyIndex entries
        for those grid keys for this disp.

    8) Write the Disp JSON back to the disp

    ormSession.commit() here.
        This stores the following updates that have been made into the disp:
        * dispJson,
        * locationJson,
        * livedb attribute updates

    ----

    9) Write the calculated data to tables

    NOTE: Disps that belong to a DispGroup will not be queued for compile by
    ImportDispTask.

    """

    # ==========================
    # 0) Load the lookups
    ormSession = CeleryDbConn.getDbSession()
    try:
        # ---------------
        # Load Coord Sets
        coordSets = (ormSession.query(ModelCoordSet)
                     .options(subqueryload(ModelCoordSet.modelSet),
                              subqueryload(ModelCoordSet.gridSizes))
                     .all())

        # Get Model Set Name Map
        coordSetById = {o.id: o for o in coordSets}

        # ---------------
        # Load Coord Sets
        textStyleById = {ts.id: ts for ts in ormSession.query(DispTextStyle).all()}

        ormSession.expunge_all()

    except Exception as e:
        logger.exception(e)
        raise self.retry(exc=e, countdown=2)

    finally:
        ormSession.close()

    # ==========================
    # This method will create new disps that will be compiled later.
    try:

        # ---------------
        # 1) Clone the disps for the group instances
        dispIdsIncludingClones = _cloneDispsForDispGroupPointer(dispIds)

    except Exception as e:
        logger.exception(e)
        raise self.retry(exc=e, countdown=2)

    # ==========================
    # Run all the ORM Session update methods
    ormSession = CeleryDbConn.getDbSession()
    try:
        with ormSession.no_autoflush:
            # ---------------
            # 2) Apply the LiveDB Attribute updates
            disps = _loadDisps(ormSession, dispIdsIncludingClones)

            # ---------------
            # 3) Apply the LiveDB Attribute updates
            _applyLiveDbAttributes(ormSession, disps, coordSetById)

            # ---------------
            # 4) Scale the Disp geomJson to match the coord set scaling
            preparedDisps = _scaleDisp(disps, coordSetById)

            # 5) DispGroups, take Disps as part of a disp group and load them
            # into JSON in the DispGroup. PreparedDisp????
            _compileDispGroups(ormSession, preparedDisps)

            # ---------------
            # 6) Extract any new LocationIndex entries, of the Disp has a key
            locationCompiledQueueItems, locationIndexByDispId = _indexLocation(
                preparedDisps, coordSetById
            )

            # ---------------
            # 7) Determine which grids this disp will live in, and create GridKeyIndex
            # entries for those grid keys for this disp.
            gridCompiledQueueItems, gridKeyIndexesByDispId = _calculateGridKeys(
                preparedDisps, coordSetById, textStyleById
            )

            # ---------------
            # 8) Write the Disp JSON back to the disp
            _updateDispsJson(preparedDisps)

        # ---------------
        # Commit the updates
        startTime = datetime.now(pytz.utc)
        ormSession.commit()
        logger.debug("Committed %s disp objects in %s",
                     len(disps), (datetime.now(pytz.utc) - startTime))

    except Exception as e:
        ormSession.rollback()
        logger.exception(e)
        raise self.retry(exc=e, countdown=2)

    finally:
        ormSession.close()

    # ==========================
    # 9) Run the bulk DB delete/insert methods
    try:

        _insertToDb(dispIdsIncludingClones,
                    gridCompiledQueueItems, gridKeyIndexesByDispId,
                    locationCompiledQueueItems, locationIndexByDispId, queueIds)

    except Exception as e:
        logger.exception(e)
        raise self.retry(exc=e, countdown=2)

    logger.info("Compiled %s disp objects in %s",
                len(dispIds), (datetime.now(pytz.utc) - startTime))


def _queryDispsForGroup(ormSession, dispGroupIds) -> Dict[int, List]:
    qry = ormSession.query(DispBase) \
        .options(subqueryload(DispBase.liveDbLinks)) \
        .filter(DispBase.groupId.in_(dispGroupIds))

    dispsByGroupId = defaultdict(list)
    for o in qry.all():
        dispsByGroupId[o.groupId].append(o)

    return dispsByGroupId


def _cloneDispsForDispGroupPointer(dispIds: List[int]):
    """ Clone Disps for DispGroupPointer

    This method will clone "instances" of the disps in the disp groups for the
    DispGroupPointer.


    """
    startTime = datetime.now(pytz.utc)

    ormSession = CeleryDbConn.getDbSession()
    try:

        # -----
        # Load the disp group pointers
        qry = ormSession.query(DispGroupPointer) \
            .filter(DispGroupPointer.targetDispGroupId != None) \
            .filter(DispGroupPointer.id.in_(dispIds))

        dispGroupPointers: List[DispGroupPointer] = qry.all()

        # If there are no DispGroupPointers that need cloning, then return.
        if not dispGroupPointers:
            logger.debug("Cloning skipped,"
                         " there are no disp group ptrs with targets, in %s",
                         (datetime.now(pytz.utc) - startTime))
            return dispIds

        dispGroupPointerTargetIds = [o.targetDispGroupId for o in dispGroupPointers]

        del qry

        # -----
        # Delete any existing disps are in these pointers
        ormSession.query(DispBase) \
            .filter(DispBase.groupId.in_([o.id for o in dispGroupPointers])) \
            .delete(synchronize_session=False)

        ormSession.commit()

        # -----
        # Query for the disp groups we'll need
        dispGroupChildsByGroupId = _queryDispsForGroup(ormSession,
                                                       dispGroupPointerTargetIds)

        # -----
        # Query for the disp groups names
        dispBaseTable = DispBase.__table__
        dispGroupTable = DispGroup.__table__

        qry = ormSession.execute(
            select(columns=[dispBaseTable.c.id,
                            dispBaseTable.c.coordSetId,
                            dispGroupTable.c.name],
                   whereclause=dispBaseTable.c.id.in_(dispGroupPointerTargetIds))
                .select_from(join(dispGroupTable, dispBaseTable,
                                  dispGroupTable.c.id == dispBaseTable.c.id))
        )

        dispGroupNameByGroupId = {o.id: '%s|%s' % (o.coordSetId, o.name)
                                  for o in qry.fetchall()}

        del qry

        # -----
        # Clone the child disps
        cloneDisps = []
        cloneLiveDbDispLinks = []

        for dispPtr in dispGroupPointers:
            if not dispPtr.targetDispGroupId:
                logger.debug("Pointer has no targetGroupId id=%s", dispPtr.id)
                continue

            dispGroupChilds = dispGroupChildsByGroupId.get(dispPtr.targetDispGroupId)

            if not dispGroupChilds:
                logger.warning("Pointer points to missing DispGroup,"
                               " id=%s, targetGroupId=%s", dispPtr.id,
                               dispPtr.targetDispGroupId)
                continue

            x, y = json.loads(dispPtr.geomJson)
            dispPtr.targetDispGroupName = \
                dispGroupNameByGroupId[dispPtr.targetDispGroupId]

            for templateDisp in dispGroupChilds:
                # Create the clone
                cloneDisp = templateDisp.tupleClone()
                cloneDisps.append(cloneDisp)

                cloneDisp.coordSetId = dispPtr.coordSetId

                # Offset the geometry
                geom = json.loads(cloneDisp.geomJson)
                geom = _scaleDispGeom(geom, 1, 1, x, y)
                cloneDisp.geomJson = json.dumps(geom)

                # Assign the clone to the DispGroupPointer
                cloneDisp.groupId = dispPtr.id

                for dispLink in templateDisp.liveDbLinks:
                    cloneDispLink = dispLink.tupleClone()
                    cloneLiveDbDispLinks.append(cloneDispLink)

                    cloneDispLink.id = None
                    cloneDispLink.disp = cloneDisp
                    cloneDispLink.coordSetId = dispPtr.coordSetId

        # -----
        # Preallocate the IDs for performance on PostGreSQL
        dispIdGen = CeleryDbConn.prefetchDeclarativeIds(DispBase, len(cloneDisps))
        for cloneDisp in cloneDisps:
            cloneDisp.id = next(dispIdGen)

        # Preallocate the IDs for performance on PostGreSQL
        dispLinkIdGen = CeleryDbConn.prefetchDeclarativeIds(LiveDbDispLink,
                                                            len(cloneLiveDbDispLinks))
        for cloneDispLink in cloneLiveDbDispLinks:
            cloneDispLink.id = next(dispLinkIdGen)
            cloneDispLink.dispId = cloneDispLink.disp.id
            cloneDispLink.disp = None

        # -----
        # Create the new list of IDs to compile
        # Do this here, otherwise it will cause a DB refresh if it's after the commit.
        dispIdsIncludingClones = dispIds + [o.id for o in cloneDisps]

        ormSession.bulk_save_objects(cloneDisps, update_changed_only=False)
        ormSession.bulk_save_objects(cloneLiveDbDispLinks, update_changed_only=False)

        ormSession.commit()

        logger.debug("Cloned %s disp group objects in %s",
                     len(cloneDisps), (datetime.now(pytz.utc) - startTime))

    except Exception:
        ormSession.rollback()
        raise

    finally:
        ormSession.close()

    return dispIdsIncludingClones


def _loadDisps(ormSession, dispIdsIncludingClones: List[int]):
    """ Load Disps

    This method loads the disps from the database

    """
    startTime = datetime.now(pytz.utc)

    # -----
    # Begin the DISP merge from live data
    qry = (
        ormSession.query(DispBase)
            .options(subqueryload(DispBase.liveDbLinks),
                     subqueryload(DispBase.level))
            .filter(DispBase.id.in_(dispIdsIncludingClones))
    )

    allDisps = qry.all()

    logger.debug("Loaded %s disp objects in %s",
                 len(allDisps), (datetime.now(pytz.utc) - startTime))

    return allDisps


def _applyLiveDbAttributes(ormSession, disps, coordSetById):
    startTime = datetime.now(pytz.utc)

    # Prepare the LiveDbKeys
    liveDbKeysByModelSetKey = defaultdict(list)
    for disp in disps:
        # Add a reference to the model set name for convenience
        disp.modelSetKey = coordSetById[disp.coordSetId].modelSet.key
        liveDbKeysByModelSetKey[disp.modelSetKey].extend(
            [dl.liveDbKey for dl in disp.liveDbLinks]
        )

    liveDbItemByModelSetKeyByKey = {}
    for modelSetKey, liveDbKeys in liveDbKeysByModelSetKey.items():
        liveDbItemByModelSetKeyByKey[modelSetKey] = {
            i.key: i for i in
            WorkerApi.getLiveDbDisplayValues(ormSession, modelSetKey, liveDbKeys)
        }

    logger.debug("Loaded LiveDB Attributes for %s disp objects in %s",
                 len(disps), (datetime.now(pytz.utc) - startTime))

    for disp in disps:  # Work out which grids we belong to
        # Get the LiveDB Items for this model set
        liveDbItemByKey = liveDbItemByModelSetKeyByKey[disp.modelSetKey]

        # Apply live db attributes
        _mergeInLiveDbValues(disp, liveDbItemByKey)

    logger.debug("Applied LiveDB values to %s disp objects in %s",
                 len(disps), (datetime.now(pytz.utc) - startTime))


def _scaleDisp(disps, coordSetById):
    """ Scale Disps

    This method scales the display item geometry as per the coord set

    """

    startTime = datetime.now(pytz.utc)

    # inserts for GridKeyCompilerQueue
    preparedDisps: List[PreparedDisp] = []

    for disp in disps:
        # Get a reference to the coordSet
        coordSet = coordSetById[disp.coordSetId]

        # Create the JSON Dict
        dispDict = disp.tupleToSmallJsonDict()

        # Get and Scale the Geometry
        geomArray = None
        # Disp Groups have no geometry
        if not isinstance(disp, DispGroup):
            geomArray = json.loads(disp.geomJson)
            geomArray = _scaleDispGeomWithCoordSet(geomArray, coordSet)
            dispDict["g"] = geomArray

        preparedDisps.append(PreparedDisp(disp, geomArray, dispDict))

    logger.debug("Scaled %s disps in %s",
                 len(disps), (datetime.now(pytz.utc) - startTime))

    return preparedDisps


def _compileDispGroups(ormSession, preparedDisps: List[PreparedDisp]):
    """ Compile Disp Groups

    This method will pack the child disps into the disp groups dispJson field.

    """

    def packDisp(disp):
        """ Pack Disp

        """
        dispDict = disp.tupleToSmallJsonDict(includeFalse=False, includeNones=False)
        dispDict["g"] = json.loads(disp.geomJson)
        return dispDict

    startTime = datetime.now(pytz.utc)

    preparedDispGroupByIds: Dict[int, PreparedDisp] = {
        o.disp.id: o
        for o in preparedDisps
        if isinstance(o.disp, DispGroup)
    }

    # Query for the disp groups with loaded child disps we'll need

    childDispsByGroupId = _queryDispsForGroup(ormSession, preparedDispGroupByIds)

    childDispCount = 0

    for groupId in preparedDispGroupByIds:
        preparedDispGroup = preparedDispGroupByIds[groupId]
        childDisps = childDispsByGroupId[groupId]

        preparedDispGroup.dispDict['di'] = json.dumps([
            packDisp(disp) for disp in childDisps
        ])

        childDispCount += len(childDisps)

    logger.debug("Packed %s disps into %s group objects in %s",
                 childDispCount, len(preparedDispGroupByIds),
                 (datetime.now(pytz.utc) - startTime))


def _indexLocation(preparedDisps, coordSetById):
    """ Index Location

    This method extracts the location index data from the disps.

    """

    startTime = datetime.now(pytz.utc)

    # ---------------
    # inserts for GridKeyCompilerQueue
    locationCompiledQueueItems = set()

    # List of location index bucket to disp index items to insert into LocationIndex
    locationIndexByDispId = {}

    count = 0

    for pdisp in preparedDisps:
        if not pdisp.geomArray or not pdisp.disp.key:
            continue
        count += 1

        # Get a reference to the coordSet
        coordSet = coordSetById[pdisp.disp.coordSetId]

        # Create the location json for the LocationIndex
        pdisp.disp.locationJson = makeLocationJson(pdisp.disp, pdisp.geomArray)

        # Create the index bucket
        indexBucket = dispKeyHashBucket(coordSet.modelSet.name, pdisp.disp.key)

        # Create the compiler queue item
        locationCompiledQueueItems.add(
            ModelSetIdIndexBucketData(modelSetId=coordSet.modelSetId,
                                      indexBucket=indexBucket)
        )

        # Create the location index item
        locationIndexByDispId[pdisp.disp.id] = dict(
            indexBucket=indexBucket,
            dispId=pdisp.disp.id,
            modelSetId=coordSet.modelSetId
        )

    logger.debug("Indexed %s disp Locations in %s",
                 count, (datetime.now(pytz.utc) - startTime))

    return locationCompiledQueueItems, locationIndexByDispId


def _calculateGridKeys(preparedDisps: List[PreparedDisp], coordSetById, textStyleById):
    """ Calculate Grid Keys

    This method Determines which grids this disp will live in,
    and creates GridKeyIndex entries for those grid keys for this disp.

    """

    startTime = datetime.now(pytz.utc)

    # ---------------
    # inserts for GridKeyCompilerQueue
    gridCompiledQueueItems = set()

    # GridKeyIndexes to insert
    gridKeyIndexesByDispId = defaultdict(list)

    # Create a small piece of reusable code
    def addGridKey(disp, gridKey):
        # Create the compiler queue item
        gridCompiledQueueItems.add(
            CoordSetIdGridKeyData(coordSetId=disp.coordSetId,
                                  gridKey=gridKey)
        )

        # Create the grid key index item
        gridKeyIndexesByDispId[disp.id].append(
            dict(dispId=disp.id,
                 coordSetId=disp.coordSetId,
                 gridKey=gridKey,
                 importGroupHash=disp.importGroupHash))

    for pdisp in preparedDisps:
        # Get a reference to the coordSet
        coordSet = coordSetById[pdisp.disp.coordSetId]

        if isinstance(pdisp.disp, DispGroup):
            if pdisp.disp.compileAsTemplate:
                addGridKey(pdisp.disp, makeDispGroupGridKey(coordSet.id))
            continue

        # Calculate the grid keys
        gridKeys = makeGridKeysForDisp(coordSet, pdisp.disp, pdisp.geomArray,
                                       textStyleById)

        for gridKey in gridKeys:
            addGridKey(pdisp.disp, gridKey)

    logger.debug("Calculated GridKeys for %s disps in %s",
                 len(preparedDisps), (datetime.now(pytz.utc) - startTime))

    return gridCompiledQueueItems, gridKeyIndexesByDispId


def _updateDispsJson(preparedDisps: List[PreparedDisp]):
    """ Update Disps Json

    This assigns the updated dispJson from the dispDict

    """
    for pdisp in preparedDisps:
        stripped = _packDispJson(pdisp.disp, pdisp.dispDict)

        # Dump the json back into the disp
        pdisp.disp.dispJson = json.dumps(stripped)


def _packDispJson(disp, dispDict) -> Dict:
    """ Pack Disp Json

    This method creates the disp hash id.

    It assigns the hashId to the disp and dispDict

    :param disp: The disp to assign the data back to
    :param dispDict: The updated dispDict prepared elsewhere
        The only updated done outside of this method is for the DispGroup
    :return: The updated dispDict (This result is used by the BranchDispUpdater)

    """
    # Strip out the nulls and falses, to make it even more compact
    stripped = {k: v
                for k, v in dispDict.items()
                if v is not None and v is not False}

    hashId = _createHashId(stripped)

    # Assign the value
    stripped['hid'] = hashId

    # Write the "compiled" disp JSON back to the disp.
    disp.hashId = hashId

    return stripped


def _insertToDb(dispIds, gridCompiledQueueItems, gridKeyIndexesByDispId,
                locationCompiledQueueItems, locationIndexByDispId, queueIds):
    """ Insert to DB

    This method provides the DB inserts and deletes after the data has been calculated.

    """
    startTime = datetime.now(pytz.utc)

    dispBaseTable = DispBase.__table__
    dispQueueTable = DispIndexerQueue.__table__

    gridKeyIndexTable = GridKeyIndex.__table__
    gridQueueTable = GridKeyCompilerQueue.__table__

    locationIndexTable = LocationIndex.__table__
    locationIndexCompilerQueueTable = LocationIndexCompilerQueue.__table__

    engine = CeleryDbConn.getDbEngine()
    conn = engine.connect()
    transaction = conn.begin()
    try:
        lockedDispIds = conn.execute(Select(
            whereclause=dispBaseTable.c.id.in_(dispIds),
            columns=[dispBaseTable.c.id],
            for_update=True))

        lockedDispIds = [o[0] for o in lockedDispIds]

        # Ensure that the Disps exist, otherwise we get an integrity error.
        gridKeyIndexes = []
        locationIndexes = []
        for dispId in lockedDispIds:
            gridKeyIndexes.extend(gridKeyIndexesByDispId[dispId])

            if dispId in locationIndexByDispId:
                locationIndexes.append(locationIndexByDispId[dispId])

        # Delete existing items in the location and grid index

        # grid index
        conn.execute(
            gridKeyIndexTable.delete(gridKeyIndexTable.c.dispId.in_(dispIds))
        )

        # location index
        conn.execute(
            locationIndexTable.delete(locationIndexTable.c.dispId.in_(dispIds))
        )

        # ---------------
        # Insert the Grid Key indexes
        if gridKeyIndexes:
            conn.execute(gridKeyIndexTable.insert(), gridKeyIndexes)

        # Directly insert into the Grid compiler queue.
        if gridCompiledQueueItems:
            conn.execute(
                gridQueueTable.insert(),
                [dict(coordSetId=i.coordSetId, gridKey=i.gridKey)
                 for i in gridCompiledQueueItems]
            )

        # ---------------
        # Insert the Location indexes
        if locationIndexes:
            conn.execute(locationIndexTable.insert(), locationIndexes)

        # Directly insert into the Location compiler queue.
        if locationCompiledQueueItems:
            conn.execute(
                locationIndexCompilerQueueTable.insert(),
                [dict(modelSetId=i.modelSetId, indexBucket=i.indexBucket)
                 for i in locationCompiledQueueItems]
            )

        # ---------------
        # Finally, delete the disp queue items

        conn.execute(
            dispQueueTable.delete(dispQueueTable.c.id.in_(queueIds))
        )

        transaction.commit()
        logger.debug("Committed %s GridKeyIndex in %s",
                     len(gridKeyIndexes), (datetime.now(pytz.utc) - startTime))

    except Exception as e:
        raise

    finally:
        conn.close()
