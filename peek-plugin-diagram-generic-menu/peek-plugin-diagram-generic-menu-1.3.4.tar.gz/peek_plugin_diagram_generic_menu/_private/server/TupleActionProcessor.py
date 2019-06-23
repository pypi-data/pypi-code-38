from vortex.handler.TupleActionProcessor import TupleActionProcessor

from peek_plugin_diagram_generic_menu._private.PluginNames import diagramGenericMenuFilt
from peek_plugin_diagram_generic_menu._private.PluginNames import diagramGenericMenuActionProcessorName
from .controller.MainController import MainController


def makeTupleActionProcessorHandler(mainController: MainController):
    processor = TupleActionProcessor(
        tupleActionProcessorName=diagramGenericMenuActionProcessorName,
        additionalFilt=diagramGenericMenuFilt,
        defaultDelegate=mainController)
    return processor
