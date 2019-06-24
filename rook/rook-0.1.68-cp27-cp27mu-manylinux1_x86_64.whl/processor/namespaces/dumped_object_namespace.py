import six

from .namespace import Namespace
from .python_object_namespace import PythonObjectNamespace


class DumpedObjectNamespace(Namespace):

    def __init__(self, type, common_type, attributes, methods=()):
        super(DumpedObjectNamespace, self).__init__(methods + (DumpedObjectNamespace.type, ))
        self.type = type
        self.common_type = common_type
        self.attributes = attributes

    def read_attribute(self, name):
        return self.attributes[name]

    def no_attriubtes(self):
        return 0 == len(self.attributes)

    def read_key(self, key):
        raise NotImplementedError()

    def type(self, args=None):
        return PythonObjectNamespace(self.type)

    def serialize_type(self):
        return type

    def get_attributes_dict(self):
        attributes = {}
        for key, value in six.iteritems(self.attributes):
            attributes[key] = value.to_dict()

        return attributes

    def get_attributes_simple_dict(self):
        attributes = {}
        for key, value in six.iteritems(self.attributes):
            attributes[key] = value.to_simple_dict()

        return attributes
