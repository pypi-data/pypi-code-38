#
# (C) ITculate, Inc. 2015-2017
# All rights reserved
# Licensed under MIT License (see LICENSE)
#

import six
from .dictionary import Dictionary
from .utils import ReadOnlyDict, encode_dict, check_keys, decode_dict

_VERTEX_NAME_ATTR = "_name"
_VERTEX_TYPE_ATTR = "_type"
_VERTEX_SUBTYPE_ATTR = "_subtype"
_VERTEX_KEYS_ATTR = "_keys"
_VERTEX_KEYWORDS = "_keywords"
_VERTEX_CAN_BE_OWNER_ATTR = "_can_be_owner"


class Vertex(object):
    def __init__(self, vertex_type, name, keys, data=None, **kwargs):
        """
        Defines a client-side vertex. This is basically a set of attributes (with special ones prefixed with '_').

        :param str vertex_type: Vertex type (utf-8 encoded)
        :param str name: Name for vertex (utf-8 encoded)
        :param dict keys: A set of unique keys identifying this vertex (utf-8 encoded)
        :param str primary_key_id: Name of key (within 'keys') designated as primary key (must be globally unique)
        :param dict data: Set of initial values to assign to vertex (optional)
        :param kwargs: Any additional key:value pairs that should be assigned to vertex.
        """
        assert vertex_type, "Type is mandatory"
        assert name, "Name is mandatory"

        check_keys(keys)
        keys = encode_dict(keys)

        if data is not None:
            assert isinstance(data, dict), "data must be of type dict"
            d = data

        else:
            d = {}

        # Add any keyword args to the dictionary
        if kwargs:
            d.update(kwargs)

        # Get the meta-data from each of the attributes
        for attribute, value in six.iteritems(d):
            stripped_value = Dictionary.update_and_strip(dictionary_type=Dictionary.D_TYPE_VERTEX,
                                                         vertex_key=six.next(six.itervalues(keys)),
                                                         attribute=attribute,
                                                         value=value)
            d[attribute] = stripped_value

        # Add the essentials (to make sure they override everything)
        d.update({
            _VERTEX_TYPE_ATTR: vertex_type,
            _VERTEX_KEYS_ATTR: ReadOnlyDict(keys),
            _VERTEX_NAME_ATTR: name,
        })

        # Finally - update self and set the dirty flag (False as this is the initial setting)
        self._d = d

        self._frozen = False

    def freeze(self):
        # Make sure this vertex is now immutable!
        self._frozen = True
        return self

    @property
    def type(self):
        return self._d[_VERTEX_TYPE_ATTR]

    @property
    def name(self):
        return self._d[_VERTEX_NAME_ATTR]

    @name.setter
    def name(self, name):
        assert not self._frozen, "Vertex is frozen!"
        self[_VERTEX_NAME_ATTR] = name

    @property
    def keys(self):
        """
        :rtype: dict
        :return The vertex keys (DO NOT CHANGE - use add_key instead!!!)
        """
        return ReadOnlyDict(self._d[_VERTEX_KEYS_ATTR])

    @property
    def first_key(self):
        return six.next(six.itervalues(self.keys))

    @property
    def document(self):
        """
        Provides access to internal document representing this vertex

        :rtype: dict[str, str]
        """
        return ReadOnlyDict(self._d)

    @property
    def can_be_owner(self):
        """
        Only one collector can be the 'owner' of a vertex. Ownership means that ability to create and delete a vertex
        as well as change its type and keys.

        When two collectors report the same vertex, it is important that one of them surrenders the right to own it.
        This helps the merging algorithm to avoid 'flickering' of vertices when conflicting reports are made.

        Defaults to 'True'

        :return: True if the collector reporting this vertex can claim ownership on it
        """
        return self.get(_VERTEX_CAN_BE_OWNER_ATTR, True)

    @can_be_owner.setter
    def can_be_owner(self, can_be_owner):
        """
        Only one collector can be the 'owner' of a vertex. Ownership means that ability to create and delete a vertex
        as well as change its type and keys.

        When two collectors report the same vertex, it is important that one of them surrenders the right to own it.
        This helps the merging algorithm to avoid 'flickering' of vertices when conflicting reports are made.

        :param bool can_be_owner: True if the collector reporting this vertex can claim ownership on it
        """
        self[_VERTEX_CAN_BE_OWNER_ATTR] = can_be_owner

    @property
    def subtype(self):
        """
        Vertex subtype is typically used to identify what's installed on the vertex (in the addition to the primary
        vertex type). For example, if a vertex is an AWS instance, but has Cassandra on it, then the primary type will
        be AWS_Instance but the subtype will be 'Cassandra'.

        Often, subtype is reported by a different collector (and then it is reported with 'can_be_owner' = False).

        :rtype: str
        """
        return self.get(_VERTEX_SUBTYPE_ATTR)

    @subtype.setter
    def subtype(self, subtype):
        """
        Vertex subtype is typically used to identify what's installed on the vertex (in the addition to the primary
        vertex type). For example, if a vertex is an AWS instance, but has Cassandra on it, then the primary type will
        be AWS_Instance but the subtype will be 'Cassandra'

        :param str subtype: Subtype to set
        """
        self[_VERTEX_SUBTYPE_ATTR] = subtype

    def update(self, d):
        """
        Override the default set to handle dirty flag

        :param dict[str, str] d: Dict to update with
        """
        assert not self._frozen, "Vertex is frozen!"
        assert isinstance(d, dict), "Expecting dict"
        assert _VERTEX_KEYS_ATTR not in d, "Cannot update keys!"
        self._d.update(d)

    def __setitem__(self, key, value):
        """
        Override the default set to handle dirty flag
        """
        assert not self._frozen, "Vertex is frozen!"
        assert not key.startswith("_"), "Cannot modify a special/internal attribute"

        stripped_value = Dictionary.update_and_strip(dictionary_type=Dictionary.D_TYPE_VERTEX,
                                                     vertex_key=self.first_key,
                                                     attribute=key,
                                                     value=value)

        self._d[key] = stripped_value

    def __getitem__(self, item):
        return self._d.__getitem__(item)

    def __delitem__(self, key):
        assert not key.startswith("_"), "Cannot delete a special/internal attribute"
        return self._d.__delitem__(key)

    def __contains__(self, item):
        return self._d.__contains__(item)

    def get(self, key, default=None):
        return self._d.get(key, default)

    def __eq__(self, other):
        assert isinstance(other, Vertex), "Only Vertex comparisons are supported"
        return self._d == other._d

    def __str__(self):
        return "Vertex ({}) {}: {}".format(self.type, self.name, self.keys)

    def __unicode__(self):
        return u"Vertex ({}) {}: {}".format(self.type, self.name, self.keys)


