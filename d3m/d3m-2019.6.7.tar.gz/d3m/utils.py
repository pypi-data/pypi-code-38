import abc
import argparse
import base64
import collections
import contextlib
import copy
import datetime
import decimal
import enum
import hashlib
import inspect
import json
import logging
import numbers
import operator
import os
import os.path
import types
import typing
import sys
import unittest
import uuid
from urllib import parse as url_parse

import custom_inherit  # type: ignore
import frozendict  # type: ignore
import git  # type: ignore
import jsonpath_ng  # type: ignore
import jsonschema  # type: ignore
import numpy  # type: ignore
import pandas  # type: ignore
import typing_inspect  # type: ignore
import yaml  # type: ignore
import pyrsistent  # type: ignore
from pytypes import type_util  # type: ignore

import d3m
from d3m import deprecate, exceptions

# Only types without elements can be listed here. If they are elements, we have to
# check all elements as well.
KNOWN_IMMUTABLE_TYPES = (
    str, int, float, bool, numbers.Integral, numbers.Complex, decimal.Decimal,
    numbers.Real, numpy.integer, numpy.float32, numpy.float64, bytes,
    datetime.date, datetime.time, datetime.datetime, type(None), enum.Enum,
)

HASH_ID_NAMESPACE = uuid.UUID('8614b2cc-89ef-498e-9254-833233b3959b')

PACKAGE_BASE = os.path.dirname(d3m.__file__)


def current_git_commit(path: str, search_parent_directories: bool = True) -> str:
    """
    Returns a git commit hash of the repo at ``path`` or above if ``search_parent_directories`` is ``True``.

    When used to get a commit hash of a Python package, for this to work, the package has
    to be installed in "editable" mode (``pip install -e``).

    Parameters
    ----------
    path : str
        A path to repo or somewhere under the repo.
    search_parent_directories : bool
        Whether to search for a git repository in directories above ``path``.

    Returns
    -------
    str
        A git commit hash.
    """

    repo = git.Repo(path=path, search_parent_directories=search_parent_directories)
    return repo.head.object.hexsha


# Using typing.TypeVar in type signature does not really work, so we are using type instead.
# See: https://github.com/python/typing/issues/520
def get_type_arguments(cls: type, *, unique_names: bool = False) -> typing.Dict[type, type]:
    """
    Returns a mapping between type arguments and their types of a given class ``cls``.

    Parameters
    ----------
    cls : type
        A class to return mapping for.
    unique_names : bool
        Should we force unique names of type parameters.

    Returns
    -------
    Dict[TypeVar, type]
        A mapping from type argument to its type.
    """

    # Using typing.TypeVar in type signature does not really work, so we are using type instead.
    # See: https://github.com/python/typing/issues/520
    result: typing.Dict[type, type] = {}

    for base_class in inspect.getmro(typing_inspect.get_origin(cls)):
        if base_class == typing.Generic:
            break

        if not typing_inspect.is_generic_type(base_class):
            continue

        parameters = typing_inspect.get_parameters(base_class)

        # We are using _select_Generic_superclass_parameters and not get_Generic_parameters
        # so that we can handle the case where the result is None.
        # See: https://github.com/Stewori/pytypes/issues/20
        arguments = type_util._select_Generic_superclass_parameters(cls, base_class)

        if arguments is None:
            arguments = [typing.Any] * len(parameters)

        if len(parameters) != len(arguments):
            raise TypeError("Number of parameters does not match number of arguments.")

        for parameter, argument in zip(parameters, arguments):
            if type_util.resolve_fw_decl(argument, module_name=base_class.__module__, globs=dir(sys.modules[base_class.__module__]))[1]:
                argument = argument.__forward_value__

            visited: typing.Set[type] = set()
            while typing_inspect.is_typevar(argument) and argument in result:
                if argument in visited:
                    raise RuntimeError("Loop while resolving type variables.")
                visited.add(argument)

                argument = result[argument]

            if parameter == argument:
                argument = typing.Any

            if parameter in result:
                if result[parameter] != argument:
                    raise TypeError("Different types for same parameter across class bases: {type1} vs. {type2}".format(
                        type1=result[parameter],
                        type2=argument,
                    ))
            else:
                result[parameter] = argument

    if unique_names:
        type_parameter_names = [parameter.__name__ for parameter in result.keys()]

        type_parameter_names_set = set(type_parameter_names)

        if len(type_parameter_names) != len(type_parameter_names_set):
            for name in type_parameter_names_set:
                type_parameter_names.remove(name)
            raise TypeError("Same name reused across different type parameters: {extra_names}".format(extra_names=type_parameter_names))

    return result


