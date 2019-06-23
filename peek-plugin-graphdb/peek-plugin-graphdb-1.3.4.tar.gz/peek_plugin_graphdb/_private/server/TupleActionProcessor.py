from vortex.handler.TupleActionProcessor import TupleActionProcessor

from peek_plugin_graphdb._private.PluginNames import graphDbFilt
from peek_plugin_graphdb._private.PluginNames import graphDbActionProcessorName
from .controller.MainController import MainController


def makeTupleActionProcessorHandler(mainController: MainController):
    processor = TupleActionProcessor(
        tupleActionProcessorName=graphDbActionProcessorName,
        additionalFilt=graphDbFilt,
        defaultDelegate=mainController)
    return processor
