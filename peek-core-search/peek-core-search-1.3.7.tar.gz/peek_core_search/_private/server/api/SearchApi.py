from typing import List

from twisted.internet.defer import Deferred

from peek_core_search._private.server.controller.SearchObjectImportController import \
    SearchObjectImportController
from peek_core_search.server.SearchApiABC import SearchApiABC


class SearchApi(SearchApiABC):

    def __init__(self, importController: SearchObjectImportController):
        self._importController = importController

    def shutdown(self):
        pass

    def importSearchObjects(self, searchObjectsEncodedPayload: bytes) -> Deferred:
        return self._importController.importSearchObjects(
            searchObjectsEncodedPayload
        )

    def removeSearchObjects(self, importGroupHashes: List[str]) -> Deferred:
        return self._importController.removeSearchObjects(importGroupHashes)