def is_instance(obj: typing.Any, cls: typing.Union[type, typing.Tuple[type]]) -> bool:
    # We do not want really to check generators. A workaround.
    # See: https://github.com/Stewori/pytypes/issues/49
    if isinstance(obj, types.GeneratorType):
        return False

    if isinstance(cls, tuple):
        cls = typing.Union[cls]  # type: ignore

    # "bound_typevars" argument has to be passed for this function to
    # correctly work with type variables.
    # See: https://github.com/Stewori/pytypes/issues/24
    return type_util._issubclass(type_util.deep_type(obj), cls, bound_typevars={})


def is_subclass(subclass: type, superclass: typing.Union[type, typing.Tuple[type]]) -> bool:
    # "bound_typevars" argument has to be passed for this function to
    # correctly work with type variables.
    # See: https://github.com/Stewori/pytypes/issues/24
    return type_util._issubclass(subclass, superclass, bound_typevars={})


def get_type(obj: typing.Any) -> type:
    typ = type_util.deep_type(obj, depth=1)

    if is_subclass(typ, type_util.Empty):
        typ = typing_inspect.get_last_args(typ)[0]

    return typ


def is_instance_method_on_class(method: typing.Any) -> bool:
    if is_class_method_on_class(method):
        return False

    if inspect.isfunction(method):
        return True

    if getattr(method, '__func__', None):
        return True

    return False


def is_class_method_on_class(method: typing.Any) -> bool:
    return inspect.ismethod(method)


def is_instance_method_on_object(method: typing.Any, object: typing.Any) -> bool:
    if not inspect.ismethod(method):
        return False

    if method.__self__ is object:
        return True

    return False


def is_class_method_on_object(method: typing.Any, object: typing.Any) -> bool:
    if not inspect.ismethod(method):
        return False

    if method.__self__ is type(object):
        return True

    return False


def is_type(obj: typing.Any) -> bool:
    return isinstance(obj, type) or obj is typing.Any or typing_inspect.is_tuple_type(obj) or typing_inspect.is_union_type(obj)


def type_to_str(obj: type) -> str:
    return type_util.type_str(obj, assumed_globals={}, update_assumed_globals=False)


class EnumMeta(enum.EnumMeta):
    def __new__(mcls, class_name, bases, namespace, **kwargs):  # type: ignore
        def __reduce_ex__(self: typing.Any, proto: int) -> typing.Any:
            return self.__class__, (self._value_,)

        if '__reduce_ex__' not in namespace:
            namespace['__reduce_ex__'] = __reduce_ex__

        cls = super().__new__(mcls, class_name, bases, namespace, **kwargs)

        def yaml_representer(dumper, data):  # type: ignore
            return yaml.ScalarNode('tag:yaml.org,2002:str', data.name)

        yaml.add_representer(cls, yaml_representer)

        return cls


class Enum(enum.Enum, metaclass=EnumMeta):
    """
    An implementation of `Enum` base class whose instances are equal to their string names, too.

    Moreover, it registers itself with "yaml" module to serialize itself as a string.
    """

    def __eq__(self, other):  # type: ignore
        if isinstance(other, str):
            return self.name == other

        return super().__eq__(other)

    # It must hold a == b => hash(a) == hash(b). Because we allow enums to be equal to names,
    # the easiest way to assure the condition is to hash everything according to their names.
    def __hash__(self):  # type: ignore
        return hash(self.name)


# Return type has to be "Any" because mypy does not support enums generated dynamically
# and complains about missing attributes when trying to access them.
def create_enum_from_json_schema_enum(
    class_name: str, obj: typing.Dict, json_paths: typing.Union[typing.Sequence[str], str], *,
    module: str = None, qualname: str = None, base_class: type = None
) -> typing.Any:
    if qualname is None:
        qualname = class_name

    if isinstance(json_paths, str):
        names = _get_names(obj, json_paths)
    else:
        names = []
        for path in json_paths:
            names += _get_names(obj, path)

    # Make the list contain unique names. It works in Python 3.6+ because dicts are ordered.
    names = list(dict.fromkeys(names))

    return Enum(value=class_name, names=names, start=1, module=module, qualname=qualname, type=base_class)  # type: ignore


def _get_names(obj: typing.Dict, path: str) -> typing.List:
    json_path_expression = jsonpath_ng.parse(path)
    return [match.value for match in json_path_expression.find(obj)]


# This allows other modules to register additional immutable values and types.
# We are doing it this way to overcome issues with import cycles.
additional_immutable_values: typing.Tuple[typing.Any, ...] = ()
additional_immutable_types: typing.Tuple[type, ...] = ()


