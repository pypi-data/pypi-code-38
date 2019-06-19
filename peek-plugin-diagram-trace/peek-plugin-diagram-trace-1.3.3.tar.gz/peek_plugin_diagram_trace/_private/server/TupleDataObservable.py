from peek_plugin_diagram_trace._private.PluginNames import diagramTraceFilt
from peek_plugin_diagram_trace._private.PluginNames import diagramTraceObservableName
from peek_plugin_diagram_trace._private.server.tuple_providers.SettingPropertyTupleProvider import \
    SettingPropertyTupleProvider
from peek_plugin_diagram_trace._private.storage.Setting import SettingProperty
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler


def makeTupleDataObservableHandler(ormSessionCreator):
    """" Make Tuple Data Observable Handler

    This method creates the observable object, registers the tuple providers and then
    returns it.

    :param ormSessionCreator: A function that returns a SQLAlchemy session when called

    :return: An instance of :code:`TupleDataObservableHandler`

    """
    tupleObservable = TupleDataObservableHandler(
        observableName=diagramTraceObservableName,
        additionalFilt=diagramTraceFilt)

    tupleObservable.addTupleProvider(SettingProperty.tupleName(),
                                     SettingPropertyTupleProvider(ormSessionCreator))

    return tupleObservable
