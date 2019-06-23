from typing import List, Dict, Optional

from peek_plugin_diagram._private.storage.ModelSet import ModelSet
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler
from vortex.handler.TupleDataObserverClient import TupleDataObserverClient


class ModelSetCacheController:
    """ Lookup Cache Controller

    This class caches the lookups in each client.

    """

    def __init__(self, tupleObserver: TupleDataObserverClient):
        self._tupleObserver = tupleObserver
        self._tupleObservable = None

        #: This stores the cache of grid data for the clients
        self._cache: Dict[int, ModelSet] = {}

    def setTupleObservable(self, tupleObservable: TupleDataObservableHandler):
        self._tupleObservable = tupleObservable

    def start(self):
        (self._tupleObserver
         .subscribeToTupleSelector(TupleSelector(ModelSet.tupleName(), {}))
         .subscribe(self._processNewTuples))

    def shutdown(self):
        self._tupleObservable = None
        self._tupleObserver = None
        self._cache = {}

    def _processNewTuples(self, tuples):
        if not tuples:
            return

        self._cache = {c.id: c for c in tuples}

        self._tupleObservable.notifyOfTupleUpdate(
            TupleSelector(ModelSet.tupleName(), {})
        )

    @property
    def modelSets(self) -> List[ModelSet]:
        return list(self._cache.values())
