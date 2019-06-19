from typing import List

from twisted.internet.defer import Deferred

from peek_plugin_docdb._private.server.controller.ImportController import ImportController
from peek_plugin_docdb.server.DocDbApiABC import DocDbApiABC


class DocDbApi(DocDbApiABC):

    def __init__(self, importController: ImportController):
        self._importController = importController

    def shutdown(self):
        pass

    def createOrUpdateDocuments(self, documentsEncodedPayload: bytes) -> Deferred:
        return self._importController.createOrUpdateDocuments(documentsEncodedPayload)

    def deleteDocuments(self, modelSetKey: str, keys: List[str]) -> Deferred:
        pass
