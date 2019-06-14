#
# (C) ITculate, Inc. 2015-2017
# All rights reserved
# Licensed under MIT License (see LICENSE)
#

__version__ = "0.14.14"

import six
import logging
import collections
# noinspection PyPackageRequirements
from unix_dates import UnixDate
from .exceptions import SDKError
from .graph import Vertex, Edge
from .dictionary import Dictionary
from .sample import TimeSeriesSample
from .types import *
from .payload import Payload
from .provider import Provider
from .utils import encode_dict
import statsd

logger = logging.getLogger(__name__)

GLOBAL_COLLECTOR_ID = "sdk"
_tenant_id = None  # type: str
_provider = None  # type: Provider
_payloads = {}  # type: dict[str, Payload]


def _check_init():
    global _payloads
    assert _payloads is not None and isinstance(_payloads, dict), "SDK was not initialized!"


# noinspection PyUnresolvedReferences
def _get_topology_payload(collector_id):
    """
    Returns the payload for this collector ID
    :param basestring collector_id: Collector ID
    :rtype: Payload
    """
    global _payloads, _tenant_id

    if isinstance(collector_id, six.text_type):
        collector_id = collector_id.encode()

    payload = _payloads.get(collector_id)
    if payload is None:
        payload = Payload(tenant_id=_tenant_id, collector_id=collector_id)
        _payloads[collector_id] = payload

    return payload


def _get_global_payload():
    """
    Returns the global payload
    :rtype: Payload
    """
    global _payloads

    payload = _payloads.get(GLOBAL_COLLECTOR_ID)
    if payload is None:
        payload = Payload(tenant_id=_tenant_id, collector_id=GLOBAL_COLLECTOR_ID)
        _payloads[GLOBAL_COLLECTOR_ID] = payload

    return payload


class Flusher(object):
    """
    Convenience class to provide a self-flushing context (using the 'with' keyword) for reporting via the SDK.
    """

    def __enter__(self):
        _check_init()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Make sure all changes are flushed
        flush_all()


def init(provider=None, host=None, tenant_id=None, **kwargs):
    """
    Initialize a global uploader that will be used to upload data to ITculate.

    The API key provided must have the 'upload' role (and associated with a single tenant).

    Possible providers are:
        'SynchronousApiUploader' (default) - Upload straight to the ITculate API server
        'AgentForwarder' - Forwards payload to an ITculate agent
        'InMemory' - Accumulates latest status in memory

    SynchronousApiUploader settings:
        'api_key', 'api_secret' - API key to use
        'server_url" - API server to connect to
                 Default: https://api.itculate.io/api/v1
        'https_proxy_url' - Proxy to use
        'role' - Alternative to providing API key and secret. Will use local credentials file and look for that role.
                 Default: 'upload'
        'home_dir' - Home directory for user (under which we should find the .itculate/credentials file)
                 Default: '~'

    AgentForwarder settings:
        'server_url' - Address of the agent to forward to
                 Default: http://localhost:8000
        'statsd_port' - Port for StatsD UDP
                 Default: 8125

    :param str provider: Name of the provider class to use (defaults to 'SynchronousApiUploader')
    :param str host: Identifier of host reporting (defaults to hostname)
    :param str tenant_id: optional tenant to report (if not provided, tenant is derived from user login data)
    :param kwargs: Provider-specific settings

    :return A flusher instance (to be able to use with the 'with' statement)
    """
    global _tenant_id, _provider, _payloads

    provider = provider or "SynchronousApiUploader"

    if host is None:
        import socket
        host = socket.gethostname()

    provider_settings = {
        "provider": provider,
        "host": host,
    }

    # Only take values that are not None
    provider_settings.update({k: v for k, v in six.iteritems(kwargs) if v is not None})

    _tenant_id = tenant_id

    # Create the provider (will assert if provider not supported)
    _provider = Provider.factory(provider_settings)

    _payloads = {}

    # Initialize the statsd
    if provider == "AgentForwarder":
        statsd.init(port=int(provider_settings.get("statsd_port", 8125)))

    return Flusher()


