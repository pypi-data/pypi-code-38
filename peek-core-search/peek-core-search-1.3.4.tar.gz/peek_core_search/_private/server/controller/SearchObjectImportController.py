import logging
from typing import List

from twisted.internet.defer import inlineCallbacks

from peek_core_search._private.worker.tasks.ImportSearchObjectTask import \
    importSearchObjectTask, removeSearchObjectTask

logger = logging.getLogger(__name__)


class SearchObjectImportController:
    def __init__(self):
        pass

    def shutdown(self):
        pass

    @inlineCallbacks
    def importSearchObjects(self, searchObjectsEncodedPayload: bytes):
        yield importSearchObjectTask.delay(searchObjectsEncodedPayload)

    @inlineCallbacks
    def removeSearchObjects(self, importGroupHashes: List[str]):
        yield removeSearchObjectTask.delay(importGroupHashes)