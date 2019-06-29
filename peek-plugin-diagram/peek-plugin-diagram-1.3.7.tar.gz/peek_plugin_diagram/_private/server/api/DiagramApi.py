import logging

from peek_plugin_diagram._private.server.api.DiagramImportApi import DiagramImportApi
from peek_plugin_diagram._private.server.api.DiagramViewerApi import DiagramViewerApi
from peek_plugin_diagram._private.server.controller.BranchUpdateController import \
    BranchUpdateController
from peek_plugin_diagram._private.server.controller.DispImportController import \
    DispImportController
from peek_plugin_diagram._private.server.controller.LookupImportController import \
    LookupImportController
from peek_plugin_diagram._private.server.controller.StatusController import \
    StatusController
from peek_plugin_diagram.server.DiagramApiABC import DiagramApiABC
from peek_plugin_diagram.server.DiagramImportApiABC import DiagramImportApiABC
from peek_plugin_diagram.server.DiagramViewerApiABC import DiagramViewerApiABC

logger = logging.getLogger(__name__)


class DiagramApi(DiagramApiABC):
    def __init__(self, mainController: StatusController,
                 dispImportController: DispImportController,
                 lookupImportController: LookupImportController,
                 branchUpdateController: BranchUpdateController,
                 ormSessionCreator):
        self._viewerApi = DiagramViewerApi(ormSessionCreator)
        self._importApi = DiagramImportApi(
            mainController, dispImportController,
            lookupImportController, branchUpdateController
        )

    def shutdown(self):
        self._importApi.shutdown()
        self._viewerApi.shutdown()

        self._importApi = None
        self._viewerApi = None

    def importApi(self) -> DiagramImportApiABC:
        return self._importApi

    def viewerApi(self) -> DiagramViewerApiABC:
        return self._viewerApi
