import logging

from peek_core_user._private.PluginNames import userPluginFilt, \
    userPluginActionProcessorName
from peek_core_user._private.server.controller.MainController import \
    MainController
from vortex.handler.TupleActionProcessor import TupleActionProcessor

logger = logging.getLogger(__name__)


def makeTupleActionProcessorHandler(mainController: MainController):
    processor = TupleActionProcessor(
        tupleActionProcessorName=userPluginActionProcessorName,
        additionalFilt=userPluginFilt,
        defaultDelegate=mainController)
    return processor
