""" Run Trace

This module contains the logic to perform python side traces.

NOTE: THIS FILE MUST BE KEPT IN SYNC WITH THE TYPESCRIPT VERSION AT :
* peek_plugin_graphdb/plugin-module/_private/tracer-service/PrivateRunTrace.ts


"""
import logging
from collections import namedtuple
from datetime import datetime
from functools import cmp_to_key
from typing import List, Dict, Optional

import pytz

from peek_plugin_graphdb._private.client.controller.FastGraphDb import FastGraphDbModel
from peek_plugin_graphdb.tuples.GraphDbLinkedEdge import GraphDbLinkedEdge
from peek_plugin_graphdb.tuples.GraphDbLinkedSegment import GraphDbLinkedSegment
from peek_plugin_graphdb.tuples.GraphDbLinkedVertex import GraphDbLinkedVertex
from peek_plugin_graphdb.tuples.GraphDbTraceConfigRuleTuple import \
    GraphDbTraceConfigRuleTuple
from peek_plugin_graphdb.tuples.GraphDbTraceConfigTuple import GraphDbTraceConfigTuple
from peek_plugin_graphdb.tuples.GraphDbTraceResultEdgeTuple import \
    GraphDbTraceResultEdgeTuple
from peek_plugin_graphdb.tuples.GraphDbTraceResultTuple import GraphDbTraceResultTuple
from peek_plugin_graphdb.tuples.GraphDbTraceResultVertexTuple import \
    GraphDbTraceResultVertexTuple

logger = logging.getLogger(__name__)

_TraceEdgeParams = namedtuple("_TraceEdgeParams", ["segment", "edge", "vertex"])


class _TraceAbortedWithMessageException(Exception):
    pass


