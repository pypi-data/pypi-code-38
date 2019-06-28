import collections
import inspect
import logging
import warnings
from abc import abstractmethod
from enum import Enum

import google.protobuf.descriptor
import google.protobuf.message
import google.protobuf.pyext._message
from google.protobuf.symbol_database import Default as get_grpc_symbol_database
from interface_meta import InterfaceMeta, override

from .utils import cast_enum_type_to_int


GRPC_SYMBOL_DATABASE = get_grpc_symbol_database()


class GRPCMessageWrapperMeta(InterfaceMeta):

    _WRAPPERS = {}
    _ENUM_TYPES = {}

    def __register_implementation__(cls):
        if not cls._MESSAGE_TYPE:
            return

        if not inspect.isclass(cls._MESSAGE_TYPE) or not issubclass(cls._MESSAGE_TYPE, google.protobuf.message.Message):
            raise ValueError(f"Class `{cls.__name__}` has an invalid `_MESSAGE_TYPE`. Object of type `{cls._MESSAGE_TYPE.__class__.__name__}` is not a subclass of `google.protobuf.message.Message`.")

        # Register subclass
        cls._WRAPPERS[cls._MESSAGE_TYPE.DESCRIPTOR.full_name] = cls

        # Add message fields as attributes of the class
        for field, desc in cls._MESSAGE_TYPE.DESCRIPTOR.fields_by_name.items():

            if field in cls._IGNORED_FIELDS:
                continue

            if hasattr(cls, field):
                # Check that it is not a collision at the metaclass level
                collides_in_metaclass = True
                for base in cls.mro():
                    if field in base.__dict__:
                        collides_in_metaclass = False
                        break

                if not collides_in_metaclass:
                    logging.warning(f"Field `{field}` of `{cls._MESSAGE_TYPE}` is masked by class attributes.")
                    continue

            # Add field wrappers so that the attributes appear in class documentation
            setattr(
                cls, field, cls.__get_field_property_method(field)
            )

            # Add enum specifications to class definition
            if desc.enum_type:
                if desc.enum_type.full_name not in cls._ENUM_TYPES:
                    cls._ENUM_TYPES[desc.enum_type.full_name] = (
                        Enum(desc.enum_type.name, [
                            (v.name, v.number)
                            for v in desc.enum_type.values
                        ])
                    )

    def __get_field_property_method(cls, field):

        def get_field(self):
            return self.__getattr__(field)
        get_field.__name__ = field

        def set_field(self):
            return self.__setattr__(field)

        return property(fget=get_field, fset=set_field)

    def for_kind(cls, kind):
        if kind is None:
            return
        if isinstance(kind, google.protobuf.descriptor.Descriptor):
            kind = kind.full_name
        if isinstance(kind, str):
            kind = GRPC_SYMBOL_DATABASE.GetSymbol(kind)
        assert inspect.isclass(kind) and issubclass(kind, google.protobuf.message.Message)
        if kind.DESCRIPTOR.full_name not in cls._WRAPPERS:
            GRPCMessageWrapperMeta(kind.DESCRIPTOR.full_name, (GRPCMessageWrapper, ), {'_MESSAGE_TYPE': kind})
        return cls._WRAPPERS[kind.DESCRIPTOR.full_name]

    def for_message(cls, message):
        if isinstance(message, google.protobuf.message.Message):
            return cls.for_kind(type(message))(message)
        return message

    def from_json(cls, json, message_type=None):
        message_type = message_type or getattr(cls, "_MESSAGE_TYPE", None)
        if not message_type:
            raise RuntimeError("`from_json()` can only be called on a wrapper which has `_MESSAGE_TYPE` set, or by passing in message_type specifically.")
        from google.protobuf.json_format import ParseDict
        return cls.for_message(ParseDict(json, message_type()))


