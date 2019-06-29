from abc import ABCMeta, abstractmethod
from typing import List

from twisted.internet.defer import Deferred


class DocDbApiABC(metaclass=ABCMeta):

    @abstractmethod
    def createOrUpdateDocuments(self, documentsEncodedPayload: bytes) -> Deferred:
        """ Create or Update Documents

        Add new documents to the document db

        :param documentsEncodedPayload: An encoded payload containing :code:`List[DocumentTuple]`
        :return: A deferred that fires when the creates or updates are complete

        """

    @abstractmethod
    def deleteDocuments(self, modelSetKey: str, keys: List[str]) -> Deferred:
        """ Delete Documents

        Delete documents from the document db.

        :param modelSetKey: the model set key to delete documents from
        :param keys: A list of keys for documents to delete
        :return: A deferred that fires when the delete is complete

        """
