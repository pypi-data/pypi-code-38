from abc import ABCMeta, abstractmethod
from typing import List

from twisted.internet.defer import Deferred


class GraphDbApiABC(metaclass=ABCMeta):

    @abstractmethod
    def createOrUpdateSegment(self, graphSegmentEncodedPayload: bytes) -> Deferred:
        """ Create or Update Segment

        Add new Graph Segments to the GraphDB

        :param graphSegmentEncodedPayload: An encoded payload containing
            :code:`GraphDbImportSegmentTuple`
        :return: A deferred that fires when the work is complete

        """

    @abstractmethod
    def deleteSegments(self, modelSetKey: str, importGroupHashes: List[str]) -> Deferred:
        """ Delete Segments

        Delete a Graph Segment from the GraphDB.

        :param modelSetKey: The model set key to delete Graph Segments from
        :param importGroupHashes: A list of the keys of the segments to delete
        :return: A deferred that fires when the work is complete

        """

    def createOrUpdateTraceConfig(self, traceEncodedPayload: bytes) -> Deferred:
        """ Create or Update Trace Config

        Add new trace configs to the GraphDB

        :param traceEncodedPayload: An encoded payload containing
            :code:`GraphDbTraceConfigTuple`
        :return: A deferred that fires when the work is complete

        """

    def deleteTraceConfig(self, modelSetKey: str, traceConfigKeys: List[str]) -> Deferred:
        """ Delete Trace Config

        Delete a trace config from the GraphDB.

        :param modelSetKey: The model set key to delete documents from
        :param traceConfigKeys: The keys of the Trace Configs to delete
        :return: A deferred that fires when the work is complete

        """
