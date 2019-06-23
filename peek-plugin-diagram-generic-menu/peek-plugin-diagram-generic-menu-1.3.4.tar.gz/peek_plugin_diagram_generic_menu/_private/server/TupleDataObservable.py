from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_plugin_diagram_generic_menu._private.PluginNames import diagramGenericMenuFilt
from peek_plugin_diagram_generic_menu._private.PluginNames import diagramGenericMenuObservableName

from .tuple_providers.DiagramGenericMenuTupleProvider import DiagramGenericMenuTupleProvider
from peek_plugin_diagram_generic_menu._private.storage.DiagramGenericMenuTuple import DiagramGenericMenuTuple


def makeTupleDataObservableHandler(ormSessionCreator):
    """" Make Tuple Data Observable Handler

    This method creates the observable object, registers the tuple providers and then
    returns it.

    :param ormSessionCreator: A function that returns a SQLAlchemy session when called

    :return: An instance of :code:`TupleDataObservableHandler`

    """
    tupleObservable = TupleDataObservableHandler(
                observableName=diagramGenericMenuObservableName,
                additionalFilt=diagramGenericMenuFilt)

    # Register TupleProviders here
    tupleObservable.addTupleProvider(DiagramGenericMenuTuple.tupleName(),
                                     DiagramGenericMenuTupleProvider(ormSessionCreator))
    return tupleObservable
