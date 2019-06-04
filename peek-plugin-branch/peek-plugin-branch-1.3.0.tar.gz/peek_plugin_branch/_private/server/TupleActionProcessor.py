from vortex.handler.TupleActionProcessor import TupleActionProcessor

from peek_plugin_branch._private.PluginNames import branchFilt
from peek_plugin_branch._private.PluginNames import branchActionProcessorName
from .controller.MainController import MainController


def makeTupleActionProcessorHandler(mainController: MainController):
    processor = TupleActionProcessor(
        tupleActionProcessorName=branchActionProcessorName,
        additionalFilt=branchFilt,
        defaultDelegate=mainController)
    return processor