def make_immutable_copy(obj: typing.Any) -> typing.Any:
    """
    Converts a given ``obj`` into an immutable copy of it, if possible.

    Parameters
    ----------
    obj : Any
        Object to convert.

    Returns
    -------
    Any
        An immutable copy of ``obj``.
    """

    if any(obj is immutable_value for immutable_value in additional_immutable_values):
        return obj

    if isinstance(obj, numpy.matrix):
        # One cannot iterate over a matrix segment by segment. You always get back
        # a matrix (2D structure) and not an array of rows or columns. By converting
        # it to an array such iteration segment by segment works.
        obj = numpy.array(obj)

    if isinstance(obj, KNOWN_IMMUTABLE_TYPES):
        # Because str is among known immutable types, it will not be picked apart as a sequence.
        return obj
    if additional_immutable_types and isinstance(obj, additional_immutable_types):
        return obj
    if is_type(obj):
        # Assume all types are immutable.
        return obj
    if isinstance(obj, typing.Mapping):
        # We simply always preserve order of the mapping. Because we want to make sure also mapping's
        # values are converted to immutable values, we cannot simply use MappingProxyType.
        return frozendict.FrozenOrderedDict((make_immutable_copy(k), make_immutable_copy(v)) for k, v in obj.items())
    if isinstance(obj, typing.Set):
        return frozenset(make_immutable_copy(o) for o in obj)
    if isinstance(obj, tuple):
        # To preserve named tuples.
        return type(obj)(make_immutable_copy(o) for o in obj)
    if isinstance(obj, pandas.DataFrame):
        return tuple(make_immutable_copy(o) for o in obj.itertuples(index=False, name=None))
    if isinstance(obj, typing.Sequence):
        return tuple(make_immutable_copy(o) for o in obj)

    raise TypeError("{obj} is not known to be immutable.".format(obj=obj))


def check_immutable(obj: typing.Any) -> None:
    """
    Checks that ``obj`` is immutable. Raises an exception if this is not true.

    Parameters
    ----------
    obj : any
        Object to check.
    """

    obj_type = type(obj)

    # First check common cases.
    if any(obj is immutable_value for immutable_value in additional_immutable_values):
        return
    if obj_type in KNOWN_IMMUTABLE_TYPES:
        return
    if obj_type is frozendict.FrozenOrderedDict:
        for k, v in obj.items():
            check_immutable(k)
            check_immutable(v)
        return
    if obj_type is tuple:
        for o in obj:
            check_immutable(o)
        return

    if isinstance(obj, KNOWN_IMMUTABLE_TYPES):
        return
    if additional_immutable_types and isinstance(obj, additional_immutable_types):
        return
    if isinstance(obj, tuple):
        # To support named tuples.
        for o in obj:
            check_immutable(o)
        return
    if is_type(obj):
        # Assume all types are immutable.
        return
    if obj_type is frozenset:
        for o in obj:
            check_immutable(o)
        return

    raise TypeError("{obj} is not known to be immutable.".format(obj=obj))


class Metaclass(custom_inherit._DocInheritorBase):
    """
    A metaclass which makes sure docstrings are inherited.

    It knows how to merge numpy-style docstrings and merge parent sections with
    child sections. For example, then it is not necessary to repeat documentation
    for parameters if they have not changed.
    """

    @staticmethod
    def class_doc_inherit(prnt_doc: str = None, child_doc: str = None) -> typing.Optional[str]:
        return custom_inherit.store['numpy'](prnt_doc, child_doc)

    @staticmethod
    def attr_doc_inherit(prnt_doc: str = None, child_doc: str = None) -> typing.Optional[str]:
        return custom_inherit.store['numpy'](prnt_doc, child_doc)


class AbstractMetaclass(abc.ABCMeta, Metaclass):
    """
    A metaclass which makes sure docstrings are inherited. For use with abstract classes.
    """


class GenericMetaclass(typing.GenericMeta, Metaclass):
    """
    A metaclass which makes sure docstrings are inherited. For use with generic classes (which are also abstract).
    """


class RefResolverNoRemote(jsonschema.RefResolver):
    def resolve_remote(self, uri: str) -> typing.Any:
        raise exceptions.NotSupportedError("Remote resolving disabled: {uri}".format(uri=uri))


def enum_validator(validator, enums, instance, schema):  # type: ignore
    if isinstance(instance, Enum):
        instance = instance.name

    yield from jsonschema.Draft4Validator.VALIDATORS['enum'](validator, enums, instance, schema)


