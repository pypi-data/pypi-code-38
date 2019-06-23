import json
import logging
from collections import defaultdict
from copy import copy
from datetime import datetime
from typing import List, Dict, Set, Tuple

import pytz
from sqlalchemy import select, bindparam, and_
from txcelery.defer import DeferrableTask

from peek_plugin_base.worker import CeleryDbConn
from peek_plugin_docdb._private.storage.DocDbCompilerQueue import DocDbCompilerQueue
from peek_plugin_docdb._private.storage.DocDbDocument import DocDbDocument
from peek_plugin_docdb._private.storage.DocDbDocumentTypeTuple import \
    DocDbDocumentTypeTuple
from peek_plugin_docdb._private.storage.DocDbModelSet import DocDbModelSet
from peek_plugin_docdb._private.storage.DocDbPropertyTuple import DocDbPropertyTuple
from peek_plugin_docdb._private.worker.CeleryApp import celeryApp
from peek_plugin_docdb._private.worker.tasks._CalcChunkKey import makeChunkKey
from peek_plugin_docdb.tuples.ImportDocumentTuple import ImportDocumentTuple
from vortex.Payload import Payload

logger = logging.getLogger(__name__)


# We need to insert the into the following tables:
# DocDbDocument - or update it's details if required
# DocDbIndex - The index of the keywords for the object
# DocDbDocumentRoute - delete old importGroupHash
# DocDbDocumentRoute - insert the new routes


@DeferrableTask
@celeryApp.task(bind=True)
def removeDocumentTask(self, modelSetKey: str, keys: List[str]) -> None:
    pass


@DeferrableTask
@celeryApp.task(bind=True)
def createOrUpdateDocuments(self, documentsEncodedPayload: bytes) -> None:
    # Decode arguments
    newDocuments: List[ImportDocumentTuple] = (
        Payload().fromEncodedPayload(documentsEncodedPayload).tuples
    )

    _validateNewDocuments(newDocuments)

    modelSetIdByKey = _loadModelSets()

    # Do the import
    try:

        documentByModelKey = defaultdict(list)
        for doc in newDocuments:
            documentByModelKey[doc.modelSetKey].append(doc)

        for modelSetKey, docs in documentByModelKey.items():
            modelSetId = modelSetIdByKey.get(modelSetKey)
            if modelSetId is None:
                modelSetId = _makeModelSet(modelSetKey)
                modelSetIdByKey[modelSetKey] = modelSetId

            docTypeIdsByName = _prepareLookups(docs, modelSetId)
            _insertOrUpdateObjects(docs, modelSetId, docTypeIdsByName)

    except Exception as e:
        logger.debug("Retrying import docDb objects, %s", e)
        raise self.retry(exc=e, countdown=3)



def _validateNewDocuments(newDocuments: List[ImportDocumentTuple]) -> None:
    for doc in newDocuments:
        if not doc.key:
            raise Exception("key is empty for %s" % doc)

        if not doc.modelSetKey:
            raise Exception("modelSetKey is empty for %s" % doc)

        if not doc.documentTypeKey:
            raise Exception("documentTypeKey is empty for %s" % doc)

        # if not doc.document:
        #     raise Exception("document is empty for %s" % doc)


