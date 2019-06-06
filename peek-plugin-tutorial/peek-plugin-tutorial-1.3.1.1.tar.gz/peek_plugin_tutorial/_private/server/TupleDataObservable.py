from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_plugin_tutorial._private.PluginNames import tutorialFilt
from peek_plugin_tutorial._private.PluginNames import tutorialObservableName

from .tuple_providers.StringIntTupleProvider import StringIntTupleProvider
from peek_plugin_tutorial._private.storage.StringIntTuple import StringIntTuple


def makeTupleDataObservableHandler(ormSessionCreator):
    """" Make Tuple Data Observable Handler

    This method creates the observable object, registers the tuple providers and then
    returns it.

    :param ormSessionCreator: A function that returns a SQLAlchemy session when called

    :return: An instance of :code:`TupleDataObservableHandler`

    """
    tupleObservable = TupleDataObservableHandler(
                observableName=tutorialObservableName,
                additionalFilt=tutorialFilt)

    # Register TupleProviders here
    tupleObservable.addTupleProvider(StringIntTuple.tupleName(),
                                     StringIntTupleProvider(ormSessionCreator))
    return tupleObservable
