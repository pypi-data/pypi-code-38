from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_plugin_branch._private.PluginNames import branchFilt
from peek_plugin_branch._private.PluginNames import branchObservableName
from peek_plugin_branch.tuples.BranchDetailTuple import BranchDetailTuple
from .tuple_providers.BranchDetailTupleProvider import BranchDetailTupleProvider


def makeTupleDataObservableHandler(ormSessionCreator):
    """" Make Tuple Data Observable Handler

    This method creates the observable object, registers the tuple providers and then
    returns it.

    :param ormSessionCreator: A function that returns a SQLAlchemy session when called

    :return: An instance of :code:`TupleDataObservableHandler`

    """
    tupleObservable = TupleDataObservableHandler(
                observableName=branchObservableName,
                additionalFilt=branchFilt)

    # Register TupleProviders here
    tupleObservable.addTupleProvider(BranchDetailTuple.tupleName(),
                                     BranchDetailTupleProvider(ormSessionCreator))
    return tupleObservable
