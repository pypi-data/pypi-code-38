from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_graphdb._private.PluginNames import graphDbFilt
from peek_plugin_graphdb._private.PluginNames import graphDbObservableName
from peek_plugin_graphdb._private.server.tuple_providers.ModelSetTupleProvider import \
    ModelSetTupleProvider
from peek_plugin_graphdb._private.storage.GraphDbModelSet import GraphDbModelSet
from peek_plugin_graphdb._private.tuples.ServerStatusTuple import ServerStatusTuple
from peek_plugin_graphdb.tuples.GraphDbModelSetTuple import GraphDbModelSetTuple
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from .controller.SegmentIndexStatusController import SegmentIndexStatusController
from .tuple_providers.ServerStatusTupleProvider import ServerStatusTupleProvider


def makeTupleDataObservableHandler(dbSessionCreator: DbSessionCreator,
                                   segmentStatusController: SegmentIndexStatusController):
    """" Make Tuple Data Observable Handler

    This method creates the observable object, registers the tuple providers and then
    returns it.

    :param dbSessionCreator: A function that returns a SQLAlchemy session when called
    :param segmentStatusController:

    :return: An instance of :code:`TupleDataObservableHandler`

    """
    tupleObservable = TupleDataObservableHandler(
        observableName=graphDbObservableName,
        additionalFilt=graphDbFilt)

    # Admin status tuple
    tupleObservable.addTupleProvider(
        ServerStatusTuple.tupleName(),
        ServerStatusTupleProvider(segmentStatusController)
    )

    # Model Set Tuple
    tupleObservable.addTupleProvider(GraphDbModelSetTuple.tupleName(),
                                     ModelSetTupleProvider(dbSessionCreator))

    return tupleObservable
