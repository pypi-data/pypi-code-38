from .consts import (
    ERROR_TYPE,
    EXCEPTION_TYPE,
    FUNC_TYPE,
    IGNORE_TYPE,
    LIB_METHODS,
)
from .decorators import functional

HANDLED_TYPES = [ERROR_TYPE, EXCEPTION_TYPE, FUNC_TYPE, IGNORE_TYPE]


class MacaroniMeta(type):
    def __new__(cls, name, bases, attrs):
        new_attrs = {}
        for attr_name, attr in attrs.items():
            if not callable(attr):
                new_attrs[attr_name] = attr
                continue

            if attr_name.startswith("_"):
                new_attrs[attr_name] = attr
                continue
            if attr_name in LIB_METHODS:
                new_attrs[attr_name] = attr
                continue
            if hasattr(attr, "_type"):
                if attr._type in HANDLED_TYPES:
                    new_attrs[attr_name] = attr
                    continue

            new_attrs[attr_name] = functional(attr)

        return super().__new__(cls, name, bases, new_attrs)


class Macaroni(metaclass=MacaroniMeta):
    def __init__(self, data=None, magic=True):
        self._exc_traceback = None
        self._magic = magic
        self.error = None
        self.exception = None
        self.data = data

    def unwrap(self):
        if self.exception:
            raise self.exception
        if self.error:
            return self.error

        return self.data
