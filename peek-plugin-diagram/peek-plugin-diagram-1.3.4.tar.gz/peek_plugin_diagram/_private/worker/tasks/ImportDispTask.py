import logging
from datetime import datetime
from typing import List, Dict, Tuple

import pytz
import ujson as json
from peek_plugin_base.storage.DbConnection import pgCopyInsert, convertToCoreSqlaInsert
from peek_plugin_base.worker import CeleryDbConn
from peek_plugin_diagram._private.server.controller.DispCompilerQueueController import \
    DispCompilerQueueController
from peek_plugin_diagram._private.storage.Display import \
    DispBase, DispEllipse, DispPolygon, DispText, DispPolyline, DispGroup, \
    DispGroupPointer, DispNull
from peek_plugin_diagram._private.storage.ModelSet import \
    ModelCoordSet, getOrCreateCoordSet
from peek_plugin_diagram._private.worker.CeleryApp import celeryApp
from peek_plugin_diagram._private.worker.tasks.ImportDispLink import importDispLinks
from peek_plugin_diagram._private.worker.tasks.LookupHashConverter import \
    LookupHashConverter
from peek_plugin_diagram.tuples.shapes.ImportDispEllipseTuple import \
    ImportDispEllipseTuple
from peek_plugin_diagram.tuples.shapes.ImportDispGroupPtrTuple import \
    ImportDispGroupPtrTuple
from peek_plugin_diagram.tuples.shapes.ImportDispGroupTuple import ImportDispGroupTuple
from peek_plugin_diagram.tuples.shapes.ImportDispPolygonTuple import \
    ImportDispPolygonTuple
from peek_plugin_diagram.tuples.shapes.ImportDispPolylineTuple import \
    ImportDispPolylineTuple
from peek_plugin_diagram.tuples.shapes.ImportDispTextTuple import ImportDispTextTuple
from peek_plugin_livedb.tuples.ImportLiveDbItemTuple import ImportLiveDbItemTuple
from txcelery.defer import DeferrableTask
from vortex.Payload import Payload

logger = logging.getLogger(__name__)

IMPORT_TUPLE_MAP = {
    ImportDispGroupTuple.tupleType(): DispGroup,
    ImportDispGroupPtrTuple.tupleType(): DispGroupPointer,
    ImportDispEllipseTuple.tupleType(): DispEllipse,
    ImportDispPolygonTuple.tupleType(): DispPolygon,
    ImportDispPolylineTuple.tupleType(): DispPolyline,
    ImportDispTextTuple.tupleType(): DispText
}

IMPORT_FIELD_NAME_MAP = {
    'levelHash': 'levelId',
    'layerHash': 'layerId',
    'lineStyleHash': 'lineStyleId',
    'colorHash': 'colorId',
    'fillColorHash': 'fillColorId',
    'lineColorHash': 'lineColorId',
    'textStyleHash': 'textStyleId',
    'targetDispGroupHash': 'targetDispGroupId',
    'targetDispGroupName': 'targetDispGroupName'
}

IMPORT_SORT_ORDER = {
    ImportDispGroupTuple.tupleType(): 0,
    ImportDispGroupPtrTuple.tupleType(): 1,
    ImportDispEllipseTuple.tupleType(): 2,
    ImportDispPolygonTuple.tupleType(): 2,
    ImportDispPolylineTuple.tupleType(): 2,
    ImportDispTextTuple.tupleType(): 2
}


@DeferrableTask
@celeryApp.task(bind=True)
def importDispsTask(self, modelSetKey: str, coordSetKey: str,
                    importGroupHash: str,
                    dispsEncodedPayload: bytes) -> List[ImportLiveDbItemTuple]:
    """ Import Disp Task

    :returns None

    """
    try:
        importDisps = Payload().fromEncodedPayload(dispsEncodedPayload).tuples

        _validateImportDisps(importDisps)

        coordSet = _loadCoordSet(modelSetKey, coordSetKey)

        _validateImportDisps(importDisps)

        dispIdsToCompile, dispLinkImportTuples, ormDisps = _importDisps(
            coordSet, importDisps
        )

        _validateConvertedDisps(ormDisps)

        # Update the coord set view start position if required.
        _updateCoordSetPosition(coordSet, importDisps)

        _bulkLoadDispsTask(importGroupHash, ormDisps)

        liveDbImportTuples = importDispLinks(
            coordSet, importGroupHash, dispLinkImportTuples
        )

        DispCompilerQueueController.queueDispIdsToCompile(
            dispIdsToCompile, CeleryDbConn.getDbSession
        )

        return liveDbImportTuples

    except Exception as e:
        logger.exception(e)
        logger.debug("Retrying import displays, %s", e)
        raise self.retry(exc=e, countdown=3)


