from pyrediseasyio.abstract_reader_writer import AbstractReaderWriter
from dominate.tags import div, span, tr, td
import threading
import json

lock = threading.Lock()


class SingleIO:
    def __init__(self, name: str, addr: str = None, default: object = None,
                 units: str = None, reader: AbstractReaderWriter = None):
        self.name = name
        self.addr = addr
        self._reader_writer = reader
        self.default = default
        self.units = units

    def __and__(self, other):
        if hasattr(other, 'value'):
            return self.value and other.value
        return self.value and other

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

    def __eq__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value == other

    def __floordiv__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value // other

    def __iadd__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        val = self.value
        val += other
        self.write(val)

    def __idiv__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        val = self.value
        val /= other
        self.write(val)

    def __ifloordiv__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        val = self.value
        val //= other
        self.write(val)

    def __imul__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        val = self.value
        val *= other
        self.write(val)

    def __invert__(self):
        return ~self.value

    def __ipow__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        val = self.value
        val **= other
        self.write(val)

    def __isub__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        val = self.value
        val -= other
        self.write(val)

    def __ne__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value != other

    def __or__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value or other

    def __pos__(self):
        return self.value

    def __pow__(self, power, modulo=None):
        if hasattr(power, 'value'):
            power = power.value
        return self.value ** power

    def __neg__(self):
        return -self.value

    def __set__(self, obj, value):
        self.write(value)

    def __str__(self):
        return f'[{type(self).__name__}] {self.name} = {self.value} {self.units}'

    def __truediv__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value / other

    @property
    def value(self):
        return self.read()

    @staticmethod
    def _convert_type(value):
        return value

    def publish(self, value, channel: str = None, and_write: bool = False):
        value = self._convert_type(value)
        data = json.dumps({self.addr: value})
        self._reader_writer.publish(data, channel)
        if and_write:
            self.write(value)

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