class PrivateRunTrace:
    def __init__(self, result: GraphDbTraceResultTuple,
                 traceConfig: GraphDbTraceConfigTuple,
                 fastDb: FastGraphDbModel,
                 startVertexOrEdgeKey: str, startSegmentKeys: List[str]) -> None:

        self._traceConfigKey = traceConfig.key
        self._traceRules = list(filter(lambda r: r.isEnabled, traceConfig.rules))
        self._traceRules.sort(key=cmp_to_key(self._ruleSortCmp))

        self._fastDb = fastDb
        self._startVertexOrEdgeKey = startVertexOrEdgeKey
        self._startSegmentKeys = startSegmentKeys

        self._alreadyTracedSet = set()
        self._result = result

        self._traceEdgeQueue: List[_TraceEdgeParams] = []

    def run(self) -> None:

        # Sort and filter the rules
        startTime = datetime.now(pytz.utc)

        try:
            # Queue up the starting point and any segments it's in
            for segmentKey in self._startSegmentKeys:
                segment = self._fastDb.getSegment(segmentKey)
                if not segment:
                    raise Exception("Could not find segment %s", segmentKey)

                vertex = segment.vertexByKey.get(self._startVertexOrEdgeKey)
                if vertex:
                    self._traceVertex(segment, vertex)
                    continue

                edge = segment.edgeByKey.get(self._startVertexOrEdgeKey)
                if edge:
                    self._traceEdgeQueue.append(_TraceEdgeParams(segment, edge, None))
                    continue

                raise Exception("Could not find vertex/edge with key %s in segment %s",
                                self._startVertexOrEdgeKey, segment.key)

            # Drain the trace queue
            while self._traceEdgeQueue:
                params = self._traceEdgeQueue.pop()
                self._traceEdge(params.segment, params.edge, params.vertex)

        except _TraceAbortedWithMessageException:
            pass

        if len(self._result.vertexes) and not self._result.edges:
            self._result.traceAbortedMessage = "The trace stopped on the start device."

        # Log the complete
        logger.debug("Trace completed. Trace Config '%s', Start Vertex or Edge '%s'"
                     " %s vertexes, %s edges, error:'%s', in %s",
                     self._traceConfigKey, self._startVertexOrEdgeKey,
                     len(self._result.vertexes), len(self._result.edges),
                     self._result.traceAbortedMessage,
                     (datetime.now(pytz.utc) - startTime))

    # ---------------
    # Rule sort comparator

    def _ruleSortCmp(self, r1, r2):
        R = GraphDbTraceConfigRuleTuple

        # First, Order the rules that apply to the start vertex first
        if r1.applyTo == R.APPLY_TO_START_VERTEX \
                and r2.applyTo != R.APPLY_TO_START_VERTEX:
            return -1

        if r1.applyTo != R.APPLY_TO_START_VERTEX \
                and r2.applyTo == R.APPLY_TO_START_VERTEX:
            return 1

        # Then just compare by order
        if r1.order == r2.order:
            return 0
        return -1 if r1.order < r2.order else 1

    # ---------------
    # Traversing methods

    def _traceEdge(self, segment: GraphDbLinkedSegment,
                   edge: GraphDbLinkedEdge,
                   fromVertex: Optional[GraphDbLinkedVertex] = None):

        if self._checkAlreadyTraced(None, edge.key):
            return

        if not self._matchTraceRules(edge=edge):
            return

        self._addEdge(edge)

        if fromVertex:
            toVertex = edge.getOtherVertex(fromVertex.key)
            self._traceVertex(segment, toVertex)

        else:
            self._traceVertex(segment, edge.srcVertex)
            self._traceVertex(segment, edge.dstVertex)

    def _traceVertex(self, segment: GraphDbLinkedSegment,
                     vertex: GraphDbLinkedVertex) -> None:

        if self._checkAlreadyTraced(vertex.key, None):
            return

        self._addVertex(vertex)

        if not self._matchTraceRules(vertex=vertex):
            return

        for edge in vertex.edges:
            self._traceEdgeQueue.append(_TraceEdgeParams(segment, edge, vertex))

        for segmentKey in vertex.linksToSegmentKeys:
            self._traceEdgesInNextSegment(vertex.key, segmentKey)

    def _traceEdgesInNextSegment(self, vertexKey: str, segmentKey: str):
        segment = self._fastDb.getSegment(segmentKey)
        if not segment:
            raise Exception("Could not find segment %s", segmentKey)

        vertex = segment.vertexByKey.get(vertexKey)
        if not vertex:
            raise Exception(
                "Vertex '%s' is not in segment '%s'" % (vertexKey, segmentKey))

        for edge in vertex.edges:
            self._traceEdgeQueue.append(_TraceEdgeParams(segment, edge, vertex))

    # ---------------
    # Add to result

    def _setTraceAborted(self, message: str):
        self._result.traceAbortedMessage = message
        raise _TraceAbortedWithMessageException()

    def _addEdge(self, edge: GraphDbLinkedEdge):
        self._result.edges.append(GraphDbTraceResultEdgeTuple(
            key=edge.key,
            srcVertexKey=edge.srcVertex.key,
            dstVertexKey=edge.dstVertex.key,
            props=edge.props
        ))

    def _addVertex(self, vertex: GraphDbLinkedVertex):
        self._result.vertexes.append(GraphDbTraceResultVertexTuple(
            key=vertex.key,
            props=vertex.props
        ))

    # ---------------
    # Already Traced State

    def _checkAlreadyTraced(self, vertexKey: Optional[str],
                            edgeKey: Optional[str]) -> bool:
        traced = (vertexKey, edgeKey) in self._alreadyTracedSet
        if not traced:
            self._alreadyTracedSet.add((vertexKey, edgeKey))

        return traced

    # ---------------
    # Match Vertex Rules
    def _matchTraceRules(self, vertex: Optional[GraphDbLinkedVertex] = None,
                         edge: Optional[GraphDbLinkedEdge] = None) -> bool:
        isVertex = vertex is not None
        isEdge = edge is not None
        isStartVertex = isVertex and vertex.key == self._startVertexOrEdgeKey

        props = vertex.props if vertex else edge.props

        for rule in self._traceRules:
            # Accept the conditions in which we'll run this rule
            if rule.applyTo == rule.APPLY_TO_VERTEX and isVertex:
                pass

            elif rule.applyTo == rule.APPLY_TO_EDGE and isEdge:
                pass

            elif rule.applyTo == rule.APPLY_TO_START_VERTEX and isStartVertex:
                pass

            else:
                # Else, this isn't the right rule for this thing, move onto the next
                continue

            # If the rule doesn't match, then continue
            if not self._matchProps(props, rule):
                continue

            # The rule has matched.

            # Apply the action - Continue
            if rule.action == rule.ACTION_CONTINUE_TRACE:
                return True

            # Apply the action - Abort
            if rule.action == rule.ACTION_ABORT_TRACE_WITH_MESSAGE:
                self._setTraceAborted(rule.actionData)
                return False

            # Apply the action - Stop
            if rule.action == rule.ACTION_STOP_TRACE:
                return False

        # No rules have decided either way, continue tracing
        return True

    # ---------------
    # Match The Properties
    def _matchProps(self, props: Dict,
                    rule: GraphDbTraceConfigRuleTuple):
        propVal = str(props.get(rule.propertyName))

        if rule.propertyValueType == rule.PROP_VAL_TYPE_SIMPLE:
            return propVal == rule.propertyValue

        if rule.propertyValueType == rule.PROP_VAL_TYPE_COMMA_LIST:
            return propVal in rule.preparedValueSet

        if rule.propertyValueType == rule.PROP_VAL_TYPE_REGEX:
            return rule.preparedRegex.match(propVal)

        if rule.propertyValueType == rule.PROP_VAL_TYPE_BITMASK_AND:
            try:
                return bool(int(propVal) & int(rule.propertyValue))

            except ValueError:
                pass

            return False

        raise NotImplementedError("rule.propertyValueType  = %s"
                                  % rule.propertyValueType)
