from vortex.handler.TupleActionProcessor import TupleActionProcessor

from peek_core_search._private.PluginNames import searchFilt
from peek_core_search._private.PluginNames import searchActionProcessorName
from .controller.MainController import MainController


def makeTupleActionProcessorHandler(mainController: MainController):
    processor = TupleActionProcessor(
        tupleActionProcessorName=searchActionProcessorName,
        additionalFilt=searchFilt,
        defaultDelegate=mainController)
    return processor
