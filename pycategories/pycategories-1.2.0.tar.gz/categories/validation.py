from typing import Callable, Generic, Type, TypeVar, Union

from categories import applicative, functor, bifunctor, semigroup
from categories import sappend


A = TypeVar('A')
B = TypeVar('B')
E = TypeVar('E')
Vn = TypeVar('Vn', bound='Validation')


class Validation(Generic[E, A]):
    _SUCCESS_TYPE = 'Success'
    _FAILURE_TYPE = 'Failure'

    def __init__(self, type: str, value: Union[E, A]) -> None:
        self.type = type
        self.value = value

    def __repr__(self) -> str:
        return '{}({})'.format(self.type, repr(self.value))

    def __eq__(self, other) -> bool:
        if isinstance(other, type(self)):
            return (self.type == other.type and
                    self.__dict__ == other.__dict__)
        else:
            return False

    def match(self, constructor) -> bool:
        return constructor(self.value).type == self.type

    @classmethod
    def failure(cls: Type, value: E) -> Vn:
        return cls(cls._FAILURE_TYPE, value)

    @classmethod
    def success(cls: Type, value: E) -> Vn:
        return cls(cls._SUCCESS_TYPE, value)


Failure = Validation.failure  # type: Callable[[E], Validation[E, A]]
Success = Validation.success  # type: Callable[[E], Validation[E, A]]


def _sappend(a: Validation[E, A], b: Validation[E, A]) -> Validation[E, A]:
    if a.type == b.type:
        return Validation(a.type, sappend(a.value, b.value))
    elif a.match(Failure):
        return a
    else:
        return b


def _fmap(f: Callable[[A], B], x: Validation) -> Validation:
    if x.match(Failure):
        return x
    else:
        return Success(f(x.value))


def _first(f: Callable, x: Validation) -> Validation:
    if x.match(Failure):
        return Failure(f(x.value))
    else:
        return x


_second = _fmap


def _apply(f: Validation, x: Validation) -> Validation:
    if f.match(Success) and x.match(Success):
        return Success(f.value(x.value))
    elif f.match(Failure):
        return f
    else:
        return x


semigroup.instance(Validation, _sappend)
functor.instance(Validation, _fmap)
bifunctor.instance(Validation, _first, _second)
applicative.instance(Validation, Success, _apply)
