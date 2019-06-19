from vortex.handler.TupleActionProcessor import TupleActionProcessor

from peek_plugin_chat._private.PluginNames import chatFilt
from peek_plugin_chat._private.PluginNames import chatActionProcessorName
from .controller.MainController import MainController


def makeTupleActionProcessorHandler(mainController: MainController):
    processor = TupleActionProcessor(
        tupleActionProcessorName=chatActionProcessorName,
        additionalFilt=chatFilt,
        defaultDelegate=mainController)
    return processor