import xml.etree.ElementTree as ET
from functools import reduce
from io import StringIO
from hashlib import sha1
from enum import Enum


class XMLHelper:
    def __init__(self, encoded_xml):
        self._namespaces = (
            _avoid_namespace_collisions(
                map(lambda el: el[1],
                    ET.iterparse(StringIO(encoded_xml),
                                 events=['start-ns']))))

        self._document = ET.parse(StringIO(encoded_xml))

        for namespace in self._namespaces.items():
            ET.register_namespace(*namespace)

    @property
    def root(self):
        return self._document.getroot()

    def namespace(self, shortname):
        return self._namespaces.get(shortname, None)

    def deep_copy(self):
        return XMLHelper(self.serialize(self.root).decode('utf-8'))

    @property
    def default_namespace(self):
        return self._namespaces.get('', None)

    def attribute_fullname(self, name, namespace=None):
        return ('{%s}%s' % (self.namespace(namespace), name)
                if namespace is not None
                else name)

    def get_attribute(self, node, name, namespace=None):
        try:
            return node.attrib[self.attribute_fullname(name, namespace)]
        except KeyError:
            return None

    def set_attribute(self, node, name, value, namespace=None):
        node.attrib[self.attribute_fullname(name, namespace)] = value

    def del_attribute(self, node, name, namespace=None):
        del node.attrib[self.attribute_fullname(name, namespace)]

    def has_attribute(self, node, name, namespace=None):
        return self.attribute_fullname(name, namespace) in node.attrib

    def serialize(self, node):
        return ET.tostring(node)


def _collision_free_name(namespace_value):
    return 'namespaceCollision%s' % sha1(
        namespace_value.encode('utf-8')).hexdigest()


def _avoid_namespace_collisions(kv_iter):
    Action = Enum('Action', 'Add Replace')

    def get_conflict_free_key(acc, key, value):
        XML_NAMESPACE_NAME = 'http://www.w3.org/XML/1998/namespace'
        XML_NAMESPACE_PREFIX = 'xml'

        existing_key, _ = next(
            filter(lambda el: el[1] == value, acc.items()),
            (None, None))

        if value == XML_NAMESPACE_NAME:
            return (Action.Add, XML_NAMESPACE_PREFIX)
        elif key.startswith('xml'):
            return (Action.Add, _collision_free_name(value))
        elif existing_key is not None:
            if key == '' and (key not in acc):
                return (Action.Replace, (existing_key, ''))
            else:
                return (Action.Add, existing_key)
        elif key in acc:
            return (Action.Add, _collision_free_name(value))
        else:
            return (Action.Add, key)

    def add_to_dict(state, kv):
        key, value = kv
        action, new_key = get_conflict_free_key(state, key, value)

        if action == Action.Add:
            state[new_key] = value
        elif action == Action.Replace:
            old_key, replacement = new_key
            del state[old_key]
            state[replacement] = value

        return state

    return reduce(add_to_dict, kv_iter, {})
