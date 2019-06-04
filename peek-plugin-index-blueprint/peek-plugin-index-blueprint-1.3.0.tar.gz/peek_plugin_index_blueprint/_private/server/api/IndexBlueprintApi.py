from typing import List

from twisted.internet.defer import Deferred

from peek_plugin_index_blueprint._private.server.controller.ThingIndexImportController import \
    ThingIndexImportController
from peek_plugin_index_blueprint.server.IndexBlueprintApiABC import IndexBlueprintApiABC


class IndexBlueprintApi(IndexBlueprintApiABC):

    def __init__(self, importController: ThingIndexImportController):
        self._importController = importController

    def shutdown(self):
        pass

    def createOrUpdateThings(self, thingsEncodedPayload: bytes) -> Deferred:
        return self._importController.createOrUpdateThings(thingsEncodedPayload)

    def removeThings(self, modelSetKey: str, importGroupHashs: List[str]) -> Deferred:
        pass