# TODO: Once migrated to JSON Schema draft 6 or later, special handling of "integer" will not be needed anymore.
#       See: https://github.com/Julian/jsonschema/issues/557
class Draft4Validator(jsonschema.Draft4Validator):
    """
    JSON schema validator with the following extensions:

    * If a value is an instance of Python enumeration, its name is checked against JSON
      schema enumeration, instead of the value itself. When converting to a proper JSON
      these values should be enumeration's name.
    * For JSON type ``integer`` validator accepts also Python ``float`` values if they
      are numerically equivalent to an integer.
    """

    VALIDATORS = dict(jsonschema.Draft4Validator.VALIDATORS, **{
        'enum': enum_validator,
    })

    def is_type(self, instance: typing.Any, type: type) -> bool:
        if type == 'string' and isinstance(instance, Enum):
            return True
        elif type == 'integer' and isinstance(instance, float):
            return instance.is_integer()
        else:
            return super().is_type(instance, type)


draft4_format_checker = copy.deepcopy(jsonschema.draft4_format_checker)


@draft4_format_checker.checks('python-type')
def json_schema_is_python_type(instance: typing.Any) -> bool:
    return is_type(instance) or isinstance(instance, str)


def load_schema_validators(schemas: typing.Dict, load_validators: typing.Sequence[str]) -> typing.List[Draft4Validator]:
    validators = []

    for schema_filename in load_validators:
        for schema_uri, schema_json in schemas.items():
            if os.path.basename(schema_uri) == schema_filename:
                break
        else:
            raise exceptions.InvalidArgumentValueError("Cannot find schema \"{schema_filename}\".".format(schema_filename=schema_filename))

        # We validate schemas using unmodified validator.
        jsonschema.Draft4Validator.check_schema(schema_json)

        validator = Draft4Validator(
            schema=schema_json,
            types=dict(Draft4Validator.DEFAULT_TYPES, **{
                'array': (list, tuple, set),
                'object': (dict, frozendict.frozendict, frozendict.FrozenOrderedDict),
            }),
            resolver=RefResolverNoRemote(schema_json['id'], schema_json, schemas),
            format_checker=draft4_format_checker,
        )

        validators.append(validator)

    return validators


def datetime_for_json(timestamp: datetime.datetime) -> str:
    # Since Python 3.6 "astimezone" can be called on naive instances
    # that are presumed to represent system local time.
    # We remove timezone information before formatting to not have "+00:00" added and
    # we then manually add "Z" instead (which has equivalent meaning).
    return timestamp.astimezone(datetime.timezone.utc).replace(tzinfo=None).isoformat('T') + 'Z'


class JsonEncoder(json.JSONEncoder):
    """
    JSON encoder with extensions, among them the main ones are:

    * Frozen dict is encoded as a dict.
    * Python types are encoded into strings describing them.
    * Python enumerations are encoded into their string names.
    * Sets are encoded into lists.
    * Encodes ndarray and DataFrame as nested lists.
    * Encodes datetime into ISO format with UTC timezone.
    * Everything else which cannot be encoded is converted to a string.

    You probably want to use `to_json_structure` and not this class, because `to_json_structure`
    also encodes ``NaN`, ``Infinity``, and ``-Infinity`` as strings.

    It does not necessary make a JSON which can then be parsed back to reconstruct original value.
    """

    def default(self, o: typing.Any) -> typing.Any:
        # Importing here to prevent import cycle.
        from d3m.metadata import base

        if isinstance(o, numpy.matrix):
            # One cannot iterate over a matrix segment by segment. You always get back
            # a matrix (2D structure) and not an array of rows or columns. By converting
            # it to an array such iteration segment by segment works.
            o = numpy.array(o)

        if isinstance(o, frozendict.frozendict):
            return dict(o)
        if isinstance(o, frozendict.FrozenOrderedDict):
            return collections.OrderedDict(o)
        if is_type(o):
            return type_to_str(o)
        if isinstance(o, Enum):
            return o.name
        if o is base.ALL_ELEMENTS:
            return repr(o)
        if o is base.NO_VALUE:
            return repr(o)
        # For encoding numpy.int64. numpy.float64 already works.
        if isinstance(o, numpy.integer):
            return int(o)
        if isinstance(o, typing.Mapping):
            return collections.OrderedDict(o)
        if isinstance(o, typing.Set):
            return sorted(o, key=str)
        if isinstance(o, pandas.DataFrame):
            return list(o.itertuples(index=False, name=None))
        if isinstance(o, typing.Sequence):
            return list(o)
        if isinstance(o, decimal.Decimal):
            return float(o)
        if isinstance(o, bytes):
            return base64.b64encode(o).decode('utf8')
        if isinstance(o, datetime.datetime):
            return datetime_for_json(o)

        try:
            return super().default(o)
        except TypeError:
            return str(o)


json_constant_map = {
    '-Infinity': str(float('-Infinity')),
    'Infinity': str(float('Infinity')),
    'NaN': str(float('NaN')),
}


