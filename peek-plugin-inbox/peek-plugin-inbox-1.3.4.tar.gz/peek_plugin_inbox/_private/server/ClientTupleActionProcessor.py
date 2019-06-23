import logging

from peek_plugin_inbox._private.PluginNames import inboxFilt, \
    inboxActionProcessorName
from peek_plugin_inbox._private.server.controller.MainController import \
    MainController
from vortex.handler.TupleActionProcessor import TupleActionProcessor

logger = logging.getLogger(__name__)


def makeTupleActionProcessorHandler(inboxProcessor: MainController):
    processor = TupleActionProcessor(
        tupleActionProcessorName=inboxActionProcessorName,
        additionalFilt=inboxFilt,
        defaultDelegate=inboxProcessor)
    return processor
