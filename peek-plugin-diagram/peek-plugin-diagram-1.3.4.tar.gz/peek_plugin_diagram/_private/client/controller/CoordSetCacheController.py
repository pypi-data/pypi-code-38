from typing import List, Dict, Optional

from peek_plugin_diagram._private.storage.ModelSet import ModelCoordSet
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler
from vortex.handler.TupleDataObserverClient import TupleDataObserverClient


class CoordSetCacheController:
    """ Lookup Cache Controller

    This class caches the lookups in each client.

    """

    def __init__(self, tupleObserver: TupleDataObserverClient):
        self._tupleObserver = tupleObserver
        self._tupleObservable = None

        #: This stores the cache of grid data for the clients
        self._coordSetCache: Dict[int, ModelCoordSet] = {}

    def setTupleObservable(self, tupleObservable: TupleDataObservableHandler):
        self._tupleObservable = tupleObservable

    def start(self):
        (self._tupleObserver
         .subscribeToTupleSelector(TupleSelector(ModelCoordSet.tupleName(), {}))
         .subscribe(self._processNewTuples))

    def shutdown(self):
        self._tupleObservable = None
        self._tupleObserver = None
        self._coordSetCache = {}

    def _processNewTuples(self, coordSetTuples):
        if not coordSetTuples:
            return

        self._coordSetCache = {c.id: c for c in coordSetTuples}

        self._tupleObservable.notifyOfTupleUpdate(
            TupleSelector(ModelCoordSet.tupleName(), {})
        )

    @property
    def coordSets(self) -> List[ModelCoordSet]:
        return list(self._coordSetCache.values())

    def coordSetForId(self, coordSetId: int) -> Optional[ModelCoordSet]:
        return self._coordSetCache.get(coordSetId)