_EDGE_TYPE_ATTR = "_type"
_EDGE_SOURCE_KEYS_ATTR = "_source_keys"
_EDGE_TARGET_KEYS_ATTR = "_target_keys"


class Edge(object):
    def __init__(self, source, target, edge_type):
        """
        :param dict[str, str] source: Set of vertex keys
        :param dict[str, str] target: Set of vertex keys
        :param str edge_type: Edge type (utf-8 encoded)
        """

        check_keys(source)
        check_keys(target)

        assert source != target, "Source and target are the same (Edge cannot point to itself)"

        self._d = ReadOnlyDict({
            _EDGE_TYPE_ATTR: edge_type,
            _EDGE_SOURCE_KEYS_ATTR: source,
            _EDGE_TARGET_KEYS_ATTR: target,
        })

    def __unicode__(self):
        return u"Edge {}: {} => {}".format(self.type.decode(),
                                           decode_dict(self.source_keys),
                                           decode_dict(self.target_keys))

    def __str__(self):
        return "Edge {}: {} => {}".format(self.type, self.source_keys, self.target_keys)

    @property
    def type(self):
        """ :rtype: str """
        return self._d[_EDGE_TYPE_ATTR]

    @property
    def source_keys(self):
        """
        :return the key dictionary (utf-8 encoded)
        :rtype: dict[str, str]
        """
        return self._d[_EDGE_SOURCE_KEYS_ATTR]

    @property
    def target_keys(self):
        """
        :return the key dictionary (utf-8 encoded)
        :rtype: dict[str, str]
        """
        return self._d[_EDGE_TARGET_KEYS_ATTR]

    # noinspection PyProtectedMember
    def __eq__(self, other):
        return self.source_keys == other.source_keys and self.target_keys == other.target_keys

    @property
    def document(self):
        """
        :rtype: dict[str, str]
        :return: Document (Read-only) representing this edge (utf-8 encoded)
        """
        return self._d