class GRPCMessageWrapper(metaclass=GRPCMessageWrapperMeta):

    _MESSAGE_TYPE = None
    _IMMUTABLE_FIELDS = ()
    _IGNORED_FIELDS = ()

    __slots__ = ['__message', '__persisted_fields']

    def __init__(self, _message=None, **kwargs):
        if self._MESSAGE_TYPE is None:
            raise RuntimeError(
                "`GRPCMessageWrapper` should not be instantiated directly. "
                "Please use `GRPCMessageWrapper.for_message(...)` instead."
            )
        self.__persisted_fields = {}
        self.__message = _message or self._MESSAGE_TYPE()
        self._init(**kwargs)

    def _init(self, **kwargs):
        self << kwargs

    @property
    def _message(self):
        return self.__message

    @property
    def _message_copy(self):
        message = type(self.__message)()
        message.CopyFrom(self.__message)
        return message

    def __dir__(self):
        return set([*(f.name for f in self.__message.DESCRIPTOR.fields if f.name not in self._IGNORED_FIELDS), *super().__dir__()])

    @property
    def __message_fields(self):
        return set(self._message.DESCRIPTOR.fields_by_name)

    def __get_field_descriptor(self, field):
        return self._message.DESCRIPTOR.fields_by_name[field]

    def __get_wrapped_value(self, field, value, evaluate_getters=True):
        descriptor = self.__get_field_descriptor(field)

        # Warn about deprecated field usage
        if descriptor.GetOptions().deprecated:
            warnings.warn(
                f"`{self._message.__class__.__name__}.{field}` is deprecated and may disappear in the future.",
                DeprecationWarning
            )

        if descriptor.label == descriptor.LABEL_REPEATED:
            if descriptor.message_type and descriptor.message_type.GetOptions().map_entry:
                wrapper = GRPCMessageWrapper.for_kind(descriptor.message_type.fields_by_name['value'].message_type)
                value = GRPCMapMessageWrapper(value, wrapper=wrapper)
            else:
                wrapper = (
                    GRPCMessageWrapper._ENUM_TYPES[descriptor.enum_type.full_name]
                    if descriptor.enum_type else
                    GRPCMessageWrapper.for_kind(descriptor.message_type)
                )
                value = GRPCRepeatedMessageWrapper(value, wrapper=wrapper)
        elif descriptor.enum_type:
            value = GRPCMessageWrapper._ENUM_TYPES[descriptor.enum_type.full_name](value)
        else:
            value = GRPCMessageWrapper.for_message(value)

        if evaluate_getters and hasattr(value, '__get__'):
            value = value.__get__() if self.__message.HasField(field) else None

        return value

    def __get_wrapped_field_value(self, field, evaluate_getters=True):
        return self.__get_wrapped_value(
            field=field,
            value=getattr(self.__message, field),
            evaluate_getters=evaluate_getters,
        )

    def __set_field_value(self, field, value):
        descriptor = self.__get_field_descriptor(field)

        # Allow wrappers to handle setting if this is not directly set on the
        # message wrapped by this instance.
        wrapper = self.__get_wrapped_field_value(field, evaluate_getters=False)
        if hasattr(wrapper, '__set__'):
            return wrapper.__set__(value)

        # Prepare enum values
        if descriptor.enum_type:
            if self._MESSAGE_TYPE:
                value = cast_enum_type_to_int(
                    enum_type=GRPCMessageWrapper._ENUM_TYPES[descriptor.enum_type.full_name],
                    value=value
                )
            else:
                logging.warning(f"`{field}` is an enum type, but messages of type `{self._message.__class__}` have not yet been individually wrapped and so only integer enum code will be accepted. Use with care.")

        self.__persisted_fields.pop(field, None)
        return self.__message.MergeFrom(self.__message.__class__(**{field: value}))

    # External API

    def __getattr__(self, attr):
        if attr not in self.__message_fields or attr in self._IGNORED_FIELDS:
            raise AttributeError(attr)

        if attr not in self.__persisted_fields:
            self.__persisted_fields[attr] = self.__get_wrapped_field_value(field=attr)
        return self.__persisted_fields[attr]

    def __setattr__(self, attr, value):
        if attr.startswith('_'):
            return super().__setattr__(attr, value)
        elif attr not in self.__message_fields or attr in self._IGNORED_FIELDS:
            raise AttributeError(attr)
        elif attr in self._IMMUTABLE_FIELDS:
            raise AttributeError(f"`{attr}` is immutable.")

        return self.__set_field_value(field=attr, value=value)

    def __delattr__(self, attr):
        self.__message.ClearField(attr)
        self.__persisted_fields.pop(attr, None)

    def __repr__(self):
        return f"GRPCMessageWrapper<{self.__class__.__name__}>"

    def __lshift__(self, other):
        if not isinstance(other, dict):
            return NotImplemented
        for key, value in other.items():
            setattr(self, key, value)
        return self

    def _compare(self, ref=None):
        ref = ref or type(self.__message)()
        if isinstance(ref, GRPCMessageWrapper):
            ref = ref._message
        if self.__message == ref:
            return

        comparison = {}

        for field_name in self.__message_fields:
            if field_name in self._IGNORED_FIELDS or field_name in self._IMMUTABLE_FIELDS:
                continue
            if getattr(ref, field_name) != getattr(self.__message, field_name):
                field_value = self.__get_wrapped_field_value(field_name, evaluate_getters=False)
                if isinstance(field_value, GRPCMessageWrapper):
                    nested_comparison = field_value._compare(ref=getattr(ref, field_name))
                    if nested_comparison:
                        comparison[field_name] = nested_comparison
                else:
                    comparison[field_name] = (
                        self.__get_wrapped_value(field=field_name, value=getattr(ref, field_name)),
                        self.__get_wrapped_field_value(field_name),
                    )

        return comparison

    def _to_json(self):
        from google.protobuf.json_format import MessageToDict
        return MessageToDict(self._message, including_default_value_fields=True)