def to_json_structure(obj: typing.Any, *, normalize_numbers: bool = False) -> typing.Any:
    """
    In addition to what `JsonEncoder` encodes, this function also encodes as strings
    float ``NaN``, ``Infinity``, and ``-Infinity``.

    It does not necessary make a JSON structure which can then be parsed back to reconstruct original value.
    """

    # We do not use "allow_nan=False" here because we will handle those values during loading.
    # "JsonEncoder.default" is not called for float values so we cannot handle them there.
    # See: https://bugs.python.org/issue36841
    json_string = json.dumps(obj, cls=JsonEncoder)

    return json.loads(
        json_string,
        parse_constant=lambda constant: json_constant_map[constant],
        parse_int=float if normalize_numbers else None,
    )


class StreamToLogger:
    def __init__(self, logger: logging.Logger, level: typing.Union[str, int]) -> None:
        self.logger = logger
        self.level = logging._checkLevel(level)  # type: ignore
        self.closed = False

    # Here we are trying to test for the case of a recursive loop which can happen
    # if you are using "logging.StreamHandler" in your logging configuration (e.g., to
    # output logging to a console) and configure it after "redirect_to_logging' context
    # manager has been entered.
    def _check_recursion(self) -> bool:
        # We start at "2" so that we start from outside of this file.
        frame = sys._getframe(2)
        line_number = None
        try:
            i = 0
            # If loop is happening, it is generally looping inside less than 10 frames,
            # so we exit after 20 frames (just to make sure, all these values are ballpark
            # values) to optimize.
            while frame and i < 20:
                if frame.f_code.co_filename == __file__:
                    # The first (in fact the last from call perspective) time we are
                    # in this file.
                    if line_number is None:
                        line_number = frame.f_lineno
                    # If we were in the same file and line already higher in the stack,
                    # we are in a recursive loop.
                    elif line_number == frame.f_lineno:
                        return True
                frame = frame.f_back
                i += 1
        finally:
            del frame

        return False

    def write(self, buffer: str) -> int:
        if self.closed:
            raise ValueError("Stream is closed.")

        if self._check_recursion():
            # We are being called by a logger in a recursive loop. Because this message has already been logged,
            # it is safe for us to just drop it to break a recursive loop.
            return 0

        for line in buffer.splitlines():
            if line.strip():
                self.logger.log(self.level, line.rstrip())

        return len(buffer)

    def writelines(self, lines: typing.List[str]) -> None:
        if self.closed:
            raise ValueError("Stream is closed.")

        if self._check_recursion():
            # We are being called by a logger in a recursive loop. Because this message has already been logged,
            # it is safe for us to just drop it to break a recursive loop.
            return

        for line in lines:
            if line.strip():
                self.logger.log(self.level, line.rstrip())

    def flush(self) -> None:
        pass

    def close(self) -> None:
        self.closed = True

    def seekable(self) -> bool:
        return False

    def seek(self, offset: int, whence: int = 0) -> int:
        raise OSError("Stream is not seekable.")

    def tell(self) -> int:
        raise OSError("Stream is not seekable.")

    def truncate(self, size: int = None) -> int:
        raise OSError("Stream is not seekable.")

    def writable(self) -> bool:
        return True

    def isatty(self) -> bool:
        return False

    def readable(self) -> bool:
        return False

    def read(self, n: int = -1) -> typing.AnyStr:
        raise OSError("Stream is write-only.")

    def readline(self, limit: int = -1) -> typing.AnyStr:
        raise OSError("Stream is write-only.")

    def readlines(self, hint: int = -1) -> typing.List[typing.AnyStr]:
        raise OSError("Stream is write-only.")

    def fileno(self) -> int:
        raise OSError("Stream does not use a file descriptor.")


