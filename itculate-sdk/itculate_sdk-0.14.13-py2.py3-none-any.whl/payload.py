#
# (C) ITculate, Inc. 2015-2017
# All rights reserved
# Licensed under MIT License (see LICENSE)
#

import logging
import re
import itertools
from collections import defaultdict

import collections
import six
from unix_dates import UnixDate

from .utils import encode_dict
from .graph import Vertex, Edge
from .dictionary import Dictionary
from .types import TypedValue, DataType

_VALID_COLLECTOR_ID = re.compile(r"^[a-zA-Z0-9_]+$")

logger = logging.getLogger(__name__)


class Payload(object):
    """
    Hold the transient state until the next 'flush' is called. When flushed, will generate a Payload with all the data
    that was accumulated since the last flush.
    """

    def __init__(self, collector_id, tenant_id=None):
        """
        :param str|None tenant_id: (optional) Tenant ID. If not provided, tenant ID will be extracted from user data
        :param str collector_id: Unique (within tenant) name for this topology
        """
        assert _VALID_COLLECTOR_ID.match(collector_id), "Invalid collector ID (must be [a-zA-Z0-9_]+)"
        self._collector_id = collector_id
        self._tenant_id = tenant_id

        self._vertices_by_pk = {}  # type: dict[str, Vertex]
        self._edges = []  # type: list[Edge]
        self._samples = defaultdict(lambda: defaultdict(list))
        self._events = []

    @property
    def collector_id(self):
        return self._collector_id

    @property
    def tenant_id(self):
        return self._tenant_id

    def __str__(self):
        return "{}-{}".format(self.__class__.__name__, self._collector_id)

    def __unicode__(self):
        return u"{}-{}".format(self.__class__.__name__, self._collector_id)

    # noinspection PyUnresolvedReferences
    def add_vertex(self,
                   vertex_type,
                   name,
                   keys,
                   primary_key_id=None,
                   counter_types=None,
                   data=None,
                   **kwargs):
        """
        Adds a vertex to the topology

        :param basestring vertex_type: Vertex type
        :param basestring primary_key_id: Name of key (within 'keys') designated as primary key (globally unique)
        :param keys: A set of unique keys identifying this vertex. If str, 'pk' will be used as key
        :type keys: dict[basestring,basestring]|basestring
        :param basestring name: Name for vertex
        :param counter_types: (optional) mapping of the different counters reported by this vertex
        :type counter_types: dict[basestring,DataType]
        :param dict data: Set of initial values to assign to vertex (optional)
        :param kwargs: Any additional key:value pairs that should be assigned to vertex.
        :rtype: Vertex
        """

        if isinstance(keys, six.string_types):
            assert primary_key_id is None or primary_key_id == "pk", \
                "Expecting primary_key_id to be None or 'pk' when providing keys as a str"
            keys = {"pk": keys.encode()}
            primary_key_id = "pk"

        else:
            keys = encode_dict(keys)
            primary_key_id = primary_key_id or keys.keys()[0]

        if isinstance(vertex_type, six.text_type):
            vertex_type = vertex_type.encode()

        if isinstance(name, six.text_type):
            name = name.encode()

        v = Vertex(vertex_type=vertex_type,
                   name=name,
                   keys=keys,
                   primary_key_id=primary_key_id,
                   data=data,
                   **kwargs)

        self.update(vertices=[v])

        if counter_types is not None:
            counter_types = encode_dict(counter_types)

            for counter, data_type in six.iteritems(counter_types):
                Dictionary.update_data_type(dictionary_type=Dictionary.D_TYPE_TIMESERIES,
                                            vertex_key=v.first_key,
                                            attribute=counter,
                                            data_type=data_type)

        return v

    def connect(self, source, target, topology):
        """
        Connect (create an edge between) two (or two sets of) vertices.
        Vertices are identified by either providing the Vertex object or only their keys.

        If source / target is a list of vertices (or keys), this will create a set of edges between all sources and all
        targets

        :param source: Identify source/s
        :type source: str|dict|Vertex|collections.Iterable[dict]|collections.Iterable[Vertex]|collections.Iterable[str]
        :param target: Identify target/s
        :type target: str|dict|Vertex|collections.Iterable[dict]|collections.Iterable[Vertex]|collections.Iterable[str]
        :param str topology: Topology (edge type) to use for this connection
        """

        # assert '$' not in topology, "Invalid topology value '{}', should not contain '$'".format(topology)

        source = source if isinstance(source, list) else [source]
        target = target if isinstance(target, list) else [target]

        edges = []
        for sk, tk in itertools.product(source, target):
            if isinstance(sk, Vertex):
                sk = sk.keys

            if isinstance(sk, six.text_type):
                sk = sk.encode()

            if isinstance(sk, str):
                sk = {"pk": sk}

            if isinstance(tk, Vertex):
                tk = tk.keys

            if isinstance(tk, six.text_type):
                tk = tk.encode()

            if isinstance(tk, str):
                tk = {"pk": tk}

            edges.append(Edge(edge_type=topology, source=sk, target=tk))

        self.update(edges=edges)

    def update(self, vertices=None, edges=None):
        """
        Update the uploader with new information.

        :param collections.Iterable[Vertex] vertices: Collection of vertices
        :param collections.Iterable[Edge] edges: Collection of edges
        """
        assert vertices or edges, "No data provided"

        if vertices:
            self._vertices_by_pk.update({v.first_key: v for v in vertices})

        if edges:
            self._edges.extend(edges)

    def add_counter_samples(self, vertex, counter, timestamp_to_value):
        """
        Add a set of time-series samples associated with a vertex or a key.

        If values are typed (TypedValue), the appropriate dictionary updates will be made based on these values.

        :param Vertex|str vertex: Vertex object or vertex key, if None, non_vertex_key will be used
        :param str counter: Counter name
        :param timestamp_to_value: An iterable of timestamps and values
        :type timestamp_to_value: collections.Iterable[(float, float|TypedValue)]
        """

        if isinstance(vertex, Vertex):
            vertex = vertex.first_key

        def convert_sample((ts, value)):
            stripped_value = Dictionary.update_and_strip(dictionary_type=Dictionary.D_TYPE_TIMESERIES,
                                                         vertex_key=vertex,
                                                         attribute=counter,
                                                         value=value)
            return ts, stripped_value

        self._samples[vertex][counter].extend(itertools.imap(convert_sample, timestamp_to_value))

    def vertex_event(self,
                     vertex,
                     message,
                     event_type="MESSAGE",
                     severity="INFO",
                     timestamp=None,
                     propagate=False,
                     document=None):
        """
        Generic event

        :param Vertex|str vertex: Vertex (or vertex key) associated with event
        :param str severity: One of CRITICAL / ERROR / WARNING / INFO / SUCCESS
        :param str event_type: A free text with event type
        :param str message: A free text describing the event
        :param float timestamp: An optional time of event (defaults to now)
        :param propagate : should event propagate in the topology
        :param document : Optional, more info as dictionary
        :return the event
        """
        event = {
            "vertex_key": vertex.first_key if isinstance(vertex, Vertex) else vertex,
            "event_time": timestamp or UnixDate.now(),
            "event_type": event_type,
            "severity": severity,
            "message": message,
            "propagate": propagate,
            "document": document, }
        self._events.append(event)
        return event

    def flush(self):
        """
        Called is when the builder of the topology is ready for it to be uploaded. All the vertices and edges are in
        and no further modifications are necessary.

        After this call, the internal state will be cleared (ready for building a new report).

        Be careful not to call flush unless the full data is populated. The ITculate server expects full reports to be
        made for the topology.

        :return: A the data accumulated by this payload or None if nothing to flush
        :rtype: dict
        """
        local_vertices_by_pk, self._vertices_by_pk = (self._vertices_by_pk, {})
        local_edges, self._edges = (self._edges, [])
        local_samples, self._samples = (self._samples, defaultdict(lambda: defaultdict(list)))
        local_dictionary = Dictionary.flush()
        local_events, self._events = (self._events, [])

        return {
            "tenant_id": self.tenant_id,
            "collector_id": self.collector_id,
            "vertices": [v.document for v in local_vertices_by_pk.values()],
            "edges": [e.document for e in local_edges],
            "samples": local_samples,
            "dictionary": local_dictionary,
            "events": local_events,
        }