class GRPCInvisibleWrapper(GRPCMessageWrapper):

    @abstractmethod
    def __get__(self):
        raise NotImplementedError

    @abstractmethod
    def __set__(self, value):
        raise NotImplementedError


class GRPCInvisibleSequenceWrapper(GRPCInvisibleWrapper):

    _SEQUENCE_ATTR = None

    @override
    def __get__(self):
        return getattr(self, self._SEQUENCE_ATTR)

    @override
    def __set__(self, value):
        sequence = getattr(self, self._SEQUENCE_ATTR)
        while sequence:
            sequence.pop()
        sequence.extend(v._message if isinstance(v, GRPCMessageWrapper) else v for v in value)

    @override
    def _compare(self, ref=None):
        return super()._compare(ref=ref).get(self._SEQUENCE_ATTR)


class GRPCContainerWrapper:

    def __init__(self, wrapper=None):
        self._wrapper = wrapper
        self.__wrapper_cache = {}

    def _wrap(self, obj):
        cache_key = id(obj)
        if cache_key not in self.__wrapper_cache:
            self.__wrapper_cache[cache_key] = self._wrapper(obj) if self._wrapper else GRPCMessageWrapper.for_message(obj)
        return self.__wrapper_cache[cache_key]

    def _unwrap(self, obj):
        if isinstance(obj, GRPCMessageWrapper):
            return obj._message
        if isinstance(self._wrapper, Enum):
            return cast_enum_type_to_int(self._wrapper, obj)
        return obj

    def _wrapper_purge(self, obj):
        self.__wrapper_cache.pop(id(obj), None)


class GRPCMapMessageWrapper(GRPCContainerWrapper, collections.abc.MutableMapping):

    def __init__(self, map, wrapper=None):
        self._map = map
        GRPCContainerWrapper.__init__(self, wrapper=wrapper)

    # MutableMapping implementations

    def __getitem__(self, key):
        if key in self._map:
            return self._wrap(self._map[key])
        raise KeyError(key)

    def __setitem__(self, key, value):
        self._wrapper_purge(self._map[key])
        if self._wrapper:
            self._map[key].MergeFrom(self._unwrap(value))
        else:
            self._map.__setitem__(key, value)

    def __delitem__(self, key):
        self._wrapper_purge(self._map[key])
        return self._map.__delitem__(key)

    def __iter__(self):
        return self._map.__iter__()

    def __len__(self):
        return self._map.__len__()

    # Additional convenience methods

    def add(self, key, **kwargs):
        self[key] = self._wrapper(**kwargs)

    def __repr__(self):
        return repr(dict(self))


class GRPCRepeatedMessageWrapper(GRPCContainerWrapper, collections.abc.MutableSequence):

    def __init__(self, sequence, wrapper=None):
        self._sequence = sequence
        GRPCContainerWrapper.__init__(self, wrapper=wrapper)

    def __set__(self, values):
        # To avoid clearing existing values if new values are invalid, we extend
        # first, and then clear up to the first new index.
        index = len(self._sequence)
        self.extend(values)
        for i in range(index):
            self.pop(0)

    # MutableSequence implementations

    def __getitem__(self, index):
        return self._wrap(self._sequence[index])

    def __setitem__(self, index, obj):
        self._wrapper_purge(self._sequence[index])
        return self._sequence.__setitem__(index, self._unwrap(obj))

    def __delitem__(self, index):
        self._wrapper_purge(self._sequence[index])
        return self._sequence.__delitem__(index)

    def __len__(self):
        return len(self._sequence)

    def insert(self, index, obj):
        obj = self._unwrap(obj)
        if isinstance(self._sequence, google.protobuf.pyext._message.RepeatedCompositeContainer):
            if index == len(self):
                self._sequence.extend([obj])
            else:
                raise RuntimeError("Insertion is only supported for repeated scalar containers.")
        else:
            self._sequence.insert(index, obj)

    # Additional convenience methods

    def add(self, **kwargs):
        if isinstance(self._sequence, google.protobuf.pyext._message.RepeatedCompositeContainer):
            self.append(self._wrapper(**kwargs))
        else:
            RuntimeError("Addition is only supported for repeated composite containers. Use `.append()` for scalar values.")

    def __repr__(self):
        return repr(list(self))