class redirect_to_logging(contextlib.AbstractContextManager):
    """
    A Python context manager which redirects all writes to stdout and stderr
    to Python logging.

    Primitives should use logging to log messages, but maybe they are not doing
    that or there are other libraries they are using which are not doing that.
    One can then use this context manager to assure that (at least all Python)
    writes to stdout and stderr by primitives are redirected to logging::

        with redirect_to_logging(logger=PrimitiveClass.logger):
            primitive = PrimitiveClass(...)
            primitive.set_training_data(...)
            primitive.fit(...)
            primitive.produce(...)
    """

    def __init__(self, logger: logging.Logger = None, stdout_level: typing.Union[int, str] = 'INFO', stderr_level: typing.Union[int, str] = 'ERROR') -> None:
        if logger is None:
            self.logger = logging.getLogger('redirect')
        else:
            self.logger = logger

        self.stdout_level = logging._checkLevel(stdout_level)  # type: ignore
        self.stderr_level = logging._checkLevel(stderr_level)  # type: ignore

        # We use a list to make this context manager re-entrant.
        self._old_stdouts: typing.List[typing.TextIO] = []
        self._old_stderrs: typing.List[typing.TextIO] = []

    def __enter__(self) -> logging.Logger:
        self._old_stdouts.append(sys.stdout)
        sys.stdout = typing.cast(typing.TextIO, StreamToLogger(self.logger, self.stdout_level))
        self._old_stderrs.append(sys.stderr)
        sys.stderr = typing.cast(typing.TextIO, StreamToLogger(self.logger, self.stderr_level))
        return self.logger

    def __exit__(self, exc_type: typing.Optional[typing.Type[BaseException]],
                 exc_value: typing.Optional[BaseException],
                 traceback: typing.Optional[types.TracebackType]) -> typing.Optional[bool]:
        sys.stdout = self._old_stdouts.pop()
        sys.stderr = self._old_stderrs.pop()
        return None


class CallbackHandler(logging.Handler):
    """
    Calls a ``callback`` with logging records as they are without any conversion except for:

     * formatting the logging message and adding it to the record object
     * assuring ``asctime`` is set
     * converts exception ``exc_info`` into exception's name
     * making sure ``args`` are JSON-compatible or removing it
     * making sure there are no null values
    """

    def __init__(self, callback: typing.Callable) -> None:
        super().__init__(logging.DEBUG)

        self.callback = callback

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self.callback(self.prepare(record))
        except Exception:
            self.handleError(record)

    def prepare(self, record: logging.LogRecord) -> typing.Dict:
        self.format(record)

        # If "asctime" is not set, we do it ourselves.
        if not hasattr(record, 'asctime'):
            if self.formatter:
                fmt = self.formatter
            else:
                fmt = logging._defaultFormatter  # type: ignore
            record.asctime = fmt.formatTime(record, fmt.datefmt)

        output = copy.copy(record.__dict__)

        # Exceptions are not JSON compatible.
        if 'exc_info' in output:
            if output['exc_info']:
                if isinstance(output['exc_info'], BaseException):
                    output['exc_type'] = type_to_str(type(output['exc_info']))
                else:
                    output['exc_type'] = type_to_str(type(output['exc_info'][1]))
            del output['exc_info']

        if 'args' in output:
            try:
                output['args'] = to_json_structure(output['args'])
            except Exception:
                # We assume this means "args" is not JSON compatible.
                del output['args']

        # We iterate over a list so that we can change dict while iterating.
        for key, value in list(output.items()):
            if value is None:
                del output[key]

        return output


def get_full_name(value: typing.Any) -> str:
    return '{module}.{name}'.format(module=value.__module__, name=value.__name__)


def has_duplicates(data: typing.Sequence) -> bool:
    """
    Returns ``True`` if ``data`` has duplicate elements.

    It works both with hashable and not-hashable elements.
    """

    try:
        return len(set(data)) != len(data)
    except TypeError:
        n = len(data)
        for i in range(n):
            for j in range(i + 1, n):
                if data[i] == data[j]:
                    return True
        return False


@contextlib.contextmanager
def silence() -> typing.Generator:
    """
    Hides logging and stdout output.
    """

    with unittest.TestCase().assertLogs(level=logging.DEBUG):
        with redirect_to_logging():
            # Just to log something, otherwise "assertLogs" can fail.
            logging.getLogger().debug("Silence.")

            yield


@deprecate.arguments('source', message="argument ignored")
def columns_sum(inputs: typing.Any, *, source: typing.Any = None) -> typing.Any:
    """
    Computes sum per column.
    """

    # Importing here to prevent import cycle.
    from d3m import container

    if isinstance(inputs, container.DataFrame):  # type: ignore
        results = container.DataFrame(inputs.agg(['sum']).reset_index(drop=True), generate_metadata=True)  # type: ignore
        return results

    elif isinstance(inputs, container.ndarray) and len(inputs.shape) == 2:
        return numpy.sum(inputs, axis=0, keepdims=True)

    else:
        raise exceptions.InvalidArgumentTypeError("Unsupported container type to sum: {type}".format(
            type=type(inputs),
        ))


def list_files(base_directory: str) -> typing.Sequence[str]:
    files = []

    base_directory = base_directory.rstrip(os.path.sep)
    base_directory_prefix_length = len(base_directory) + 1
    for dirpath, dirnames, filenames in os.walk(base_directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)

            # We do not use "os.path.relpath" because it is to general
            # and it first try to construct absolute path which is slow.
            files.append(filepath[base_directory_prefix_length:])

    # We sort to have a canonical order.
    files = sorted(files)

    return files