def _loadCoordSet(modelSetKey, coordSetKey):
    ormSession = CeleryDbConn.getDbSession()
    try:
        coordSet = getOrCreateCoordSet(ormSession, modelSetKey, coordSetKey)
        ormSession.expunge_all()
        return coordSet

    finally:
        ormSession.close()


def _validateImportDisps(importDisp: List):

    for importDisp in importDisp:
        isGroup = isinstance(importDisp, ImportDispGroupTuple)
        # isGroupChild = not isGroup and importDisp.parentDispGroupHash

        if not isGroup and importDisp.layerHash is None:
            raise Exception("Disps must have layers and levels")

        if not isGroup and importDisp.levelHash is None:
            raise Exception("Disps must have layers and levels")


def _validateConvertedDisps(disps: List):
    NoneT = type(None)

    def checkInt(importDisp, attrName):
        if hasattr(importDisp, attrName):
            if type(getattr(importDisp, attrName)) not in (int, float, NoneT):
                raise Exception('Disp %s must be int : "%s"'
                                % (attrName, importDisp.colorHash))

    for disp in disps:
        checkInt(disp, 'colorHash')
        checkInt(disp, 'lineColorHash')
        checkInt(disp, 'fillColorHash')
        checkInt(disp, 'lineStyleHash')
        checkInt(disp, 'textStyleHash')
        checkInt(disp, 'layerHash')
        checkInt(disp, 'levelHash')