def _loadModelSets() -> Dict[str, int]:
    # Get the model set
    engine = CeleryDbConn.getDbEngine()
    conn = engine.connect()
    try:
        modelSetTable = DocDbModelSet.__table__
        results = list(conn.execute(select(
            columns=[modelSetTable.c.id, modelSetTable.c.key]
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
        newItem = DocDbModelSet(key=modelSetKey, name=modelSetKey)
        dbSession.add(newItem)
        dbSession.commit()
        return newItem.id

    finally:
        dbSession.close()


def _prepareLookups(newDocuments: List[ImportDocumentTuple], modelSetId: int) -> Dict[str, int]:
    """ Check Or Insert Search Properties

    Make sure the search properties exist.

    """

    dbSession = CeleryDbConn.getDbSession()

    startTime = datetime.now(pytz.utc)

    try:

        docTypeNames = set()
        propertyNames = set()

        for o in newDocuments:
            o.documentTypeKey = o.documentTypeKey.lower()
            docTypeNames.add(o.documentTypeKey)

            if o.document:
                propertyNames.update([s.lower() for s in o.document])

        # Prepare Properties
        dbProps = (
            dbSession.query(DocDbPropertyTuple)
                .filter(DocDbPropertyTuple.modelSetId == modelSetId)
                .all()
        )
        propertyNames -= set([o.name for o in dbProps])

        if propertyNames:
            for newPropName in propertyNames:
                dbSession.add(DocDbPropertyTuple(
                    name=newPropName, title=newPropName, modelSetId=modelSetId
                ))

            dbSession.commit()

        del dbProps
        del propertyNames

        # Prepare Object Types
        dbObjectTypes = (
            dbSession.query(DocDbDocumentTypeTuple)
                .filter(DocDbDocumentTypeTuple.modelSetId == modelSetId)
                .all()
        )
        docTypeNames -= set([o.name for o in dbObjectTypes])

        if not docTypeNames:
            docTypeIdsByName = {o.name: o.id for o in dbObjectTypes}

        else:
            for newType in docTypeNames:
                dbSession.add(DocDbDocumentTypeTuple(
                    name=newType, title=newType, modelSetId=modelSetId
                ))

            dbSession.commit()

            dbObjectTypes = dbSession.query(DocDbDocumentTypeTuple).all()
            docTypeIdsByName = {o.name: o.id for o in dbObjectTypes}

        logger.debug("Prepared lookups in %s", (datetime.now(pytz.utc) - startTime))

        return docTypeIdsByName

    except Exception as e:
        dbSession.rollback()
        raise

    finally:
        dbSession.close()


def _insertOrUpdateObjects(newDocuments: List[ImportDocumentTuple],
                           modelSetId: int,
                           docTypeIdsByName: Dict[str, int]) -> None:
    """ Insert or Update Objects

    1) Find objects and update them
    2) Insert object if the are missing

    """

    documentTable = DocDbDocument.__table__
    queueTable = DocDbCompilerQueue.__table__

    startTime = datetime.now(pytz.utc)

    engine = CeleryDbConn.getDbEngine()
    conn = engine.connect()
    transaction = conn.begin()

    try:
        importHashSet = set()
        dontDeleteObjectIds=[]
        objectIdByKey: Dict[str, int] = {}

        objectKeys = [o.key for o in newDocuments]
        chunkKeysForQueue: Set[Tuple[str, str]] = set()

        # Query existing objects
        results = list(conn.execute(select(
            columns=[documentTable.c.id, documentTable.c.key,
                     documentTable.c.chunkKey, documentTable.c.documentJson],
            whereclause=and_(documentTable.c.key.in_(objectKeys),
                             documentTable.c.modelSetId == modelSetId)
        )))

        foundObjectByKey = {o.key: o for o in results}
        del results

        # Get the IDs that we need
        newIdGen = CeleryDbConn.prefetchDeclarativeIds(
            DocDbDocument, len(newDocuments) - len(foundObjectByKey)
        )

        # Create state arrays
        inserts = []
        updates = []

        # Work out which objects have been updated or need inserting
        for importDocument in newDocuments:
            importHashSet.add(importDocument.importGroupHash)

            existingObject = foundObjectByKey.get(importDocument.key)
            importDocumentTypeId = docTypeIdsByName[importDocument.documentTypeKey]

            packedJsonDict = copy(importDocument.document)
            packedJsonDict['_dtid'] = importDocumentTypeId
            packedJsonDict['_msid'] = modelSetId
            documentJson = json.dumps(packedJsonDict, sort_keys=True)

            # Work out if we need to update the object type
            if existingObject:
                updates.append(
                    dict(b_id=existingObject.id,
                         b_typeId=importDocumentTypeId,
                         b_documentJson=documentJson)
                )
                dontDeleteObjectIds.append(existingObject.id)

            else:
                id_ = next(newIdGen)
                existingObject = DocDbDocument(
                    id=id_,
                    modelSetId=modelSetId,
                    documentTypeId=importDocumentTypeId,
                    key=importDocument.key,
                    importGroupHash=importDocument.importGroupHash,
                    chunkKey=makeChunkKey(importDocument.modelSetKey, importDocument.key),
                    documentJson=documentJson
                )
                inserts.append(existingObject.tupleToSqlaBulkInsertDict())

            objectIdByKey[existingObject.key] = existingObject.id
            chunkKeysForQueue.add((modelSetId, existingObject.chunkKey))

        if importHashSet:
            conn.execute(
                documentTable
                    .delete(and_(~documentTable.c.id.in_(dontDeleteObjectIds),
                                 documentTable.c.importGroupHash.in_(importHashSet)))
            )

        # Insert the DocDb Objects
        if inserts:
            conn.execute(documentTable.insert(), inserts)

        if updates:
            stmt = (
                documentTable.update()
                    .where(documentTable.c.id == bindparam('b_id'))
                    .values(documentTypeId=bindparam('b_typeId'),
                            documentJson=bindparam('b_documentJson'))
            )
            conn.execute(stmt, updates)

        if chunkKeysForQueue:
            conn.execute(
                queueTable.insert(),
                [dict(modelSetId=m, chunkKey=c) for m, c in chunkKeysForQueue]
            )

        if inserts or updates or chunkKeysForQueue:
            transaction.commit()
        else:
            transaction.rollback()

        logger.debug("Inserted %s updated %s queued %s chunks in %s",
                     len(inserts), len(updates), len(chunkKeysForQueue),
                     (datetime.now(pytz.utc) - startTime))

    except Exception:
        transaction.rollback()
        raise


    finally:
        conn.close()
