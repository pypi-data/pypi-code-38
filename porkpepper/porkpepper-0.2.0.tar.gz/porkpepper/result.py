from typing import *
from .error import UnwrapError


T = TypeVar('T')
E = TypeVar('E')


class Result(Generic[T]):
    def __init__(self, v: Any = None):
        self._v = v

    @property
    def is_ok(self):
        if self._v is None:
            return True
        if isinstance(self._v, type):
            object_type = self._v
        else:
            object_type = type(self._v)
        return not issubclass(object_type, Exception)

    @property
    def is_error(self) -> bool:
        if self._v is None:
            return False
        if isinstance(self._v, type):
            object_type = self._v
        else:
            object_type = type(self._v)
        return issubclass(object_type, Exception)

    @property
    def is_none(self) -> bool:
        return self._v is None

    @property
    def is_some(self) -> bool:
        return not self.is_none and not self.is_error

    def unwrap(self) -> T:
        if self.is_error:
            raise UnwrapError
        return self._v

    @property
    def error(self) -> Optional[Exception]:
        if self.is_error:
            return self._v
        return None

    @staticmethod
    def none() -> 'Result':
        return Result()

    def __repr__(self):
        if self.is_error:
            return "<Result({}): {}>".format(type(self._v).__name__, self._v)
        return "<Result: {}>".format(self._v)


__all__ = ["Result"]
