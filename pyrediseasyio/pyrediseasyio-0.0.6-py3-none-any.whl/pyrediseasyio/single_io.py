from pyrediseasyio.abstract_reader_writer import AbstractReaderWriter
import threading
from str2bool import str2bool

lock = threading.Lock()


class SingleIO:
    def __init__(self, name: str, addr: str, default: object, reader: AbstractReaderWriter = None):
        self.name = name
        self.addr = addr
        self._reader_writer = reader
        self.default = default

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

    def __eq__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value == other

    def __ne__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value != other

    def __get__(self, instance, owner):
        self.read()
        return self

    def __set__(self, obj, value):
        self.write(value)

    def __str__(self):
        return f'[{type(self).__name__}] {self.name} = {self.value}'

    @property
    def value(self):
        return self.read()

    @staticmethod
    def _convert_type(value):
        return value

    def read(self):
        if self._reader_writer is None:
            return None
        with lock:
            val = self._reader_writer.read(self.addr)
            if val is None:
                val = self.default
            val = self._convert_type(val)
            return val

    def write(self, value):
        if self._reader_writer is None:
            return
        with lock:
            value = self._convert_type(value)
            self._reader_writer.write(self.addr, value)


class BooleanIO(SingleIO):
    def __init__(self, name: str, addr: str, default: bool = False, reader: AbstractReaderWriter = None):
        super().__init__(name, addr, default, reader)

    @staticmethod
    def _convert_type(value):
        if isinstance(value, str):
            return str2bool(value)
        return bool(value)

    def __bool__(self):
        return self.value
    
    @property
    def value(self) -> bool:
        return super().value


class IntIO(SingleIO):
    def __init__(self, name: str, addr: str, default: int = 0, reader: AbstractReaderWriter = None):
        super().__init__(name, addr, default, reader)

    @staticmethod
    def _convert_type(value):
        return int(value)


class FloatIO(SingleIO):
    def __init__(self, name: str, addr: str, default: float = 0, reader: AbstractReaderWriter = None):
        super().__init__(name, addr, default, reader)

    @staticmethod
    def _convert_type(value):
        return float(value)


class StringIO(SingleIO):
    def __init__(self, name: str, addr: str, default: str = '', reader: AbstractReaderWriter = None):
        super().__init__(name, addr, default, reader)

    @staticmethod
    def _convert_type(value):
        return str(value)


