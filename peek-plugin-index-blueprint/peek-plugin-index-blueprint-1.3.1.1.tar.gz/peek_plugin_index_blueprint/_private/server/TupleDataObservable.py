from peek_plugin_base.storage.DbConnection import DbSessionCreator
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_plugin_index_blueprint._private.PluginNames import indexBlueprintFilt
from peek_plugin_index_blueprint._private.PluginNames import indexBlueprintObservableName
from peek_plugin_index_blueprint._private.server.tuple_providers.ModelSetTupleProvider import \
    ModelSetTupleProvider
from peek_plugin_index_blueprint._private.server.tuple_providers.ThingTypeTupleProvider import \
    ThingTypeTupleProvider
from peek_plugin_index_blueprint._private.tuples.ThingIndexServerStatusTuple import \
    ThingIndexServerStatusTuple
from peek_plugin_index_blueprint.tuples.IndexBlueprintModelSetTuple import \
    IndexBlueprintModelSetTuple
from peek_plugin_index_blueprint.tuples.ThingTypeTuple import ThingTypeTuple
from .controller.ThingIndexStatusController import ThingIndexStatusController
from .tuple_providers.ThingIndexServerStatusTupleProvider import \
    ThingIndexServerStatusTupleProvider


def makeTupleDataObservableHandler(
        dbSessionCreator: DbSessionCreator,
        thingIndexStatusController: ThingIndexStatusController):
    """" Make Tuple Data Observable Handler

    This method creates the observable object, registers the tuple providers and then
    returns it.

    :param dbSessionCreator: A function that returns a SQLAlchemy session when called
    :param thingIndexStatusController:

    :return: An instance of :code:`TupleDataObservableHandler`

    """
    tupleObservable = TupleDataObservableHandler(
        observableName=indexBlueprintObservableName,
        additionalFilt=indexBlueprintFilt)

    # Admin status tuple
    tupleObservable.addTupleProvider(
        ThingIndexServerStatusTuple.tupleName(),
        ThingIndexServerStatusTupleProvider(thingIndexStatusController)
    )

    # ThingIndex Type Tuple
    tupleObservable.addTupleProvider(ThingTypeTuple.tupleName(),
                                     ThingTypeTupleProvider(dbSessionCreator))

    # Model Set Tuple
    tupleObservable.addTupleProvider(IndexBlueprintModelSetTuple.tupleName(),
                                     ModelSetTupleProvider(dbSessionCreator))

    return tupleObservable
