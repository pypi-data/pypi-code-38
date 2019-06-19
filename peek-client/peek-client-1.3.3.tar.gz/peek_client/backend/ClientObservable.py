import logging

from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

logger = logging.getLogger(__name__)

peekClientObservableName = "peek_client"

observable = TupleDataObservableHandler(
    observableName=peekClientObservableName,
    additionalFilt={"plugin": "peek_client"},
    subscriptionsEnabled=True)

# observable.addTupleProvider(PluginAppTileTuple.tupleName(), HomeAppTileTupleProvider())