def is_int(typ: type) -> bool:
    # We support more types than those listed in "d3m.types.simple_data_types".
    # "d3m_utils.is_subclass" is respecting Python numeric tower.
    return is_subclass(typ, typing.Union[int, numpy.integer, numbers.Integral])


def is_float(typ: type) -> bool:
    # We support more types than those listed in "d3m.types.simple_data_types".
    # "d3m_utils.is_subclass" is respecting Python numeric tower.
    return is_subclass(typ, typing.Union[float, numpy.float32, numpy.float64, decimal.Decimal, numbers.Real]) and not is_int(typ)


def is_numeric(typ: type) -> bool:
    return is_int(typ) or is_float(typ)


def compute_hash_id(obj: typing.Dict) -> str:
    obj = copy.copy(obj)

    if 'id' in obj:
        del obj['id']

    # We iterate over a list so that we can change dict while iterating.
    for key in list(obj.keys()):
        # Do not count any private field into hash.
        if key.startswith('_'):
            del obj[key]

    # We have to use "to_json_structure" first so that we normalize numbers.
    # We cannot do this just with a custom encoder because encoders are not
    # called for float values so we cannot handle them there.
    # See: https://bugs.python.org/issue36841
    to_hash_id = json.dumps(to_json_structure(obj, normalize_numbers=True), sort_keys=True)

    return str(uuid.uuid5(HASH_ID_NAMESPACE, to_hash_id))


def compute_digest(obj: typing.Dict) -> str:
    obj = copy.copy(obj)

    if 'digest' in obj:
        del obj['digest']

    # We iterate over a list so that we can change dict while iterating.
    for key in list(obj.keys()):
        # Do not count any private field into digest.
        if key.startswith('_'):
            del obj[key]

    # We have to use "to_json_structure" first so that we normalize numbers.
    # We cannot do this just with a custom encoder because encoders are not
    # called for float values so we cannot handle them there.
    # See: https://bugs.python.org/issue36841
    to_digest = json.dumps(to_json_structure(obj, normalize_numbers=True), sort_keys=True)

    return hashlib.sha256(to_digest.encode('utf8')).hexdigest()


def is_sequence(value: typing.Any) -> bool:
    return isinstance(value, typing.Sequence) and not isinstance(value, str)


def get_dict_path(input_dict: typing.Dict, path: typing.Sequence[typing.Any]) -> typing.Any:
    value: typing.Any = input_dict

    for segment in path:
        value = value.get(segment, None)

        if value is None:
            return None

    return value


def set_dict_path(input_dict: typing.Dict, path: typing.Sequence[typing.Any], value: typing.Any) -> None:
    if not path:
        raise exceptions.InvalidArgumentValueError("\"path\" has to be non-empty.")

    for segment in path[:-1]:
        if segment not in input_dict:
            input_dict[segment] = {}
        input_dict = input_dict[segment]

    input_dict[path[-1]] = value


def register_yaml_representers() -> None:
    def yaml_representer_numpy_float(dumper: yaml.Dumper, data: typing.Any) -> typing.Any:
        return dumper.represent_float(float(data))

    def yaml_representer_numpy_int(dumper: yaml.Dumper, data: typing.Any) -> typing.Any:
        return dumper.represent_int(int(data))

    representers = [
        {'type': numpy.float32, 'representer': yaml_representer_numpy_float},
        {'type': numpy.float64, 'representer': yaml_representer_numpy_float},
        {'type': numpy.int32, 'representer': yaml_representer_numpy_int},
        {'type': numpy.int64, 'representer': yaml_representer_numpy_int},
        {'type': numpy.integer, 'representer': yaml_representer_numpy_int},
    ]

    for representer in representers:
        yaml.Dumper.add_representer(representer['type'], representer['representer'])
        yaml.SafeDumper.add_representer(representer['type'], representer['representer'])


def matches_structural_type(source_structural_type: type, target_structural_type: typing.Union[str, type]) -> bool:
    if isinstance(target_structural_type, str):
        return type_to_str(source_structural_type) == target_structural_type
    else:
        return is_subclass(source_structural_type, target_structural_type)


# Register YAML representers.
register_yaml_representers()


