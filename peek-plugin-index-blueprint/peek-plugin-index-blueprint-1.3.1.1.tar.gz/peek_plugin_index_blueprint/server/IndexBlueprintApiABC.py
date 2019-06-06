from abc import ABCMeta, abstractmethod
from typing import List

from twisted.internet.defer import Deferred


class IndexBlueprintApiABC(metaclass=ABCMeta):

    @abstractmethod
    def createOrUpdateThings(self, thingsEncodedPayload: bytes) -> Deferred:
        """ Create or Update Things

        Add new thingIndexs to the thingIndex db

        :param thingsEncodedPayload: An encoded payload containing :code:`List[ThingTuple]`
        :return: A deferred that fires when the creates or updates are complete

        """

    @abstractmethod
    def removeThings(self, modelSetKey: str, importGroupHashs: List[str]) -> Deferred:
        """ Delete ThingIndexs

        Delete thingIndexs from the thingIndex db.

        :param modelSetKey: the model set key to delete thingIndexs from
        :param importGroupHashs: A list of importGroupHash values to delete
        :return: A deferred that fires when the delete is complete

        """
