from vortex.handler.TupleActionProcessor import TupleActionProcessor

from peek_plugin_docdb._private.PluginNames import docDbFilt
from peek_plugin_docdb._private.PluginNames import docDbActionProcessorName
from .controller.MainController import MainController


def makeTupleActionProcessorHandler(mainController: MainController):
    processor = TupleActionProcessor(
        tupleActionProcessorName=docDbActionProcessorName,
        additionalFilt=docDbFilt,
        defaultDelegate=mainController)
    return processor
