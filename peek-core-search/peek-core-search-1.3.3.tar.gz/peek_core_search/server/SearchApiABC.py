from abc import ABCMeta, abstractmethod
from typing import List

from twisted.internet.defer import Deferred

from peek_core_search.tuples.ImportSearchObjectTuple import ImportSearchObjectTuple


class SearchApiABC(metaclass=ABCMeta):

    @abstractmethod
    def importSearchObjects(self, searchObjectsEncodedPayload: bytes) -> Deferred:
        """ Import Search Objects

        This method imports a group of objects into the search.

        :param searchObjectsEncodedPayload: A group/list of objects to import into the search
                The format of the encodedPayload tuples is List[ImportSearchObjectTuple]
                using Payload(tuples=tuples).toEncodedPayload()

        :return: A deferred that fires when the objects are queued for indexing.

        """

    @abstractmethod
    def removeSearchObjects(self, importGroupHashes: List[str]) -> Deferred:
        """ Remove Search Objects

        This method removes a group of objects from the search that have "importGroupHashes"

        :param importGroupHashes: A list of strings matching the "importGroupHash"
            provided when the objects were imported.
        :return: A deferred that fires when the objects are queued for deleting.

        """
