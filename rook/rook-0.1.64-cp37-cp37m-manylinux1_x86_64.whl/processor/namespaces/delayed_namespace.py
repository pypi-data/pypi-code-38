import six

from . import namespace


class DelayedNamespace(namespace.Namespace):
    def __init__(self, value):
        super(DelayedNamespace, self).__init__()

        self.value = value
        self.variant = None
        self.namespace = None

    def call_method(self, name, args):
        self._load()
        return self.namespace.call_method(name, args)

    def read_attribute(self, name):
        self._load()
        return self.namespace.read_attribute(name)

    def write_attribute(self, name, value):
        self._load()
        return self.namespace.write_attribute(name, value)

    def read_key(self, key):
        self._load()
        return self.namespace.read_key(key)

    def to_dict(self):
        self._load()
        return self.namespace.to_dict()

    def to_simple_dict(self):
        self._load()
        return self.namespace.to_simple_dict()

    def get_variant(self):
        self._load()
        return self.variant

    def _load(self):
        if self.namespace is not None:
            return

        from .. import namespace_serializer
        from google.protobuf.json_format import ParseDict, Parse
        from rook.protobuf import rook_pb2

        if isinstance(self.value, six.string_types):
            self.variant = Parse(self.value, rook_pb2.Variant())
        else:
            self.variant = ParseDict(self.value, rook_pb2.Variant())

        self.namespace = namespace_serializer.NamespaceSerializer().loads(self.variant)
