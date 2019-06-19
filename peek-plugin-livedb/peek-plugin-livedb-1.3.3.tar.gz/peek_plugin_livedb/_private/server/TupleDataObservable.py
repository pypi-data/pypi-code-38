from peek_plugin_livedb._private.PluginNames import livedbFilt
from peek_plugin_livedb._private.PluginNames import livedbObservableName
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler


def makeTupleDataObservableHandler(ormSessionCreator):
    """" Make Tuple Data Observable Handler

    This method creates the observable object, registers the tuple providers and then
    returns it.

    :param ormSessionCreator: A function that returns a SQLAlchemy session when called

    :return: An instance of :code:`TupleDataObservableHandler`

    """
    tupleObservable = TupleDataObservableHandler(
        observableName=livedbObservableName,
        additionalFilt=livedbFilt)

    # # Register TupleProviders here
    # tupleObservable.addTupleProvider(StringIntTuple.tupleName(),
    #                                  StringIntTupleProvider(ormSessionCreator))
    return tupleObservable
