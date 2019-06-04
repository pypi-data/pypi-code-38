from vortex.handler.TupleActionProcessor import TupleActionProcessor

from peek_plugin_tutorial._private.PluginNames import tutorialFilt
from peek_plugin_tutorial._private.PluginNames import tutorialActionProcessorName
from .controller.MainController import MainController


def makeTupleActionProcessorHandler(mainController: MainController):
    processor = TupleActionProcessor(
        tupleActionProcessorName=tutorialActionProcessorName,
        additionalFilt=tutorialFilt,
        defaultDelegate=mainController)
    return processor
