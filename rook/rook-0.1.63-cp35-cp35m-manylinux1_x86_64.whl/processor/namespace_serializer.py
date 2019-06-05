import os
import datetime
import traceback
from types import FunctionType, MethodType, TracebackType
from collections import Iterable

import six

if six.PY2:
    from types import TypeType

from google.protobuf.internal.type_checkers import Int32ValueChecker, Int64ValueChecker

from .namespaces.container_namespace import ContainerNamespace
from .namespaces.python_object_namespace import PythonObjectNamespace
from .namespaces.collection_namespace import DictNamespace, ListNamespace, LIST_TYPE
from .namespaces.user_object_namespace import UserObjectNamespace
from .namespaces.error_namespace import ErrorNamespace
from .namespaces.max_depth_namespace import MaxDepthNamespace
from .namespaces.formatted_namespace import FormattedNamespace
from .namespaces.dumped_primitive_namespace import DumpedPrimitiveNamespace
from .namespaces.string_namespace import StringNamespace
from .namespaces.unknown_namespace import UnknownNamespace
from .namespaces.code_object_namespace import CodeObjectNamespace
from .namespaces.dynamic_object_namespace import DynamicObjectNamespace
from .namespaces.delayed_namespace import DelayedNamespace

from ..logger import logger

try:
    from rook.protobuf import rook_pb2
except ImportError:
    from rook.protobuf2 import variant_pb2 as rook_pb2

from rook.config import ProtobufConfiguration, ErrorConfiguration

try:
    import numpy
except ImportError:
    numpy = None


