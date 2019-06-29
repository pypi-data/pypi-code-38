from vortex.handler.TupleActionProcessor import TupleActionProcessor

from peek_plugin_livedb._private.PluginNames import livedbFilt
from peek_plugin_livedb._private.PluginNames import livedbActionProcessorName
from .controller.MainController import MainController


def makeTupleActionProcessorHandler(mainController: MainController):
    processor = TupleActionProcessor(
        tupleActionProcessorName=livedbActionProcessorName,
        additionalFilt=livedbFilt,
        defaultDelegate=mainController)
    return processor
