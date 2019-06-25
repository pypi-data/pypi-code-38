from typing import Callable, Generic, Type, TypeVar, Union

from categories import applicative, functor, bifunctor, monad


A = TypeVar('A')
B = TypeVar('B')
E = TypeVar('E')
Etr = TypeVar('Etr', bound='Either')


class Either(Generic[E, A]):
    _RIGHT_TYPE = 'Right'  # type: str
    _LEFT_TYPE = 'Left'  # type: str

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
    def left(cls: Type, value: E) -> Etr:
        return cls(cls._LEFT_TYPE, value)

    @classmethod
    def right(cls: Type, value: A) -> Etr:
        return cls(cls._RIGHT_TYPE, value)


Left = Either.left  # type: Callable[[E], Either[E, A]]
Right = Either.right  # type: Callable[[A], Either[E, A]]


def _fmap(f: Callable[[A], B], x: Either) -> Either[E, B]:
    if x.match(Right):
        return Right(f(x.value))
    else:
        return x


def _first(f: Callable[[E], B], x: Either) -> Either[B, A]:
    if x.match(Left):
        return Left(f(x.value))
    else:
        return x


_second = _fmap


def _apply(f: Either, x: Either):
    if f.match(Right) and x.match(Right):
        return Right(f.value(x.value))
    elif f.match(Left):
        return f
    elif x.match(Left):
        return x


def _bind(m: Either[E, A], f: Callable) -> Either:
    """
    (>>=) :: Monad m => m a -> (a -> m b) -> m b
    """
    if m.match(Right):
        return f(m.value)
    else:
        return m


functor.instance(Either, _fmap)
bifunctor.instance(Either, _first, _second)
applicative.instance(Either, Right, _apply)
monad.instance(Either, Right, _bind)


def either(f: Callable, g: Callable, x: Either) -> Either:
    """
    Given two functions and an Either object, call the first function on the
    value in the Either if it's a Left value, otherwise call the second
    function on the value in the Either. Return the result of the function
    that's called.

    :param f: a function that accepts the type packed in ``x``
    :param g: a function that accepts the type packed in ``x``
    :param x: an Either object
    :returns: Whatever the functions ``f`` or ``g`` return
    """
    if x.match(Left):
        return f(x.value)
    else:
        return g(x.value)
