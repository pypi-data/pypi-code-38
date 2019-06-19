from collections import defaultdict
from typing import Dict

from peek_plugin_graphdb.tuples.GraphDbLinkedEdge import GraphDbLinkedEdge
from peek_plugin_graphdb.tuples.GraphDbLinkedVertex import GraphDbLinkedVertex


class GraphDbLinkedSegment:
    """ Linked Segment

    This tuple is the publicly exposed Segment

    """
    #:  The unique key of this segment
    key: str = None

    #:  The model set of this segment
    modelSetKey: str = None

    #:  The edges
    edgeByKey: Dict[str, GraphDbLinkedEdge] = None

    #:  The vertexes
    vertexByKey: Dict[str, GraphDbLinkedVertex] = None

    def __init__(self):
        self.edgeByKey = {}
        self.vertexByKey = {}

    def unpackJson(self, jsonDict: Dict, segmentKey: str,
                   modelSetKey: str) -> 'GraphDbLinkedSegment':
        self.key = segmentKey
        self.modelSetKey = modelSetKey

        linksToSegmentKeysByVertexKey = defaultdict(list)
        for jsonLink in jsonDict["links"]:
            linksToSegmentKeysByVertexKey[jsonLink["vk"]].append(jsonLink["sk"])

        for jsonVertex in jsonDict["vertexes"]:
            newVertex = GraphDbLinkedVertex()
            newVertex._k = jsonVertex["k"]
            newVertex._p = jsonVertex["p"]
            newVertex._e = []
            newVertex._sk = []
            if newVertex.key in linksToSegmentKeysByVertexKey:
                newVertex._sk = linksToSegmentKeysByVertexKey[newVertex.key]
            self.vertexByKey[newVertex.key] = newVertex

        for jsonEdge in jsonDict["edges"]:
            newEdge = GraphDbLinkedEdge()
            newEdge._k = jsonEdge["k"]
            newEdge._p = jsonEdge["p"]
            newEdge._s = self.vertexByKey[jsonEdge["sk"]]
            newEdge._d = self.vertexByKey[jsonEdge["dk"]]
            newEdge.srcVertex._e.append(newEdge)
            newEdge.dstVertex._e.append(newEdge)
            self.edgeByKey[newEdge.key] = newEdge

        return self