class NamespaceSerializer(object):

    def __init__(self):
        pass

    def dump(self, namespace, variant, log_errors=True):
        try:
            if isinstance(namespace, ContainerNamespace):
                return self._dump_container_namespace(namespace, variant, log_errors)
            elif isinstance(namespace, PythonObjectNamespace):
                return self._dump_object_namespace(namespace, variant, log_errors)
            elif isinstance(namespace, StringNamespace):
                return self._dump_string_namespace(namespace, variant, log_errors)
            elif isinstance(namespace, DumpedPrimitiveNamespace):
                return self._dump_primitive_namespace(namespace, variant, log_errors)
            elif isinstance(namespace, UserObjectNamespace):
                return self._dump_user_object_namespace(namespace, variant, log_errors)
            elif isinstance(namespace, ListNamespace):
                return self._dump_list_namespace(namespace, variant, log_errors)
            elif isinstance(namespace, DictNamespace):
                return self._dump_dictionary_namespace(namespace, variant, log_errors)
            elif isinstance(namespace, ErrorNamespace):
                return self._dump_error_namespace(namespace, variant, log_errors)
            elif isinstance(namespace, MaxDepthNamespace):
                return self._dump_max_depth_namespace(namespace, variant, log_errors)
            elif isinstance(namespace, FormattedNamespace):
                return self._dump_formatted_namespace(namespace, variant, log_errors)
            elif isinstance(namespace, UnknownNamespace):
                return self._dump_unknown_namespace(namespace, variant, log_errors)
            elif isinstance(namespace, CodeObjectNamespace):
                return self.dump_code_namespace(namespace, variant, log_errors)
            elif isinstance(namespace, DynamicObjectNamespace):
                return self.dump_dynamic_namespace(namespace, variant, log_errors)
            elif isinstance(namespace, DelayedNamespace):
                return self.dump_delayed_namespace(namespace, variant, log_errors)
            else:
                raise NotImplementedError("Does not support serializing this type!", type(namespace))
        except Exception as e:
            message = "Failed to serialize namespace"

            from .error import Error
            variant.Clear()
            variant.variant_type = variant.VARIANT_ERROR

            if log_errors:
                Error(exc=e, message=message).dump(variant.error_value)
                logger.exception(message)

    def dumps(self, namespace, log_errors=True):
        variant = rook_pb2.Variant()
        self.dump(namespace, variant, log_errors)
        return variant

    def loads(self, message):
        return self._load_variant(message)

    def _dump_container_namespace(self, namespace, variant, log_errors):
        variant.variant_type = variant.VARIANT_NAMESPACE

        for key, value in six.iteritems(namespace.dictionary):
            item = variant.namespace_value.attributes.add()
            item.name = key
            self.dump(value, item.value, log_errors)

    def _dump_object_namespace(self, namespace, variant, log_errors):
        self._dump_python_object(namespace.obj, variant, 0, namespace.dump_config, log_errors)

    def _dump_string_namespace(self, namespace, variant, log_errors):
        self._dump_dumped_object_namespace(namespace, variant, log_errors)

        if "string" == namespace.common_type:
            variant.variant_type = variant.VARIANT_STRING
            variant.string_value.original_size = namespace.original_size
            variant.string_value.value = namespace.obj
        elif "binary" == namespace.common_type:
            variant.variant_type = variant.VARIANT_BINARY
            variant.binary_value.original_size = namespace.original_size
            variant.binary_value.value = namespace.obj
        else:
            raise ValueError("Invalid string type %s", str(type(namespace.obj)))

    def _dump_primitive_namespace(self, namespace, variant, log_errors):
        self._dump_dumped_object_namespace(namespace, variant, log_errors)
        self._dump_primitive(namespace.obj, namespace.type, variant, PythonObjectNamespace.ObjectDumpConfig.UNLIMITED_STRING)

    def _dump_formatted_namespace(self, namespace, variant, log_errors):
        variant.variant_type = variant.VARIANT_FORMATTED_MESSAGE
        variant.message_value.message = namespace.obj

    def _dump_unknown_namespace(self, namespace, variant, log_errors):
        variant.variant_type = variant.VARIANT_UKNOWN_OBJECT
        variant.original_type = namespace.type

    def _dump_python_object(self, obj, variant, current_depth, config, log_errors):
        try:
            self._dump_python_object_unsafe(obj, variant, current_depth, config, log_errors)
        except Exception as e:
            message = "Failed to serialize namespace"

            variant.Clear()
            variant.variant_type = variant.VARIANT_ERROR

            if log_errors:
                from .error import Error
                Error(exc=e, message=message).dump(variant.error_value)
                logger.exception(message)

    def _dump_python_object_unsafe(self, obj, variant, current_depth, config, log_errors):
        if current_depth == config.max_depth:
            self._dump_max_depth(obj, variant)
        else:
            self._dump_base_object(obj, variant, current_depth, config, log_errors)

            if self._is_primitive(obj):
                self._dump_primitive(obj, str(type(obj)), variant, config.max_string)
            elif isinstance(obj, LIST_TYPE):
                self._dump_list(obj, variant, current_depth, config, log_errors)
            elif isinstance(obj, dict):
                self._dump_dictionary(obj, variant, current_depth, config, log_errors)
            elif isinstance(obj, BaseException):
                self._dump_exception(obj, variant, current_depth, config, log_errors)
            elif isinstance(obj, TracebackType):
                self._dump_traceback(obj, variant, current_depth, config, log_errors)
            elif NamespaceSerializer.is_numpy_obj(obj):
                self._dump_primitive(obj.item(), str(type(obj)), variant, config.max_string)
            elif hasattr(obj, '__dict__'):
                self._dump_user_class(obj, variant, current_depth, config)
            else:
                self._dump_not_supported(obj, variant)

        # If debugging NamespaceSerializer
        if ProtobufConfiguration.NAMESPACE_SERIALIZER_DUMPING:

            try:
                # We have to write to a local file as logging itself is using NamespaceSerializer
                with open(ProtobufConfiguration.NAMESPACE_SERIALIZER_DUMPING, 'a') as f:
                    try:
                        f.write('Attempting dump of-\t' + str(type(obj)) + '\n')
                        dump = variant.SerializeToString()
                        f.write('Dump successful. Size-\t' + str(len(dump)) + '\n')
                    except Exception:
                        f.write('Erorr while processing object\n')
                        f.write(traceback.format_exc())
                        f.write('\n')
            except IOError:
                # We have to write to console as we have nothing else
                print('Failed to open file')

    BUILTIN_ATTRIBUTES_IGNORE = ['__dict__', '__module__', '__weakref__', '__name__', '__doc__', '__bases__']

    def _dump_traceback(self, obj, variant, current_depth, config, log_errors):
        # python separates the "forward" stack (callees of the except clause)
        # and the "backward" stack (callers of above)
        # Possibly would be more useful to wrap this in a StackNamespace
        tb = traceback.format_tb(obj)
        tb[1:1] = traceback.format_stack(obj.tb_frame.f_back)
        value = ''.join(tb)

        variant.variant_type = variant.VARIANT_STRING
        variant.string_value.original_size = len(value)
        variant.string_value.value = value

    def _dump_base_object(self, obj, variant, current_depth, config, log_errors):
        variant.original_type = str(type(obj))

        if hasattr(obj, '__dict__'):
            # __dict is copied before iteration, as it might
            # change in another thread. We do not deep copy,
            # because we don't really mind if the values
            # change.
            for key, value in six.iteritems(obj.__dict__.copy()):
                if key not in self.BUILTIN_ATTRIBUTES_IGNORE:
                    attribute = variant.attributes.add()
                    attribute.name = key
                    self._dump_python_object(value, attribute.value, current_depth+1, config, log_errors)

        if hasattr(obj, '__slots__') and obj.__slots__:
            items = obj.__slots__
            # py4j (used by pyspark to communicate with Java proxy objects) sets __slots__ to Java proxy objects,
            # and supports __dir__ instead.
            if not isinstance(items, Iterable):
                items = dir(items)
            for key in list(items):
                if key not in self.BUILTIN_ATTRIBUTES_IGNORE:
                    attribute = variant.attributes.add()
                    attribute.name = key
                    try:
                        value = getattr(obj, key)
                    except AttributeError:
                        value = None
                    self._dump_python_object(value, attribute.value, current_depth + 1, config, log_errors)

    try:
        BINARY_TYPES = (buffer, bytearray)
        CODE_TYPES = (FunctionType, MethodType, TypeType)
        PRIMITIVE_TYPES = (type(None), int, long, float, str, unicode, complex) + BINARY_TYPES + CODE_TYPES + (datetime.datetime,)

    except NameError:
        BINARY_TYPES = (bytearray, bytes)
        CODE_TYPES = (FunctionType, MethodType, type)
        PRIMITIVE_TYPES = (type(None), int, float, str, complex) + BINARY_TYPES + CODE_TYPES + (datetime.datetime,)

    @staticmethod
    def _is_primitive(obj):
        return isinstance(obj, NamespaceSerializer.PRIMITIVE_TYPES)

    def _dump_max_depth(self, namespace, variant):
        variant.variant_type = variant.VARIANT_MAX_DEPTH

    def _dump_primitive(self, obj, original_type, variant, max_string):
        if obj is None:
            variant.variant_type = variant.VARIANT_NONE

        elif isinstance(obj, int) and (obj < Int32ValueChecker._MAX) and (obj > Int32ValueChecker._MIN):
            variant.variant_type = variant.VARIANT_INT
            variant.int_value = int(obj)

        elif isinstance(obj, six.integer_types) and (obj < Int64ValueChecker._MAX) and (obj > Int64ValueChecker._MIN):
            variant.variant_type = variant.VARIANT_LONG
            variant.long_value = int(obj)

        elif isinstance(obj, six.integer_types):
            variant.variant_type = variant.VARIANT_LARGE_INT
            variant.large_int_value.value = str(obj)

        elif isinstance(obj, bool):
            variant.variant_type = variant.VARIANT_INT
            variant.int_value = int(obj)

        elif isinstance(obj, float):
            variant.variant_type = variant.VARIANT_DOUBLE
            variant.double_value = float(obj)

        elif isinstance(obj, six.string_types):
            variant.variant_type = variant.VARIANT_STRING
            variant.string_value.original_size = len(obj)

            if len(obj) > max_string:
                obj = obj[:max_string]

            string = self.normalize_string(obj)
            variant.string_value.value = string

        elif isinstance(obj, self.BINARY_TYPES) or original_type == 'binary_type':
            variant.variant_type = variant.VARIANT_BINARY
            variant.binary_value.original_size = len(obj)

            if len(obj) > max_string:
                obj = obj[:max_string]

            variant.binary_value.value = bytes(obj)

        elif isinstance(obj, self.CODE_TYPES):
            variant.variant_type = variant.VARIANT_CODE_OBJECT
            variant.code_value.name = self.normalize_string(obj.__name__)
            if hasattr(obj, '__code__') and hasattr(obj.__code__, 'co_filename'):
                variant.code_value.filename = self.normalize_string(obj.__code__.co_filename)
                variant.code_value.lineno = int(obj.__code__.co_firstlineno)
            if hasattr(obj, '__module__') and obj.__module__:
                variant.code_value.module = self.normalize_string(obj.__module__)

        elif isinstance(obj, complex):
            variant.variant_type = variant.VARIANT_COMPLEX
            variant.complex_value.real = float(obj.real)
            variant.complex_value.imaginary = float(obj.imag)

        elif isinstance(obj, datetime.datetime):
            self._dump_datetime(obj, variant)

        else:
            raise ValueError("Object is not a supported primitive!", type(obj))

    def _dump_datetime(self, obj, variant):
        if obj.tzinfo:
            obj = obj.replace(tzinfo=None)

        variant.variant_type = variant.VARIANT_TIME
        variant.time_value.FromDatetime(obj)

    def _dump_list(self, collection, variant, current_depth, config, log_errors):
        variant.variant_type = variant.VARIANT_LIST
        variant.list_value.type = ListNamespace.get_common_type(collection)
        if ListNamespace.is_numpy_obj(collection):
            collection = collection.tolist()
        variant.list_value.original_size = len(collection)

        # Dump only if we are not too deep
        if current_depth < config.max_collection_dump:

            for index, item in enumerate(collection):
                if index >= config.max_width:
                    break

                variant_item = variant.list_value.values.add()
                self._dump_python_object(item, variant_item, current_depth+1, config, log_errors)

    def _dump_dictionary(self, collection, variant, current_depth, config, log_errors):
        variant.variant_type = variant.VARIANT_MAP
        variant.map_value.original_size = len(collection)

        # Dump only if we are not too deep
        if current_depth < config.max_collection_dump:

            i = 0

            for key, value in six.iteritems(collection):
                i += 1
                if i > config.max_width:
                    break

                pair = variant.map_value.pairs.add()
                self._dump_python_object(key, pair.first, current_depth+1, config, log_errors)
                self._dump_python_object(value, pair.second, current_depth+1, config, log_errors)

    def _dump_exception(self, exc, variant, current_depth, config, log_errors):
        variant.variant_type = variant.VARIANT_OBJECT

        args = variant.attributes.add()
        args.name = "args"
        self._dump_python_object(exc.args, args.value, current_depth + 1, config, log_errors)

    def _dump_user_class(self, obj, variant, current_depth, config):
        variant.variant_type = variant.VARIANT_OBJECT

    def _dump_not_supported(self, obj, variant):
        variant.variant_type = variant.VARIANT_UKNOWN_OBJECT

    def _dump_dumped_object_namespace(self, namespace, variant, log_errors):
        variant.original_type = namespace.type

        for key, value in six.iteritems(namespace.attributes):
            attribute = variant.attributes.add()
            attribute.name = key
            self.dump(value, attribute.value, log_errors)

    def _dump_user_object_namespace(self, namespace, variant, log_errors):
        self._dump_dumped_object_namespace(namespace, variant, log_errors)
        variant.variant_type = variant.VARIANT_OBJECT

    def _dump_list_namespace(self, namespace, variant, log_errors):
        self._dump_dumped_object_namespace(namespace, variant, log_errors)

        variant.variant_type = variant.VARIANT_LIST
        variant.list_value.type = namespace.common_type
        variant.list_value.original_size = namespace.original_size

        for item in namespace:
            variant_item = variant.list_value.values.add()
            self.dump(item, variant_item, log_errors)

    def _dump_dictionary_namespace(self, namespace, variant, log_errors):
        self._dump_dumped_object_namespace(namespace, variant, log_errors)

        variant.variant_type = variant.VARIANT_MAP
        variant.map_value.original_size = namespace.original_size

        for key, value in six.iteritems(namespace):
            pair = variant.map_value.pairs.add()

            self.dump(key, pair.first, log_errors)
            self.dump(value, pair.second, log_errors)

    def _dump_error_namespace(self, namespace, variant, log_errors):
        variant.variant_type = variant.VARIANT_ERROR
        variant.error_value.message = namespace.message.obj
        self.dump(namespace.parameters, variant.error_value.parameters, log_errors)
        self.dump(namespace.exc, variant.error_value.exc, log_errors)
        self.dump(namespace.traceback, variant.error_value.traceback, log_errors)

    def _dump_max_depth_namespace(self, namespace, variant, log_errors):
        variant.variant_type = variant.VARIANT_MAX_DEPTH

    def dump_code_namespace(self, namespace, variant, log_errors):
        self._dump_dumped_object_namespace(namespace, variant, log_errors)

        variant.variant_type = variant.VARIANT_CODE_OBJECT
        variant.code_value.name = namespace.name
        variant.code_value.module = namespace.module
        variant.code_value.filename = namespace.filename
        variant.code_value.lineno = namespace.lineno

    def dump_dynamic_namespace(self, namespace, variant, log_errors):
        variant.variant_type = variant.VARIANT_DYNAMIC

    def dump_delayed_namespace(self, namespace, variant, log_errors):
        variant.MergeFrom(namespace.get_variant())

    def dump_type_namespace(self, namespace, variant, log_errors):
        self._dump_dumped_object_namespace(namespace, variant, log_errors)

        variant.variant_type = variant.VARIANT_TYPE
        variant.type_value.name = namespace.name

    def _load_variant(self, variant):
        # NOTE: This the common types are partially duplicated with PythonObjectNamespace.get_common_type

        try:
            if variant.variant_type == rook_pb2.Variant.VARIANT_NONE:
                return DumpedPrimitiveNamespace(None, variant.original_type, "null", self._load_attributes(variant))
            elif variant.variant_type == rook_pb2.Variant.VARIANT_INT:
                return DumpedPrimitiveNamespace(variant.int_value, variant.original_type, "int", self._load_attributes(variant))
            elif variant.variant_type == rook_pb2.Variant.VARIANT_LONG:
                return DumpedPrimitiveNamespace(variant.long_value, variant.original_type, "int", self._load_attributes(variant))
            elif variant.variant_type == rook_pb2.Variant.VARIANT_DOUBLE:
                return DumpedPrimitiveNamespace(variant.double_value, variant.original_type, "float", self._load_attributes(variant))
            elif variant.variant_type == rook_pb2.Variant.VARIANT_BINARY:
                return StringNamespace(variant.binary_value.value, variant.binary_value.original_size,
                                       variant.original_type, "binary", self._load_attributes(variant))
            elif variant.variant_type == rook_pb2.Variant.VARIANT_STRING:
                return StringNamespace(variant.string_value.value, variant.string_value.original_size,
                                       variant.original_type, "string", self._load_attributes(variant))
            elif variant.variant_type == rook_pb2.Variant.VARIANT_TIME:
                return DumpedPrimitiveNamespace(variant.time_value.ToDatetime(), variant.original_type,
                                                "datetime", self._load_attributes(variant))
            elif variant.variant_type == rook_pb2.Variant.VARIANT_LIST:
                return self._load_list(variant)
            elif variant.variant_type == rook_pb2.Variant.VARIANT_MAP:
                return self._load_dictionary(variant)
            elif variant.variant_type == rook_pb2.Variant.VARIANT_OBJECT:
                return self._load_user_class(variant)
            elif variant.variant_type == rook_pb2.Variant.VARIANT_NAMESPACE:
                return self._load_container_namespace(variant)
            elif variant.variant_type == rook_pb2.Variant.VARIANT_ERROR:
                return self._load_error(variant.error_value)
            elif variant.variant_type == rook_pb2.Variant.VARIANT_MAX_DEPTH:
                return self._load_max_depth()
            elif variant.variant_type == rook_pb2.Variant.VARIANT_FORMATTED_MESSAGE:
                return self._load_formatted_namespace(variant)
            elif variant.variant_type == rook_pb2.Variant.VARIANT_UKNOWN_OBJECT:
                return UnknownNamespace(variant.original_type, self._load_attributes(variant))
            elif variant.variant_type == rook_pb2.Variant.VARIANT_CODE_OBJECT:
                return self._load_code_object(variant)
            elif variant.variant_type == rook_pb2.Variant.VARIANT_LARGE_INT:
                return DumpedPrimitiveNamespace(int(variant.large_int_value.value), variant.original_type,
                                                "int", self._load_attributes(variant))
            elif variant.variant_type == rook_pb2.Variant.VARIANT_COMPLEX:
                return DumpedPrimitiveNamespace(complex(variant.complex_value.real, variant.complex_value.imaginary),
                                                variant.original_type, "complex", self._load_attributes(variant))
            elif variant.variant_type == rook_pb2.Variant.VARIANT_UNDEFINED:
                return DumpedPrimitiveNamespace(None, variant.original_type, "null", self._load_attributes(variant))
            elif variant.variant_type == rook_pb2.Variant.VARIANT_DYNAMIC:
                return DynamicObjectNamespace()
            else:
                raise ValueError("Invalid type", variant.variant_type)
        except Exception as e:
            message = "Failed to serialize namespace"
            logger.exception(message)

            from .error import Error
            error = Error(exc=e, message=message)

            # This is a duplication of Error as we can't use it here safely
            return ErrorNamespace(PythonObjectNamespace(message),
                                  PythonObjectNamespace(error.parameters),
                                  PythonObjectNamespace(error.exc),
                                  PythonObjectNamespace('\n'.join(traceback.format_tb(error.traceback))))

    def _load_attributes(self, variant):
        attributes = dict()

        for attribute in variant.attributes:
            attributes[attribute.name] = self._load_variant(attribute.value)

        return attributes

    def _load_list(self, variant):
        result = list()

        for item in variant.list_value.values:
            result.append(self._load_variant(item))

        return ListNamespace(result, variant.list_value.original_size, variant.original_type, variant.list_value.type,
                             self._load_attributes(variant))

    def _load_dictionary(self, variant):
        result = dict()

        for item in variant.map_value.pairs:
            result[self._load_variant(item.first)] = self._load_variant(item.second)

        return DictNamespace(result, variant.map_value.original_size, variant.original_type,
                             self._load_attributes(variant))

    def _load_user_class(self, variant):
        return UserObjectNamespace(variant.original_type, self._load_attributes(variant))

    def _load_container_namespace(self, variant):
        result = dict()

        for attribute in variant.namespace_value.attributes:
            result[attribute.name] = self._load_variant(attribute.value)

        return ContainerNamespace(result)

    def _load_error(self, error):
        return ErrorNamespace(PythonObjectNamespace(error.message),
                              self._load_variant(error.parameters),
                              self._load_variant(error.exc),
                              self._load_variant(error.traceback))

    def _load_max_depth(self):
        return MaxDepthNamespace()

    def _load_formatted_namespace(self, variant):
        return FormattedNamespace(variant.message_value.message)

    def _load_code_object(self, variant):
        return CodeObjectNamespace(variant.code_value.name,
                                   variant.code_value.module,
                                   variant.code_value.filename,
                                   variant.code_value.lineno,
                                   variant.original_type,
                                   self._load_attributes(variant))

    @staticmethod
    def normalize_string(obj):
        if six.PY2:
            if isinstance(obj, str):
                return unicode(obj, errors="replace")
            else:
                return unicode(obj)
        else:
            return str(obj)

    @staticmethod
    def is_numpy_obj(obj):
        if not numpy:
            return False

        return isinstance(obj, numpy.generic)
