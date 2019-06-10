from vortex.handler.TupleActionProcessor import TupleActionProcessor

from peek_plugin_index_blueprint._private.PluginNames import indexBlueprintFilt
from peek_plugin_index_blueprint._private.PluginNames import indexBlueprintActionProcessorName
from .controller.MainController import MainController


def makeTupleActionProcessorHandler(mainController: MainController):
    processor = TupleActionProcessor(
        tupleActionProcessorName=indexBlueprintActionProcessorName,
        additionalFilt=indexBlueprintFilt,
        defaultDelegate=mainController)
    return processor
