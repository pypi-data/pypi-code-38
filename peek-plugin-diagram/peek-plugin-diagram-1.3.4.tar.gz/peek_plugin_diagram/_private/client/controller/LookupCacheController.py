from typing import List

from copy import copy

from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.storage.Display import DispLevel, DispTextStyle, \
    DispLayer, DispColor, DispLineStyle
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler
from vortex.handler.TupleDataObserverClient import TupleDataObserverClient

lookupCachePayloadFilt = dict(key="client.lookup.update")
lookupCachePayloadFilt.update(diagramFilt)


class LookupCacheController:
    """ Lookup Cache Controller

    This class caches the lookups in each client.

    """
    #: This stores the cache of grid data for the clients
    _levelLookups: List[DispLevel] = None
    _layerLookups: List[DispLayer] = None
    _colorLookups: List[DispColor] = None
    _lineStyleLookups: List[DispLineStyle] = None
    _textStyleLookups: List[DispTextStyle] = None

    def __init__(self, tupleObserver: TupleDataObserverClient):
        self._tupleObserver = tupleObserver
        self._tupleObservable = None

    def setTupleObservable(self, tupleObservable: TupleDataObservableHandler):
        self._tupleObservable = tupleObservable

    def start(self):
        (self._tupleObserver
         .subscribeToTupleSelector(TupleSelector(DispLevel.tupleType(), {}))
         .subscribe(self._processNewTuples))

        (self._tupleObserver
         .subscribeToTupleSelector(TupleSelector(DispLayer.tupleType(), {}))
         .subscribe(self._processNewTuples))

        (self._tupleObserver
         .subscribeToTupleSelector(TupleSelector(DispColor.tupleType(), {}))
         .subscribe(self._processNewTuples))

        (self._tupleObserver
         .subscribeToTupleSelector(TupleSelector(DispLineStyle.tupleType(), {}))
         .subscribe(self._processNewTuples))

        (self._tupleObserver
         .subscribeToTupleSelector(TupleSelector(DispTextStyle.tupleType(), {}))
         .subscribe(self._processNewTuples))

    def shutdown(self):
        self._tupleObservable = None
        self._tupleObserver = None

        self._levelLookups = []
        self._layerLookups = []
        self._colorLookups = []
        self._lineStyleLookups = []
        self._textStyleLookups = []

    def _processNewTuples(self, lookupTuples):

        if not lookupTuples:
            return

        firstTupleType = lookupTuples[0].tupleType()
        if DispLevel.tupleType() == firstTupleType:
            self._levelLookups = lookupTuples

        elif DispLayer.tupleType() == firstTupleType:
            self._layerLookups = lookupTuples

        elif DispColor.tupleType() == firstTupleType:
            self._colorLookups = lookupTuples

        elif DispLineStyle.tupleType() == firstTupleType:
            self._lineStyleLookups = lookupTuples

        elif DispTextStyle.tupleType() == firstTupleType:
            self._textStyleLookups = lookupTuples

        else:
            raise NotImplementedError(
                "Cache not implemented for %s" % firstTupleType)

        self._tupleObservable.notifyOfTupleUpdate(
            TupleSelector(firstTupleType, {})
        )

    def lookups(self, lookupTupleType) -> List:
        if DispLevel.tupleType() == lookupTupleType:
            return copy(self._levelLookups)

        if DispLayer.tupleType() == lookupTupleType:
            return copy(self._layerLookups)

        if DispColor.tupleType() == lookupTupleType:
            return copy(self._colorLookups)

        if DispLineStyle.tupleType() == lookupTupleType:
            return copy(self._lineStyleLookups)

        if DispTextStyle.tupleType() == lookupTupleType:
            return copy(self._textStyleLookups)

        raise NotImplementedError("Cache not implemented for %s" % lookupTupleType)
