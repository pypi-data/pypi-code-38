from peek_core_device._private.PluginNames import deviceFilt
from peek_core_device._private.PluginNames import deviceObservableName
from peek_core_device._private.server.tuple_providers.DeviceInfoTupleProvider import \
    DeviceInfoTupleProvider
from peek_core_device._private.server.tuple_providers.DeviceUpdateTupleProvider import \
    DeviceUpdateTupleProvider
from peek_core_device._private.storage.DeviceInfoTuple import DeviceInfoTuple
from peek_core_device._private.storage.DeviceUpdateTuple import DeviceUpdateTuple
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler


def makeTupleDataObservableHandler(ormSessionCreator):
    """" Make Tuple Data Observable Handler

    This method creates the observable object, registers the tuple providers and then
    returns it.

    :param ormSessionCreator: A function that returns a SQLAlchemy session when called

    :return: An instance of :code:`TupleDataObservableHandler`

    """
    tupleObservable = TupleDataObservableHandler(
        observableName=deviceObservableName,
        additionalFilt=deviceFilt)

    # Register TupleProviders here
    tupleObservable.addTupleProvider(DeviceUpdateTuple.tupleName(),
                                     DeviceUpdateTupleProvider(ormSessionCreator))

    tupleObservable.addTupleProvider(DeviceInfoTuple.tupleName(),
                                     DeviceInfoTupleProvider(ormSessionCreator))
    return tupleObservable
