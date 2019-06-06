import logging
from typing import List

from twisted.internet.defer import inlineCallbacks

from peek_plugin_index_blueprint._private.worker.tasks.ThingIndexImporter import \
    createOrUpdateThings
from peek_plugin_index_blueprint._private.worker.tasks.ThingIndexRemover import \
    removeThings

logger = logging.getLogger(__name__)


class ThingIndexImportController:
    def __init__(self):
        pass

    def shutdown(self):
        pass

    @inlineCallbacks
    def removeThings(self, modelSetKey: str, importGroupHashes: List[str]):
        yield removeThings.delay(modelSetKey, importGroupHashes)

    @inlineCallbacks
    def createOrUpdateThings(self, thingsEncodedPayload: bytes):
        yield createOrUpdateThings.delay(thingsEncodedPayload)
