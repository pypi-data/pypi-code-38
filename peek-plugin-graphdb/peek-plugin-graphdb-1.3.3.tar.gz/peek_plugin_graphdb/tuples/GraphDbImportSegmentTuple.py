import hashlib
import json
from typing import List

import ujson
from vortex.Tuple import addTupleType, TupleField, Tuple

from peek_plugin_graphdb._private.PluginNames import graphDbTuplePrefix
from peek_plugin_graphdb.tuples.GraphDbImportEdgeTuple import GraphDbImportEdgeTuple
from peek_plugin_graphdb.tuples.GraphDbImportSegmentLinkTuple import \
    GraphDbImportSegmentLinkTuple
from peek_plugin_graphdb.tuples.GraphDbImportVertexTuple import GraphDbImportVertexTuple


@addTupleType
class GraphDbImportSegmentTuple(Tuple):
    """ Import Segment Tuple

    This tuple is the publicly exposed Segment

    """
    __tupleType__ = graphDbTuplePrefix + 'GraphDbImportSegmentTuple'

    #:  The unique key of this segment
    key: str = TupleField()

    #:  The model set of this segment
    modelSetKey: str = TupleField()

    #:  The edges
    edges: List[GraphDbImportEdgeTuple] = TupleField([])

    #:  The vertexes
    vertexes: List[GraphDbImportVertexTuple] = TupleField([])

    #:  The links to the other segments
    links: List[GraphDbImportSegmentLinkTuple] = TupleField([])

    #:  The hash of this import group
    importGroupHash: str = TupleField()

    def generateSegmentKey(self) -> str:
        """ Generate Segment Key

        This method generates a unique has of this segment based on its internal
        contents, that is, the edges, vertexes but not links to other segments.

        """

        m = hashlib.md5()
        m.update(b'zeroth item padding')

        for edge in sorted(self.edges, key=lambda e: e.key):
            m.update(str(edge).encode())

        for vertex in sorted(self.vertexes, key=lambda v: v.key):
            m.update(str(vertex).encode())

        return m.hexdigest()

    def generateSegmentHash(self) -> str:
        """ Generate Segment Hash

        This method generates a unique has of this segment based on its internal
        and external contents, that is, the edges, vertexes
        AND the links to other segments.

        """

        m = hashlib.md5()
        m.update(b'zeroth item padding')

        for edge in sorted(self.edges, key=lambda e: e.key):
            m.update(ujson.dumps(edge.tupleToSqlaBulkInsertDict(), sort_keys=True)
                     .encode())

        for vertex in sorted(self.vertexes, key=lambda v: v.key):
            m.update(ujson.dumps(vertex.tupleToSqlaBulkInsertDict(), sort_keys=True)
                     .encode())

        for link in sorted(self.links, key=lambda l: l.vertexKey + l.segmentKey):
            m.update(ujson.dumps(link.tupleToSqlaBulkInsertDict(), sort_keys=True)
                     .encode())

        m.update(self.key.encode())
        m.update(self.modelSetKey.encode())

        return m.hexdigest()

    def packJson(self) -> str:
        jsonDict = dict(
            edges=[i.packJsonDict() for i in self.edges],
            links=[i.packJsonDict() for i in self.links],
            vertexes=[i.packJsonDict() for i in self.vertexes]
        )
        return json.dumps(jsonDict, sort_keys=True, indent='')