class PMap(pyrsistent.PMap):
    """
    Extends `pyrsistent.PMap` to (by default) iterate over its items in sorted order.
    """

    def iterkeys(self, *, sort: bool = True, reverse: bool = False) -> typing.Iterable:
        for k, _ in self.iteritems(sort=sort, reverse=reverse):
            yield k

    def itervalues(self, *, sort: bool = True, reverse: bool = False) -> typing.Iterable:
        for _, v in self.iteritems(sort=sort, reverse=reverse):
            yield v

    def iteritems(self, *, sort: bool = True, reverse: bool = False) -> typing.Iterable:
        if sort:
            yield from sorted(super().iteritems(), key=operator.itemgetter(0), reverse=reverse)
        else:
            yield from super().iteritems()

    # In Python 3 this is also an iterable.
    def values(self, *, sort: bool = True, reverse: bool = False) -> typing.Iterable:
        return self.itervalues(sort=sort, reverse=reverse)

    # In Python 3 this is also an iterable.
    def keys(self, *, sort: bool = True, reverse: bool = False) -> typing.Iterable:
        return self.iterkeys(sort=sort, reverse=reverse)

    # In Python 3 this is also an iterable.
    def items(self, *, sort: bool = True, reverse: bool = False) -> typing.Iterable:
        return self.iteritems(sort=sort, reverse=reverse)

    def evolver(self) -> 'Evolver':
        return Evolver(self)

    def __reduce__(self) -> typing.Tuple[typing.Callable, typing.Tuple[typing.Dict]]:
        return pmap, (dict(self),)


class Evolver(pyrsistent.PMap._Evolver):
    def persistent(self) -> PMap:
        if self.is_dirty():
            self._original_pmap = PMap(self._size, self._buckets_evolver.persistent())

        return self._original_pmap


# It is OK to use a mutable default value here because it is never changed in-place.
def pmap(initial: typing.Mapping = {}, pre_size: int = 0) -> PMap:
    super_pmap = pyrsistent.pmap(initial, pre_size)

    return PMap(super_pmap._size, super_pmap._buckets)


EMPTY_PMAP = pmap()


def is_uri(uri: str) -> bool:
    """
    Test if a given string is an URI.

    Parameters
    ----------
    uri : str
        A potential URI to test.

    Returns
    -------
    bool
        ``True`` if string is an URI, ``False`` otherwise.
    """

    try:
        parsed_uri = url_parse.urlparse(uri, allow_fragments=False)
    except Exception:
        return False

    return parsed_uri.scheme != ''


def fix_uri(uri: str, *, allow_relative_path: bool = True) -> str:
    """
    Make a real file URI from a path.

    Parameters
    ----------
    uri : str
        An input URI.
    allow_relative_path : bool
        Allow path to be relative?

    Returns
    -------
    str
        A fixed URI.
    """

    if is_uri(uri):
        return uri

    if not uri.startswith('/') and not allow_relative_path:
        raise exceptions.InvalidArgumentValueError(f"Path cannot be relative: {uri}")

    # Make absolute and normalize at the same time.
    uri = os.path.abspath(uri)

    return 'file://{uri}'.format(uri=uri)


def outside_package_context() -> typing.Optional[deprecate.Context]:
    frame = sys._getframe(1)
    try:
        while frame:
            if os.path.commonpath([PACKAGE_BASE, frame.f_code.co_filename]) != PACKAGE_BASE:
                return deprecate.Context(None, None, frame.f_code.co_filename, frame.f_globals.get('__name__', None), frame.f_lineno)

            frame = frame.f_back

    finally:
        del frame

    return None


already_logged: typing.Set[typing.Tuple[deprecate.Context, deprecate.Context]] = set()


def log_once(logger: logging.Logger, level: int, msg: str, *args: typing.Any, **kwargs: typing.Any) -> None:
    frame = sys._getframe(1)
    try:
        if not frame:
            function_context = None
        else:
            function_context = deprecate.Context(str(level), msg, frame.f_code.co_filename, frame.f_globals.get('__name__', None), frame.f_lineno)
    finally:
        del frame

    module_context = outside_package_context()

    context = (module_context, function_context)

    if context in already_logged:
        return

    if module_context is not None and function_context is not None:
        already_logged.add(context)

    logger.log(level, msg, *args, **kwargs)


# A workaround to handle also binary stdin/stdout.
# See: https://gitlab.com/datadrivendiscovery/d3m/issues/353
# See: https://bugs.python.org/issue14156
class FileType(argparse.FileType):
    def __call__(self, string: str) -> typing.IO[typing.Any]:
        handle = super().__call__(string)

        if string == '-' and 'b' in self._mode:  # type: ignore
            handle = handle.buffer  # type: ignore

        return handle


def filter_local_location_uris(doc: typing.Dict) -> None:
    if 'location_uris' in doc:
        location_uris = []
        for location_uri in doc['location_uris']:
            try:
                parsed_uri = url_parse.urlparse(location_uri, allow_fragments=False)
            except Exception:
                continue

            if parsed_uri.scheme == 'file':
                continue

            location_uris.append(location_uri)

        if location_uris:
            doc['location_uris'] = location_uris
        else:
            del doc['location_uris']
