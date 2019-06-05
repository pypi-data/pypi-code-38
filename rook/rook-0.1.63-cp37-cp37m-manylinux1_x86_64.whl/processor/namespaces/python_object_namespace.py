import six
import datetime

from .namespace import Namespace

from rook.exceptions import RookKeyNotFound, RookAttributeNotFound


class PythonObjectNamespace(Namespace):

    try:
        BINARY_TYPES = (buffer, bytearray)
    except NameError:
        BINARY_TYPES = (bytearray, bytes)

    class ObjectDumpConfig(object):

        DEFAULT_MAX_DEPTH = 3
        DEFAULT_MAX_WIDTH = 20
        DEFAULT_MAX_COLLECTION_DEPTH = 2
        DEFAULT_MAX_STRING = 512

        CONSERVATIVE_MAX_DEPTH = 5
        CONSERVATIVE_MAX_WIDTH = 20
        CONSERVATIVE_MAX_COLLECTION_DEPTH = 2
        CONSERVATIVE_MAX_STRING = 256

        UNLIMITED_STRING = 64 * 1024
        UNLIMITED_COLLECTION_WIDTH = 100

        def __init__(self, max_depth=None, max_width=None, max_collection_dump=None, max_string=None):
            self.max_depth = max_depth or self.DEFAULT_MAX_DEPTH
            self.max_width = max_width or self.DEFAULT_MAX_WIDTH
            self.max_collection_dump = max_collection_dump or self.DEFAULT_MAX_COLLECTION_DEPTH
            self.max_string = max_string or self.DEFAULT_MAX_STRING

        def __eq__(self, other):
            try :
                return self.max_depth == other.max_depth and self.max_width == other.max_width and \
                       self.max_collection_dump == other.max_collection_dump and self.max_string == other.max_string
            except:
                return False

        @classmethod
        def default_limits(cls, obj):
            return PythonObjectNamespace.ObjectDumpConfig(
                cls.DEFAULT_MAX_DEPTH,
                cls.DEFAULT_MAX_WIDTH,
                cls.DEFAULT_MAX_COLLECTION_DEPTH,
                cls.DEFAULT_MAX_STRING)

        @classmethod
        def conservative_limits(cls, obj):
            return PythonObjectNamespace.ObjectDumpConfig(
                cls.CONSERVATIVE_MAX_DEPTH,
                cls.CONSERVATIVE_MAX_WIDTH,
                cls.CONSERVATIVE_MAX_COLLECTION_DEPTH,
                cls.CONSERVATIVE_MAX_STRING)

        @classmethod
        def tailor_limits(cls, obj):
            if isinstance(obj, six.string_types):
                return PythonObjectNamespace.ObjectDumpConfig(1, 0, 0, cls.UNLIMITED_STRING)
            if isinstance(obj, (list, dict, set, tuple)):
                return PythonObjectNamespace.ObjectDumpConfig(max_width=cls.UNLIMITED_COLLECTION_WIDTH)
            else:
                return PythonObjectNamespace.ObjectDumpConfig()

    def __init__(self, obj, dump_config=None, methods=()):
        super(PythonObjectNamespace, self).__init__(methods + self.METHODS)
        self.obj = obj
        self.dump_config = dump_config or self.ObjectDumpConfig()

    @classmethod
    def get_common_type(cls, obj):
        # NOTE: This list is partially duplicated with the list in NamespaceSerializer._load_variant
        if obj is None:
            return u'null'
        elif isinstance(obj, six.integer_types):
            return u'int'
        elif isinstance(obj, six.string_types):
            return u'string'
        elif isinstance(obj, float):
            return u'float'
        elif isinstance(obj, cls.BINARY_TYPES):
            return u'buffer'
        elif isinstance(obj, datetime.datetime):
            return u'datetime'
        elif isinstance(obj, (list, set, tuple)):
            from .collection_namespace import ListNamespace
            return ListNamespace.get_common_type(obj)
        elif isinstance(obj, (dict)):
            return u'dict'
        elif isinstance(obj, complex):
            return u'complex'
        else:
            raise ValueError("Unknown type- %s", str(type(obj)))

    def read_attribute(self, name):
        try:
            return PythonObjectNamespace(getattr(self.obj, name))
        except AttributeError:
            raise RookAttributeNotFound(name)

    def read_key(self, key):
        try:
            return PythonObjectNamespace(self.obj[key])
        except (KeyError, IndexError):
            raise RookKeyNotFound(key)

    def type(self, args=None):
        return PythonObjectNamespace(self.serialize_type())

    def serialize_type(self):
        return str(type(self.obj))

    def size(self, args=None):
        return PythonObjectNamespace(len(self.obj))

    def depth(self, args):
        self.dump_config.max_depth = int(args)
        return self

    def width(self, args):
        self.dump_config.max_width = int(args)
        return self

    def collection_dump(self, args):
        self.dump_config.max_collection_dump = int(args)
        return self

    def string(self, args):
        self.dump_config.max_string = int(args)
        return self

    def to_dict(self):
        result = {
            u'@namespace': self.__class__.__name__,
            u'@common_type': self.get_common_type(self.obj),
            u'@original_type': self.serialize_type(),
            }

        if hasattr(self.obj,'__dict__'):
            result['@attributes'] = self.obj.__dict__
        else:
            result['@attributes'] = {}

        if six.PY2 and isinstance(self.obj, str):
            result[u'@value'] = unicode(self.obj, errors='replace')
        elif six.PY2 and isinstance(self.obj, (int, long, float, str, unicode, buffer, bytearray, bytes, list, dict, set, frozenset)) or \
            six.PY3 and isinstance(self.obj, (int, float, str, bytes, bytearray, list, dict, set, frozenset)):
            result[u'@value'] = self.obj

        return result

    def to_simple_dict(self):
        return self.obj

    def __hash__(self):
        return hash(self.obj)

    def __nonzero__(self):
        return bool(self.obj)

    if six.PY3:
        __bool__ = __nonzero__

    METHODS = (type, size, depth, width, collection_dump, string)
