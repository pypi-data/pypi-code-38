from peek_plugin_gis_diagram._private.server.controller.MainController import \
    MainController
from peek_plugin_gis_diagram.server.GisDiagramApiABC import GisDiagramApiABC


class GisDiagramApi(GisDiagramApiABC):
    def __init__(self, mainController: MainController):
        self._mainController = mainController

    def shutdown(self):
        pass