def _importDisps(coordSet: ModelCoordSet, importDisps: List):
    """ Link Disps

    1) Use the AgentImportDispGridLookup to convert lookups from importHash
        to id
    2) set the  coordSetId

    This is not done in a thread because the lookups cause issues

    """

    dispIdGen = CeleryDbConn.prefetchDeclarativeIds(DispBase, len(importDisps))

    dispIdsToCompile = []
    importDispLinks = []
    ormDisps = []

    ormSession = CeleryDbConn.getDbSession()
    try:

        lookupConverter = LookupHashConverter(ormSession,
                                              modelSetId=coordSet.modelSetId,
                                              coordSetId=coordSet.id)

        dispGroupPtrWithTargetHash: List[Tuple[DispGroupPointer, str]] = []
        dispGroupChildWithTargetHash: List[Tuple[DispBase, str]] = []

        # Preload any groups our pointers may point to.

        # Pre-import any DispGroup IDs we may need
        dispGroupTargetImportHashes = [
            o.targetDispGroupHash
            for o in importDisps
            if o.tupleType() == ImportDispGroupPtrTuple.tupleType()
        ]

        # This will store DispGroup and DispGroupPointer hashes
        groupIdByImportHash: Dict[str, int] = {
            o.importHash: o.id
            for o in
            ormSession.query(DispBase.importHash, DispBase.id)
                .filter(DispBase.importHash.in_(dispGroupTargetImportHashes))
                .filter(DispBase.coordSetId == coordSet.id)
        }

        del dispGroupTargetImportHashes

        # This is a list of DispGroup.id.
        # We use this to filter out disps that part of a DispGroup,
        # they don't get compiled
        dispGroupIds = set()

        # Sort the DispGroups first, so they are created before any FK references them
        sortedImportDisps = sorted(importDisps,
                                   key=lambda o: IMPORT_SORT_ORDER[o.tupleType()])

        for importDisp in sortedImportDisps:
            # Convert the geometry into the internal array format
            _convertGeom(importDisp)

            # Create the storage tuple instance, and copy over the data.
            ormDisp = _convertImportTuple(importDisp)
            ormDisps.append(ormDisp)

            # Preallocate the IDs for performance on PostGreSQL
            ormDisp.id = next(dispIdGen)

            # Assign the coord set id.
            ormDisp.coordSetId = coordSet.id

            # If this is a dispGroup, index it's ID
            if isinstance(ormDisp, DispGroup):
                dispGroupIds.add(ormDisp.id)
                groupIdByImportHash[ormDisp.importHash] = ormDisp.id

            # If this is a dispGroupPtr, index its targetHash so we can update it
            if isinstance(ormDisp, DispGroupPointer):
                groupIdByImportHash[ormDisp.importHash] = ormDisp.id

                if ormDisp.targetDispGroupName:
                    ormDisp.targetDispGroupName = '%s|%s' % (
                        coordSet.id, ormDisp.targetDispGroupName
                    )

                # Not all DispGroupPointers have targets,
                # they can be orphaned instances
                if importDisp.targetDispGroupHash:
                    dispGroupPtrWithTargetHash.append(
                        (ormDisp, importDisp.targetDispGroupHash)
                    )

            # If this is a dispGroupPtr, index its targetHash so we can update it
            parentDispGroupHash = getattr(importDisp, "parentDispGroupHash", None)
            if parentDispGroupHash:
                dispGroupChildWithTargetHash.append((ormDisp, parentDispGroupHash))

            # Add some interim data to the import display link, so it can be created
            if hasattr(importDisp, "liveDbDispLinks"):
                for importDispLink in importDisp.liveDbDispLinks:
                    attrName = importDispLink.dispAttrName
                    importDispLink.internalRawValue = getattr(ormDisp, attrName)
                    importDispLink.internalDispId = ormDisp.id
                    importDispLinks.append(importDispLink)

            # Convert the values of the liveDb attributes
            lookupConverter.convertLookups(ormDisp)

            # Add the after translate value, this is the Display Value
            if hasattr(importDisp, "liveDbDispLinks"):
                for importDispLink in importDisp.liveDbDispLinks:
                    attrName = importDispLink.dispAttrName
                    importDispLink.internalDisplayValue = getattr(ormDisp, attrName)

            # Queue the Disp to be compiled into a grid.
            # Disps belonging to a DispGroup do not get compiled into grids.
            if ormDisp.groupId not in dispGroupIds:
                dispIdsToCompile.append(ormDisp.id)

        # Link the DispGroups
        # Create the links between the Disp and DispGroup
        for ormDisp, groupHash in dispGroupChildWithTargetHash:
            groupOrmObjId = groupIdByImportHash.get(groupHash)
            if groupOrmObjId is None:
                raise Exception(
                    "DispGroup with importHash %s doesn't exist" % groupHash)

            ormDisp.groupId = groupOrmObjId

        # Link the DispGroupPtr to the DispGroup
        # This is only used when the dispGrouPtr points to a disp group
        for ormDisp, groupHash in dispGroupPtrWithTargetHash:
            groupOrmObjId = groupIdByImportHash.get(groupHash)
            if groupOrmObjId is None:
                raise Exception(
                    "DispGroup with importHash %s doesn't exist" % groupHash)

            ormDisp.targetDispGroupId = groupOrmObjId


    finally:
        ormSession.close()

    return dispIdsToCompile, importDispLinks, ormDisps


def _convertGeom(importDisp):
    if not hasattr(importDisp, "geom"):
        return

    coordArray = []
    for i in importDisp.geom:
        coordArray.append(i[0])
        coordArray.append(i[1])

    importDisp.geom = json.dumps(coordArray)


