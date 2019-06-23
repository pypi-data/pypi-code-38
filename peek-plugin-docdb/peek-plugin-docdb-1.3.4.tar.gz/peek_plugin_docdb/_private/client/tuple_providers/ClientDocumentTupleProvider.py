import json
import logging
from collections import defaultdict
from typing import Union, List

from twisted.internet.defer import Deferred

from peek_plugin_docdb._private.client.controller.DocumentCacheController import \
    DocumentCacheController
from peek_plugin_docdb._private.storage.DocDbDocumentTypeTuple import \
    DocDbDocumentTypeTuple
from peek_plugin_docdb._private.storage.DocDbEncodedChunk import DocDbEncodedChunk
from peek_plugin_docdb._private.storage.DocDbModelSet import DocDbModelSet
from peek_plugin_docdb._private.worker.tasks._CalcChunkKey import makeChunkKey
from peek_plugin_docdb.tuples.DocumentTuple import DocumentTuple
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class ClientDocumentTupleProvider(TuplesProviderABC):
    def __init__(self, cacheHandler: DocumentCacheController):
        self._cacheHandler = cacheHandler

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        modelSetKey = tupleSelector.selector["modelSetKey"]
        keys = tupleSelector.selector["keys"]

        keysByChunkKey = defaultdict(list)

        foundDocuments: List[DocumentTuple] = []

        for key in keys:
            keysByChunkKey[makeChunkKey(modelSetKey, key)].append(key)

        for chunkKey, subKeys in keysByChunkKey.items():
            chunk: DocDbEncodedChunk = self._cacheHandler.documentChunk(chunkKey)

            if not chunk:
                logger.warning("Document chunk %s is missing from cache", chunkKey)
                continue

            docsByKeyStr = Payload().fromEncodedPayload(chunk.encodedData).tuples[0]
            docsByKey = json.loads(docsByKeyStr)

            for subKey in subKeys:
                if subKey not in docsByKey:
                    logger.warning(
                        "Document %s is missing from index, chunkKey %s",
                        subKey, chunkKey
                    )
                    continue

                # Reconstruct the data
                objectProps: {} = json.loads(docsByKey[subKey])

                # Get out the object type
                thisDocumentTypeId = objectProps['_dtid']
                del objectProps['_dtid']

                # Get out the object type
                thisModelSetId = objectProps['_msid']
                del objectProps['_msid']

                # Create the new object
                newObject = DocumentTuple()
                foundDocuments.append(newObject)

                newObject.key = subKey
                newObject.modelSet = DocDbModelSet(id=thisModelSetId)
                newObject.documentType = DocDbDocumentTypeTuple(id=thisDocumentTypeId)
                newObject.document = objectProps

        # Create the vortex message
        return Payload(filt, tuples=foundDocuments).makePayloadEnvelope().toVortexMsg()
