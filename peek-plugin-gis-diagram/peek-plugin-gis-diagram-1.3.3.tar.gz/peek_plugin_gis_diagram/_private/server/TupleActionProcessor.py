from vortex.handler.TupleActionProcessor import TupleActionProcessor

from peek_plugin_gis_diagram._private.PluginNames import gisDiagramFilt
from peek_plugin_gis_diagram._private.PluginNames import gisDiagramActionProcessorName
from .controller.MainController import MainController


def makeTupleActionProcessorHandler(mainController: MainController):
    processor = TupleActionProcessor(
        tupleActionProcessorName=gisDiagramActionProcessorName,
        additionalFilt=gisDiagramFilt,
        defaultDelegate=mainController)
    return processor
