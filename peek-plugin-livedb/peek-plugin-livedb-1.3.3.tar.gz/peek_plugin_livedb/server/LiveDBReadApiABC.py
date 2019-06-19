from abc import ABCMeta, abstractmethod
from typing import Optional, List

from rx.subjects import Subject
from twisted.internet.defer import Deferred


class LiveDBReadApiABC(metaclass=ABCMeta):
    @abstractmethod
    def priorityKeysObservable(self, modelSetName: str) -> Subject:
        """ Priority Live DB Key Observable

        This observable emits list of keys that the live db acquisition plugins should
        prioritised, these keys will be monitored until the next
        priorityLiveDbKey update.

        This list will represent keys relating to the objects that are
        currently being viewed.

        :param modelSetName:  The name of the model set of the keys to observe.

        :return: An observable that emits a List[str].

        """

    @abstractmethod
    def pollKeysObservable(self, modelSetName: str) -> Subject:
        """ Poll Live DB Key Observable

        This observable emits list of keys that the live db acquisition plugins should
        poll ONCE.

        This list will represent keys relating to the objects that are
        currently being viewed.

        :param modelSetName:  The name of the model set of the keys to observe.

        :return: An observable that emits a List[str].

        """

    @abstractmethod
    def itemAdditionsObservable(self, modelSetName: str) -> Subject:
        """ Live DB Tuple Added Items Observable

        Return an observable that fires when livedb items are added

        :param modelSetName: The name of the model set for the live db

        :return: An observable that fires when keys are removed from the live db
        :rtype: An observable that emits List[LiveDbDisplayValueTuple]

        """

    @abstractmethod
    def itemDeletionsObservable(self, modelSetName: str) -> Subject:
        """ Live DB Tuple Removed Items Observable

        Return an observable that fires when livedb items are removed

        :param modelSetName:  The name of the model set for the live db

        :return: An observable that fires when keys are removed from the live db
        :rtype: An observable that emits List[str]

        """

    @abstractmethod
    def bulkLoadDeferredGenerator(self, modelSetName: str,
                                  keyList: Optional[List[str]] = None,
                                  chunkSize: int = 2500) -> Deferred:
        """ Live DB Tuples

        Return a generator that returns deferreds that are fired with chunks of the
         entire live db.

        :param chunkSize: The number of items to return for each chunk
        :param modelSetName:  The name of the model set for the live db
        :param keyList:  An optional list of keys that the data is required for

        :return: A deferred that fires with a list of tuples
        :rtype: C{LiveDbDisplayValueTuple}

        This is served up in chunks to prevent ballooning the memory usage.

        Here is an example of how to use this method

        ::

                @inlineCallbacks
                def loadFromDiagramApi(diagramLiveDbApi:DiagramLiveDbApiABC):
                    deferredGenerator = diagramLiveDbApi.bulkLoadDeferredGenerator("modelName")

                    while True:
                        d = next(deferredGenerator)
                        liveDbValueTuples = yield d # List[LiveDbDisplayValueTuple]

                        # The end of the list is marked my an empty result
                        if not liveDbValueTuples:
                            break

                        # TODO, do something with this chunk of liveDbValueTuples



        """

    @abstractmethod
    def rawValueUpdatesObservable(self, modelSetName: str) -> Subject:
        """ Raw Value Update Observable

        Return an observable that fires with lists of C{LiveDbRawValueTuple} tuples
        containing updates to live db values.

        :param modelSetName:  The name of the model set for the live db

        :return: An observable that fires when values are updated in the livedb
        :rtype: Subject[List[LiveDbRawValueTuple]]

        """

    @abstractmethod
    def displayValueUpdatesObservable(self, modelSetName: str) -> Subject:
        """ Display Value Update Observable

        Return an observable that fires with lists of C{LiveDbDisplayValueTuple} tuples
        containing updates to live db values.

        :param modelSetName:  The name of the model set for the live db

        :return: An observable that fires when values are updated in the livedb
        :rtype: An observable that fires with List[LiveDbDisplayValueTuple]

        """
