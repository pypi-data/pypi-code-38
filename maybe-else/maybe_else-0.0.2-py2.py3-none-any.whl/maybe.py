from __future__ import annotations

import functools
from typing import Any, Callable, Type, cast, NoReturn, TypeVar

FuncSig = TypeVar("FuncSig", bound=Callable)


def _set_value_ignoring_exceptions(exception_type: Type[Exception] = Exception) -> Callable[[FuncSig], FuncSig]:
    def decorator(func: FuncSig) -> FuncSig:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            instance = args[0]

            try:
                instance._value_ = func(*args, **kwargs)
            except exception_type:
                instance._value_ = MissingValue
            finally:
                return instance

        return cast(FuncSig, wrapper)
    return decorator


class MissingValueMeta(type):
    def __repr__(cls) -> str:
        return cls.__name__

    def __call__(cls) -> NoReturn:  # type: ignore
        raise TypeError(f"Class {cls.__name__} is not callable.")


class MissingValue(metaclass=MissingValueMeta):
    pass


class Maybe:
    def __init__(self, val: Any) -> None:
        self._value_ = val if val is not None else MissingValue

    def __repr__(self) -> str:
        return f"{type(self).__name__}({repr(self._value_)})"

    def __bool__(self) -> bool:
        return self._value_ is not MissingValue

    def __getattr__(self, name: str) -> Maybe:
        try:
            self._value_ = getattr(self._value_, name)
        except AttributeError:
            if not (name.startswith("_") and "ipython" in name.lower()):
                self._value_ = MissingValue
        finally:
            return self

    @_set_value_ignoring_exceptions(KeyError)
    def __getitem__(self, key: str) -> Maybe:
        return self._value_[key]

    @_set_value_ignoring_exceptions(TypeError)
    def __call__(self, *args: Any, **kwargs: Any) -> Maybe:
        return self._value_(*args, **kwargs)

    @_set_value_ignoring_exceptions(TypeError)
    def __add__(self, other: Any) -> Maybe:
        return self._value_ + other

    @_set_value_ignoring_exceptions(TypeError)
    def __radd__(self, other: Any) -> Maybe:
        return other + self._value_

    @_set_value_ignoring_exceptions(TypeError)
    def __sub__(self, other: Any) -> Maybe:
        return self._value_ - other

    @_set_value_ignoring_exceptions(TypeError)
    def __rsub__(self, other: Any) -> Maybe:
        return other - self._value_

    @_set_value_ignoring_exceptions(TypeError)
    def __mul__(self, other: Any) -> Maybe:
        return self._value_ * other

    @_set_value_ignoring_exceptions(TypeError)
    def __rmul__(self, other: Any) -> Maybe:
        return other * self._value_

    @_set_value_ignoring_exceptions(TypeError)
    def __truediv__(self, other: Any) -> Maybe:
        return self._value_ / other

    @_set_value_ignoring_exceptions(TypeError)
    def __rtruediv__(self, other: Any) -> Maybe:
        return other / self._value_

    @_set_value_ignoring_exceptions(TypeError)
    def __floordiv__(self, other: Any) -> Maybe:
        return self._value_ // other

    @_set_value_ignoring_exceptions(TypeError)
    def __rfloordiv__(self, other: Any) -> Maybe:
        return other // self._value_

    @_set_value_ignoring_exceptions(TypeError)
    def __mod__(self, other: Any) -> Maybe:
        return self._value_ % other

    @_set_value_ignoring_exceptions(TypeError)
    def __rmod__(self, other: Any) -> Maybe:
        return other % self._value_

    @_set_value_ignoring_exceptions(TypeError)
    def __and__(self, other: Any) -> Maybe:
        return self._value_ & other

    @_set_value_ignoring_exceptions(TypeError)
    def __rand__(self, other: Any) -> Maybe:
        return other & self._value_

    @_set_value_ignoring_exceptions(TypeError)
    def __or__(self, other: Any) -> Maybe:
        return self._value_ | other

    @_set_value_ignoring_exceptions(TypeError)
    def __ror__(self, other: Any) -> Maybe:
        return other | self._value_

    def else_(self, alternative: Any) -> Any:
        return self._value_ if self._value_ is not MissingValue else alternative
