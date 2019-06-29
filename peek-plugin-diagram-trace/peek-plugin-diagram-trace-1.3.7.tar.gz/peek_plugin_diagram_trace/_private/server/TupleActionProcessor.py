from vortex.handler.TupleActionProcessor import TupleActionProcessor

from peek_plugin_diagram_trace._private.PluginNames import diagramTraceFilt
from peek_plugin_diagram_trace._private.PluginNames import diagramTraceActionProcessorName
from .controller.MainController import MainController


def makeTupleActionProcessorHandler(mainController: MainController):
    processor = TupleActionProcessor(
        tupleActionProcessorName=diagramTraceActionProcessorName,
        additionalFilt=diagramTraceFilt,
        defaultDelegate=mainController)
    return processor