# noinspection PyUnresolvedReferences
def add_vertex(collector_id,
               vertex_type,
               name,
               keys,
               counter_types=None,
               data=None,
               **kwargs):
    """
    Adds a vertex to the uploader

    Keys is a dictionary of all the unique keys identifying a vertex.
    If a single string is provided as for 'keys', the 'pk' key name will be used.

    :param basestring collector_id: Unique name identifying the reporter of this topology
    :param basestring vertex_type: Vertex type
    :param dict[basestring,basestring]|basestring keys: A set of unique keys identifying this vertex.
    :param basestring name: Name for vertex
    :param dict[basestring,DataType] counter_types: (optional) mapping of the different counters reported by this vertex
    :param dict data: Set of initial values to assign to vertex (optional)
    :param kwargs: Any additional key:value pairs that should be assigned to vertex.
    :rtype: Vertex
    """
    _check_init()

    return _get_topology_payload(collector_id).add_vertex(vertex_type=vertex_type,
                                                          name=name,
                                                          keys=keys,
                                                          counter_types=counter_types,
                                                          data=data,
                                                          **kwargs)


# noinspection PyUnresolvedReferences
def connect(source, target, topology, collector_id):
    """
    Connect (create an edge between) two (or two sets of) vertices.
    Vertices are identified by either providing the Vertex object or only their keys.

    If source / target is a list of vertices (or keys), this will create a set of edges between all sources and all
    targets

    :param basestring collector_id: Unique name identifying the reporter of this topology
    :param source: Identify source/s
    :type source: basestring|dict|Vertex|collections.Iterable[dict]|collections.Iterable[Vertex]|collections.Iterable[basestring]
    :param target: Identify target/s
    :type source: basestring|dict|Vertex|collections.Iterable[dict]|collections.Iterable[Vertex]|collections.Iterable[basestring]
    :param basestring topology: Topology (edge type) to use
    """
    _check_init()

    if isinstance(topology, six.text_type):
        topology = topology.encode()

    _get_topology_payload(collector_id).connect(source=source, target=target, topology=topology)


def add_sample(vertex, counter, value, timestamp=None):
    """
    Add a single sample for a counter

    :param Vertex|basestring vertex: Vertex object or vertex key
    :param basestring counter: Counter name
    :param float|TypedValue value: Value for counter
    :param float timestamp: A unix timestamp (seconds since epoch). If None, current time is taken.
    """
    _check_init()

    if timestamp is None:
        timestamp = UnixDate.now()

    add_samples(vertex=vertex, counter=counter, timestamp_to_value=((timestamp, value),))


# noinspection PyUnresolvedReferences
def add_samples(vertex, counter, timestamp_to_value):
    """
    Add a series of samples for a single counter

    :param Vertex|basestring vertex: Vertex object or vertex key
    :param basestring counter: Counter name
    :param collections.Iterable[(float, float|TypedValue)] timestamp_to_value: An iterable of pairs of timestamp, value
    """
    _check_init()

    assert isinstance(vertex, Vertex) or isinstance(vertex, six.string_types), \
        "Bad class type for vertex - {}".format(vertex.__class__.__name__)

    if isinstance(counter, six.text_type):
        counter = counter.encode()

    _get_global_payload().add_counter_samples(vertex=vertex,
                                              counter=counter,
                                              timestamp_to_value=timestamp_to_value)


# noinspection PyUnresolvedReferences
def enable_grouper_algorithm(group_vertex_type, member_vertex_type, topology):
    """
    Configure the grouping algorithm to group together vertices of type 'member_vertex_type' under group vertices
    of type 'group_vertex_type' by adding group edges of type 'topology'.

    Once configured, the algorithm will run periodically, adding new edges for the group, while keeping the original
    edges intact.

    :param basestring group_vertex_type: Vertex type
    :param basestring member_vertex_type: Vertex type
    :param basestring topology: Topology (edge type) to use
    """
    _check_init()

    if isinstance(member_vertex_type, six.text_type):
        member_vertex_type = member_vertex_type.encode()

    meta_data = Dictionary.lookup_algorithm_meta_data(vertex_type=member_vertex_type, name="grouper")
    meta_data = meta_data if meta_data else {"groups_info": []}
    for info in meta_data["groups_info"]:
        if info["group_edge_type"] == topology and info["group_vertex_type"] == group_vertex_type:
            # meta_data already contains this, do nothing
            return

    meta_data["groups_info"].append({"group_vertex_type": group_vertex_type, "group_edge_type": topology})

    Dictionary.update_algorithm(vertex_type=member_vertex_type, name="grouper", meta_data=meta_data)


