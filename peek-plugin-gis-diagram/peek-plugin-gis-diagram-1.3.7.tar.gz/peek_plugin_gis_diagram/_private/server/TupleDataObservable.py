from peek_plugin_diagram.server.DiagramViewerApiABC import DiagramViewerApiABC
from peek_plugin_diagram.tuples.model.DiagramCoordSetTuple import DiagramCoordSetTuple
from peek_plugin_gis_diagram._private.PluginNames import gisDiagramFilt
from peek_plugin_gis_diagram._private.PluginNames import gisDiagramObservableName

from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler
from .tuple_providers.CoordSetTupleProvider import CoordSetTupleProvider


def makeTupleDataObservableHandler(diagramPluginViewerApi: DiagramViewerApiABC,
                                   ormSessionCreator):
    """" Make Tuple Data Observable Handler

    This method creates the observable object, registers the tuple providers and then
    returns it.

    :param diagramPluginViewerApi: The ViewerAPI for the peek_plugin_diagram
    :param ormSessionCreator: A function that returns a SQLAlchemy session when called

    :return: An instance of :code:`TupleDataObservableHandler`

    """
    tupleObservable = TupleDataObservableHandler(
        observableName=gisDiagramObservableName,
        additionalFilt=gisDiagramFilt)

    # Register TupleProviders here
    tupleObservable.addTupleProvider(DiagramCoordSetTuple.tupleName(),
                                     CoordSetTupleProvider(diagramPluginViewerApi))
    return tupleObservable
