from controlpyweb.abstract_reader_writer import AbstractReaderWriter
import threading
from controlpyweb.errors import ControlPyWebReadOnlyError
from str2bool import str2bool

lock = threading.Lock()


class SingleIO:
    def __init__(self, name: str, addr: str, default: object,
                 reader: AbstractReaderWriter = None, *args, **kwargs):
        self.units = kwargs.get("units") if kwargs is not None else ""
        self.name = name
        self.addr = addr
        self._reader_writer = reader
        self._default = default

    def __and__(self, other):
        if hasattr(other, 'value'):
            return self.value and other.value
        return self.value and other

    def __eq__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value == other

    def __ne__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value != other

    def __gt__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value > other

    def __lt__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value < other

    def __ge__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value >= other

    def __le__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value <= other

    def __get__(self, instance, owner):
        self.read()
        return self

    def __set__(self, obj, value):
        raise ControlPyWebReadOnlyError

    def __str__(self):
        return f'[{type(self).__name__}] {self.name} = {self.value}'

    def __add__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value + other

    def __sub__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value - other

    def __mul__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value * other

    def __truediv__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value / other

    def __floordiv__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value // other

    @property
    def value(self):
        val = self.read()
        if val is None:
            return self._default
        return self._convert_type(val)

    @staticmethod
    def _convert_type(value):
        return value

    def read(self):
        with lock:
            if self._reader_writer is None:
                return None
            val = self._reader_writer.read(self.addr)
            val = self._convert_type(val)
            return val

    def read_immediate(self):
        with lock:
            val = self._reader_writer.read_immediate(self.addr)
            return val


class DiscreteIn(SingleIO):
    def __init__(self, name: str, addr: str, default: bool = False,
                 reader: AbstractReaderWriter = None, *args, **kwargs):
        super().__init__(name, addr, default, reader, *args, **kwargs)

    @staticmethod
    def _convert_type(value):
        if isinstance(value, str):
            return str2bool(value)
        return bool(value)

    def __bool__(self):
        return bool(self.value)


class IOOut(DiscreteIn):
    def __init__(self, name: str, addr: str, default,
                 reader: AbstractReaderWriter = None, *args, **kwargs):
        super().__init__(name, addr, default, reader, *args, **kwargs)
        self.ignore_duplicate_writes = kwargs.get('ignore_duplicate_writes', True) if kwargs is not None else True

    def __set__(self, instance, value):
        if isinstance(value, SingleIO):
            value = value.value
        self.write(value)

    def write(self, value):
        if self.ignore_duplicate_writes and value == self.value:
            return
        self._reader_writer.write(self.addr, self._convert_type(value))

    def write_immediate(self, value):
        self._reader_writer.write_immediate(self.addr, self._convert_type(value))


class DiscreteOut(IOOut, DiscreteIn):
    def __init__(self, name: str, addr: str, default: bool = False,
                 reader: AbstractReaderWriter = None, *args, **kwargs):
        super().__init__(name, addr, default, reader, *args, **kwargs)


class AnalogIn(SingleIO):
    def __init__(self, name: str, addr: str, default: float = 0.0,
                 reader: AbstractReaderWriter = None, *args, **kwargs):
        super().__init__(name, addr, default, reader, *args, **kwargs)

    @staticmethod
    def _convert_type(value):
        return float(value)


class AnalogOut(IOOut, AnalogIn):
    def __init__(self, name: str, addr: str, default: float = 0.0,
                 reader: AbstractReaderWriter = None, *args, **kwargs):
        super().__init__(name, addr, default, reader, *args, **kwargs)

    @staticmethod
    def _convert_type(value):
        return float(value)



