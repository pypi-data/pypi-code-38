from typing import List

from abc import ABCMeta, abstractmethod
from twisted.internet.defer import Deferred

from peek_plugin_diagram.server.DiagramImportApiABC import DiagramImportApiABC
from peek_plugin_diagram.server.DiagramViewerApiABC import DiagramViewerApiABC


class DiagramApiABC(metaclass=ABCMeta):
    def importApi(self) -> DiagramImportApiABC:
        """ Import API

        :return: The Import API for the diagram plugin

        """

    def viewerApi(self) -> DiagramViewerApiABC:
        """ Viewer API

        :return: The viewer API for the diagram plugin

        """
