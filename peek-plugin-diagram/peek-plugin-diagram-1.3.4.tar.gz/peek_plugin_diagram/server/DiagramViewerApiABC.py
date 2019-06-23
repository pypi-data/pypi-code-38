from typing import List

from abc import ABCMeta, abstractmethod
from twisted.internet.defer import Deferred


class DiagramViewerApiABC(metaclass=ABCMeta):
    @abstractmethod
    def getCoordSets(self, modelSetKey: str) -> Deferred:
        """ Get Coordinate Set Tuples

        Returns a list of coordinate set tuples for a model set name

        :param modelSetKey:  The name of the model set query for.

        :return: A deferred that fires with a list of tuples
                List[DiagramCoordSetTuple]

        """
