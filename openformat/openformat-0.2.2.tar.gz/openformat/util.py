import logging
import re
import struct
import numpy as np

LOGGER = logging.getLogger(__name__)
CTYPES_FORMAT_LOOKUP = {
    'int': 'i',
    'uint': 'I',
    'short': 'h',
    'ushort': 'H',
    'char': 's',
    'WORD': 'h',
    'double': 'd',
    'str': 's',
}
ARRAY_PATTERN = re.compile(r'(\w+)\[(\d+(?:,\s*\d+)*)\]')
STRUCT_PATTERN = re.compile(r'(\d+)?(\w+)')
STR_PATTERN = re.compile(r'\d+str')


def _load_array(match, buffer, byte_order):
    """
    Load a numpy array.
    """
    dtype, shape = match.groups()
    dtype = np.dtype(CTYPES_FORMAT_LOOKUP.get(dtype, dtype))
    if byte_order in '><':
        dtype = dtype.newbyteorder(byte_order)
    shape = [int(part.strip()) for part in shape.split(',')]
    size = int(np.prod(shape) * dtype.itemsize)
    return np.frombuffer(buffer.read(size), dtype).reshape(shape)


def _load_struct(match, buffer, byte_order):
    """
    Load structured binary data after type substitution.
    """
    num, dtype = match.groups()
    dtype = CTYPES_FORMAT_LOOKUP.get(dtype, dtype)
    fmt = f"{byte_order}{num or ''}{dtype}"
    size = struct.calcsize(fmt)
    values = struct.unpack(fmt, buffer.read(size))
    return values if len(values) > 1 else values[0]


PATTERNS = [
    (STRUCT_PATTERN, _load_struct),
    (ARRAY_PATTERN, _load_array),
]


def from_buffer(type_, buffer, byte_order=None):
    """
    Load data with `type_` from `buffer` using a given `byte_order`.
    """
    byte_order = byte_order or '@'

    if isinstance(type_, type) and issubclass(type_, Structure):
        return type_.from_buffer(buffer, byte_order)

    if isinstance(type_, tuple):
        type_, size = type_
        return [from_buffer(type_, buffer, byte_order) for _ in range(size)]

    if isinstance(type_, str):
        for pattern, loader in PATTERNS:
            match = pattern.fullmatch(type_)
            if match:
                return loader(match, buffer, byte_order)

    assert callable(type_), "`type_` is not a recognised format string or callable"
    return type_(buffer, byte_order)


class Structure(dict):
    """
    Abstract base class for structures.
    """
    __fields__ = None
    __size__ = None

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:  # pragma: no cover
            raise AttributeError(key)

    def __repr__(self):
        return "{name}({fields})".format(
            name=str(self.__class__),
            fields=", ".join([f"{key}={value}" for key, value in self.items()])
        )

    @classmethod
    def from_buffer(cls, buffer, byte_order=None):
        """
        Create an instance of `cls` from `buffer` using the specified `byte_order`.
        """
        offset = buffer.tell()
        assert cls.__fields__ is not None, "`__fields__` must not be `None`"
        byte_order = byte_order or '@'
        instance = cls()
        for name, type_ in cls.__fields__:  # pylint: disable=E1133
            instance[name] = from_buffer(type_, buffer, byte_order)
        delta = buffer.tell() - offset
        assert cls.__size__ is None or delta == cls.__size__, \
            f"{cls} consumed {delta} bytes (expected {cls.__size__}); pointer at {buffer.tell()}"
        LOGGER.info(f'{cls} consumed {delta} bytes; pointer at {buffer.tell()}')
        instance.validate()
        return instance

    def validate(self):
        """
        Validate the structure.
        """
        for name, type_ in self.__fields__:
            if isinstance(type_, str) and STR_PATTERN.fullmatch(type_):
                try:
                    self[name] = self[name].partition(b'\x00')[0].decode()
                except UnicodeDecodeError:  # pragma: no cover
                    LOGGER.debug(f"could not decode attribute {name} of {self.__class__}: {self[name]}")