# noinspection PyUnresolvedReferences
def vertex_event(collector_id,
                 vertex, message,
                 event_type="MESSAGE",
                 severity="INFO",
                 timestamp=None,
                 propagate=False,
                 document=None):
    """
    Generic event
    :param basestring collector_id: Unique name identifying the reporter of this topology
    :param Vertex|basestring vertex: Vertex (or vertex key) associated with event
    :param str severity: One of CRITICAL / ERROR / WARNING / INFO / SUCCESS
    :param basestring event_type: A free text with event type
    :param basestring message: A free text describing the event
    :param float timestamp: An optional time of event (defaults to now)
    :param bool propagate: should event propagate in the topology
    :param dict document: Optional, more info as dictionary

    """
    _check_init()

    if isinstance(collector_id, six.text_type):
        collector_id = collector_id.encode()

    if isinstance(message, six.text_type):
        message = message.encode()

    if isinstance(event_type, six.text_type):
        event_type = event_type.encode()

    return _get_topology_payload(collector_id).vertex_event(vertex=vertex,
                                                            message=message,
                                                            event_type=event_type,
                                                            severity=severity,
                                                            timestamp=timestamp,
                                                            propagate=propagate,
                                                            document=document)


def vertex_healthy(collector_id, vertex, message=None, timestamp=None):
    """
    Health (up) event - indicates a vertex is healthy.

    Under the hood, this Will generate an event of type "HEALTHY" with severity "SUCCESS".
    If message is not provided, the default message would be: "{Vertex type} {Vertex name} is healthy"

    :param basestring collector_id: Unique name identifying the reporter of this topology
    :param Vertex|basestring vertex: Vertex (or vertex key) associated with event
    :param basestring message: A free text describing the event
    :param float timestamp: An optional time of event (defaults to now)
    """
    vertex_event(collector_id=collector_id,
                 vertex=vertex,
                 message=message,
                 event_type="HEALTHY",
                 severity="SUCCESS",
                 timestamp=timestamp)


def vertex_property_change(collector_id,
                           vertex,
                           attribute,
                           old_value,
                           new_value,
                           message=None,
                           timestamp=None,
                           severity="INFO"):
    """
    Health (up) event - indicates a vertex is healthy.

    Under the hood, this Will generate an event of type "HEALTHY" with severity "SUCCESS".
    If message is not provided, the default message would be: "{Vertex type} {Vertex name} is healthy"

    :param basestring collector_id: Unique name identifying the reporter of this topology
    :param Vertex|basestring vertex: Vertex (or vertex key) associated with event
    :param basestring message: A free text describing the event
    :param float timestamp: An optional time of event (defaults to now)
    :return the event as dict
    """
    updates = [{
        "attribute-path": [attribute],
        "attribute-name": attribute,
        "old-value": old_value,
        "new-value": new_value
    }]

    document = {
        "updates": updates,
        "vertex-type": vertex.type,
        "vertex-name": vertex.name,
    }

    return vertex_event(collector_id=collector_id,
                        vertex=vertex,
                        message=message,
                        event_type="PROPERTY_CHANGED",
                        severity=severity,
                        timestamp=timestamp,
                        document=document)


def vertex_unhealthy(collector_id, vertex, message=None, timestamp=None, attribute=None, old_value=None, new_value=None):
    """
    Health (down) event - indicates a vertex is unhealthy.

    Under the hood, this Will generate an event of type "HEALTHY" with severity "SUCCESS".
    If message is not provided, the default message would be: "{Vertex type} {Vertex name} is unhealthy"

    :param basestring collector_id: Unique name identifying the reporter of this topology
    :param Vertex|basestring vertex: Vertex (or vertex key) associated with event
    :param basestring message: A free text describing the event
    :param float timestamp: An optional time of event (defaults to now)
    """

    document = None

    if attribute:
        updates = [{
            "attribute-path": [attribute],
            "attribute-name": attribute,
            "old-value": old_value,
            "new-value": new_value
        }]

        document = {
            "updates": updates,
            "vertex-type": vertex.type,
            "vertex-name": vertex.name,
        }

    vertex_event(collector_id=collector_id,
                 vertex=vertex,
                 message=message,
                 event_type="UNHEALTHY",
                 severity="ERROR",
                 document=document,
                 timestamp=timestamp)


# noinspection PyUnresolvedReferences
def flush_topology(collector_id):
    """
    Flush a topology collected by the given collector id

    :param basestring collector_id: Collector ID to flush
    :return: True if any data was flushed
    :rtype: bool
    """
    global _payloads

    _check_init()

    if isinstance(collector_id, six.text_type):
        collector_id = collector_id.encode()

    if collector_id not in _payloads:
        return False

    return _provider.flush_now((_payloads[collector_id],)) > 0


def flush_all():
    """
    Flushes all unsent data without waiting for the next interval
    :return: number of payloads flushed
    """

    global _payloads
    return _provider.flush_now(_payloads)
