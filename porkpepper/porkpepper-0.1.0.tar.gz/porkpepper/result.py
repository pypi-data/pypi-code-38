from typing import *


T = TypeVar('T')
E = TypeVar('E')


class Result(Generic[T]):
    def __init__(self, v: Any = None):
        self._v = v

    @property
    def is_ok(self):
        return not isinstance(self._v, Exception)

    @property
    def is_error(self) -> bool:
        return isinstance(self._v, Exception)

    @property
    def is_none(self) -> bool:
        return self._v is None

    @property
    def is_some(self) -> bool:
        return not self.is_none and not self.is_error

    def unwrap(self) -> T:
        if self.is_error:
            raise ReferenceError
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
