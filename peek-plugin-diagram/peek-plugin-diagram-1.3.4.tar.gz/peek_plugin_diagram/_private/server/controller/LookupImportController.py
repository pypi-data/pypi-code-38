import ujson as json
import logging
from typing import List, Optional, Any, Dict

from twisted.internet.defer import inlineCallbacks, returnValue

from peek_plugin_diagram._private.storage.Display import DispColor, DispLayer, DispLevel, \
    DispLineStyle, DispTextStyle
from peek_plugin_diagram._private.storage.ModelSet import getOrCreateModelSet, \
    getOrCreateCoordSet
from peek_plugin_diagram.tuples.lookups.ImportDispColorTuple import ImportDispColorTuple
from peek_plugin_diagram.tuples.lookups.ImportDispLayerTuple import ImportDispLayerTuple
from peek_plugin_diagram.tuples.lookups.ImportDispLevelTuple import ImportDispLevelTuple
from peek_plugin_diagram.tuples.lookups.ImportDispLineStyleTuple import \
    ImportDispLineStyleTuple
from peek_plugin_diagram.tuples.lookups.ImportDispTextStyleTuple import \
    ImportDispTextStyleTuple
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Tuple import TUPLE_TYPES_BY_NAME

logger = logging.getLogger(__name__)

ORM_TUPLE_MAP: Dict[str, Any] = {
    ImportDispColorTuple.tupleType(): DispColor,
    ImportDispLayerTuple.tupleType(): DispLayer,
    ImportDispLevelTuple.tupleType(): DispLevel,
    ImportDispLineStyleTuple.tupleType(): DispLineStyle,
    ImportDispTextStyleTuple.tupleType(): DispTextStyle,
}


class LookupImportController:
    def __init__(self, dbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    def shutdown(self):
        pass

    @inlineCallbacks
    def importLookups(self, modelSetKey: str, coordSetKey: Optional[str],
                      lookupTupleType: str, lookupTuples: List,
                      deleteOthers: bool, updateExisting: bool):

        yield self._importInThread(modelSetKey, coordSetKey,
                                   lookupTupleType, lookupTuples,
                                   deleteOthers, updateExisting)

        logger.debug("TODO, Notify the observable")

        return True

    @deferToThreadWrapWithLogger(logger)
    def _importInThread(self, modelSetKey: str, coordSetKey: str, tupleType: str,
                        tuples,
                        deleteOthers: bool, updateExisting: bool):
        LookupType = ORM_TUPLE_MAP[tupleType]

        if LookupType == DispLineStyle:
            self._convertLineStyles(tuples)

        itemsByImportHash = {}

        addCount = 0
        updateCount = 0
        deleteCount = 0

        ormSession = self._dbSessionCreator()
        try:

            modelSet = getOrCreateModelSet(ormSession, modelSetKey)
            coordSet = None

            if coordSetKey:
                coordSet = getOrCreateCoordSet(
                    ormSession, modelSetKey, coordSetKey)

                all = (ormSession.query(LookupType)
                       .filter(LookupType.coordSetId == coordSet.id)
                       .all())

            else:
                all = (ormSession.query(LookupType)
                       .filter(LookupType.modelSetId == modelSet.id)
                       .all())

            def updateFks(lookup):
                if hasattr(lookup, "coordSetId"):
                    assert coordSet
                    lookup.coordSetId = coordSet.id
                else:
                    lookup.modelSetId = modelSet.id

            for lookup in all:
                # Initialise
                itemsByImportHash[lookup.importHash] = lookup

            for lookup in tuples:
                importHash = str(lookup.importHash)

                # If it's an existing item, update it
                if importHash in itemsByImportHash:
                    existing = itemsByImportHash.pop(importHash)

                    if updateExisting:
                        for fieldName in lookup.tupleFieldNames():
                            setattr(existing, fieldName,
                                    getattr(lookup, fieldName))

                        updateFks(existing)
                        updateCount += 1

                # If it's a new item, create it
                else:
                    newTuple = LookupType()

                    for fieldName in lookup.tupleFieldNames():
                        if fieldName in ("id", "coordSetId", "modelSetId"):
                            continue
                        setattr(newTuple, fieldName,
                                getattr(lookup, fieldName))

                    updateFks(newTuple)
                    ormSession.add(newTuple)
                    addCount += 1

            if deleteOthers:
                for lookup in list(itemsByImportHash.values()):
                    ormSession.delete(lookup)
                    deleteCount += 1

            try:
                ormSession.commit()

            except Exception as e:
                ormSession.rollback()
                logger.exception(e)
                raise

            logger.info("Updates for %s received, Added %s, Updated %s, Deleted %s",
                        tupleType, addCount, updateCount, deleteCount)

        except Exception as e:
            logger.exception(e)
            raise

        finally:
            ormSession.close()

    @deferToThreadWrapWithLogger(logger)
    def getLookups(self, modelSetKey: str, coordSetKey: Optional[str],
                   tupleType: str):

        LookupType = ORM_TUPLE_MAP[tupleType]

        ormSession = self._dbSessionCreator()
        try:

            modelSet = getOrCreateModelSet(ormSession, modelSetKey)

            if coordSetKey:
                coordSet = getOrCreateCoordSet(
                    ormSession, modelSetKey, coordSetKey)

                all = (ormSession.query(LookupType)
                       .filter(LookupType.coordSetId == coordSet.id)
                       .all())

            else:
                all = (ormSession.query(LookupType)
                       .filter(LookupType.modelSetId == modelSet.id)
                       .all())

            importTuples = []
            ImportTuple = TUPLE_TYPES_BY_NAME[tupleType]

            for ormTuple in all:
                newTuple = ImportTuple()

                for fieldName in newTuple.tupleFieldNames():
                    if fieldName == 'modelSetKey':
                        newTuple.modelSetKey = modelSetKey

                    elif fieldName == 'coordSetKey':
                        newTuple.coordSetKey = coordSetKey

                    else:
                        setattr(newTuple, fieldName,
                                getattr(ormTuple, fieldName))

                importTuples.append(newTuple)

            return importTuples

        except Exception as e:
            logger.exception(e)

        finally:
            ormSession.close()

    def _convertLineStyles(self, importLineStyles: List[ImportDispTextStyleTuple]):
        for style in importLineStyles:
            dp = style.dashPattern

            if dp is None:
                continue

            if not isinstance(dp, list):
                dp = [dp]

            style.dashPattern = json.dumps(dp)
