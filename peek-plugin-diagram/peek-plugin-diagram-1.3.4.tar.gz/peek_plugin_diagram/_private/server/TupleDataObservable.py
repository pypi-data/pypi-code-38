from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.PluginNames import diagramObservableName
from peek_plugin_diagram._private.server.controller.BranchLiveEditController import \
    BranchLiveEditController
from peek_plugin_diagram._private.server.controller.StatusController import \
    StatusController
from peek_plugin_diagram._private.server.tuple_providers.BranchKeyToIdMapProvider import \
    BranchKeyToIdMapTupleProvider
from peek_plugin_diagram._private.server.tuple_providers.BranchLiveEditTupleProvider import \
    BranchLiveEditTupleProvider
from peek_plugin_diagram._private.server.tuple_providers.DiagramLoaderStatusTupleProvider import \
    DiagramLoaderStatusTupleProvider
from peek_plugin_diagram._private.server.tuple_providers.ServerCoordSetTupleProvider import \
    ServerCoordSetTupleProvider
from peek_plugin_diagram._private.server.tuple_providers.ServerLookupTupleProvider import \
    ServerLookupTupleProvider
from peek_plugin_diagram._private.server.tuple_providers.ServerModelSetTupleProvider import \
    ServerModelSetTupleProvider
from peek_plugin_diagram._private.storage.Display import DispLevel, DispLayer, DispColor, \
    DispLineStyle, DispTextStyle
from peek_plugin_diagram._private.storage.ModelSet import ModelCoordSet, ModelSet
from peek_plugin_diagram._private.tuples.DiagramImporterStatusTuple import \
    DiagramImporterStatusTuple
from peek_plugin_diagram._private.tuples.branch.BranchKeyToIdMapTuple import \
    BranchKeyToIdMapTuple
from peek_plugin_diagram._private.tuples.branch.BranchLiveEditTuple import \
    BranchLiveEditTuple


def makeTupleDataObservableHandler(ormSessionCreator,
                                   statusController: StatusController,
                                   branchLiveEditController: BranchLiveEditController):
    """" Make Tuple Data Observable Handler

    This method creates the observable object, registers the tuple providers and then
    returns it.

    :param branchLiveEditController:
    :param ormSessionCreator: A callable that returns an SQLAlchemy session
    :param statusController: The status controller
    :return: An instance of :code:`TupleDataObservableHandler`

    """
    tupleObservable = TupleDataObservableHandler(
        observableName=diagramObservableName,
        additionalFilt=diagramFilt)

    # Register TupleProviders here
    tupleObservable.addTupleProvider(DiagramImporterStatusTuple.tupleName(),
                                     DiagramLoaderStatusTupleProvider(statusController))

    # Register TupleProviders here
    tupleObservable.addTupleProvider(ModelSet.tupleName(),
                                     ServerModelSetTupleProvider(ormSessionCreator))

    # Register TupleProviders here
    tupleObservable.addTupleProvider(ModelCoordSet.tupleName(),
                                     ServerCoordSetTupleProvider(ormSessionCreator))

    # Register TupleProviders here
    tupleObservable.addTupleProvider(BranchKeyToIdMapTuple.tupleName(),
                                     BranchKeyToIdMapTupleProvider(ormSessionCreator))

    # Register TupleProviders here
    lookupTupleProvider = ServerLookupTupleProvider(ormSessionCreator)
    tupleObservable.addTupleProvider(DispLevel.tupleName(), lookupTupleProvider)
    tupleObservable.addTupleProvider(DispLayer.tupleName(), lookupTupleProvider)
    tupleObservable.addTupleProvider(DispColor.tupleName(), lookupTupleProvider)
    tupleObservable.addTupleProvider(DispLineStyle.tupleName(), lookupTupleProvider)
    tupleObservable.addTupleProvider(DispTextStyle.tupleName(), lookupTupleProvider)

    tupleObservable.addTupleProvider(
        BranchLiveEditTuple.tupleName(),
        BranchLiveEditTupleProvider(branchLiveEditController)
    )

    return tupleObservable