def _convertImportTuple(importDisp):
    """ Convert Import Tuple

    This method mostly copies over data from the import tuple into the storage tuple,
    converting some fields and field names as required.

    """
    if not importDisp.tupleType() in IMPORT_TUPLE_MAP:
        raise Exception(
            "Import Tuple %s is not a valid type" % importDisp.tupleType()
        )

    disp = IMPORT_TUPLE_MAP[importDisp.tupleType()]()

    for importFieldName in importDisp.tupleFieldNames():
        if importFieldName == "data" and importDisp.data:
            disp.dataJson = json.dumps(importDisp.data)
            continue

        if importFieldName == "geom":

            # Groups are stored in whichever grid where the where ever the center point
            # is located, OR, in the special dispgroup grid.
            if isinstance(disp, DispGroup) and not importDisp.geom:
                continue

            disp.geomJson = importDisp.geom

            # Moved to server, due to celery 3 pickle problem
            # disp.geomJson = json.dumps(convertFromWkbElement(importDisp.geom))
            continue

        # Convert the field name if it exists
        dispFieldName = IMPORT_FIELD_NAME_MAP.get(importFieldName, importFieldName)

        setattr(disp, dispFieldName, getattr(importDisp, importFieldName))

    if isinstance(disp, DispGroup):
        disp.dispsJson = '[]'

    return disp


def _bulkLoadDispsTask(importGroupHash: str, disps: List):
    """ Import Disps Links

    1) Drop all disps with matching importGroupHash

    2) set the  coordSetId

    :param importGroupHash:
    :param disps: An array of disp objects to import
    :return:
    """

    dispTable = DispBase.__table__

    engine = CeleryDbConn.getDbEngine()
    conn = engine.connect()
    transaction = conn.begin()

    try:
        conn.execute(dispTable
                     .delete()
                     .where(dispTable.c.importGroupHash == importGroupHash))

        transaction.commit()

        _bulkInsertDisps(engine, disps)

    except Exception:
        transaction.rollback()
        raise

    finally:
        conn.close()


def _bulkInsertDisps(engine, disps: List):
    """ Bulk Insert Disps

    1) Drop all disps with matching importGroupHash

    2) set the  coordSetId

    :param engine: The connection to use
    :param disps: An array of disp objects to import
    :return:
    """

    INSERT_MAP = (
        (DispGroup, (DispBase, DispGroup)),
        (DispGroupPointer, (DispBase, DispGroupPointer)),
        (DispEllipse, (DispBase, DispEllipse)),
        (DispPolyline, (DispBase, DispPolyline)),
        (DispPolygon, (DispBase, DispPolygon)),
        (DispText, (DispBase, DispText)),
        (DispNull, (DispBase, DispNull)),
    )

    startTime = datetime.now(pytz.utc)
    startDispsLen = len(disps)
    rawConn = engine.raw_connection()

    try:
        for DispType, Tables in INSERT_MAP:
            inserts = []
            remainingDisps = []

            for disp in disps:
                if isinstance(disp, DispType):
                    insertDict = convertToCoreSqlaInsert(disp, DispType)
                    insertDict['type'] = DispType.RENDERABLE_TYPE
                    inserts.append(insertDict)

                else:
                    remainingDisps.append(disp)

            disps = remainingDisps

            if not inserts:
                continue

            for Table in Tables:
                pgCopyInsert(rawConn, Table.__table__, inserts)
                # conn.execute(Table.__table__.insert(), inserts)

        if disps:
            raise Exception("_bulkInsertDisps: We didn't insert all the disps")

        logger.info("Inserted %s Disps in %s",
                    startDispsLen, (datetime.now(pytz.utc) - startTime))

        rawConn.commit()

    except Exception:
        rawConn.rollback()
        raise

    finally:
        rawConn.close()


def _updateCoordSetPosition(coordSet: ModelCoordSet, disps: List):
    """ Update CoordSet Position

    1) Drop all disps with matching importGroupHash

    2) set the  coordSetId

    :param coordSet:
    :param disps: An array of disp objects to import
    :return:
    """

    if coordSet.initialPanX or coordSet.initialPanY or coordSet.initialZoom:
        return

    startTime = datetime.now(pytz.utc)

    ormSession = CeleryDbConn.getDbSession()

    try:

        # Initialise the ModelCoordSet initial position if it's not set
        for disp in disps:
            if not hasattr(disp, 'geomJson'):
                continue
            coords = json.loads(disp.geomJson)
            coordSet.initialPanX = coords[0]
            coordSet.initialPanY = coords[1]
            coordSet.initialZoom = 0.05
            ormSession.merge(coordSet)
            break

        ormSession.commit()

        logger.info("Updated coordset position in %s",
                    (datetime.now(pytz.utc) - startTime))

    finally:
        ormSession.close()
