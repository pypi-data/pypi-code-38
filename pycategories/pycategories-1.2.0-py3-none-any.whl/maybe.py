from typing import Any, Callable, Generic, Type, TypeVar

from categories import applicative, functor, mappend
from categories import monad, monoid
from categories import semigroup, sappend


A = TypeVar('A')
B = TypeVar('B')
M = TypeVar('M', bound='Maybe')


class Maybe(Generic[A]):
    _JUST_TYPE = 'Just'  # type: str
    _NOTHING_TYPE = 'Nothing'  # type: str

    def __init__(self, type: str, value: A = None) -> None:
        self.type = type
        if self.type == self._JUST_TYPE:
            self.value = value

    def __repr__(self) -> str:
        return ('Nothing' if self.type == self._NOTHING_TYPE else
                'Just({})'.format(repr(self.value)))

    def __eq__(self, other) -> bool:
        if isinstance(other, type(self)):
            return (self.type == other.type and
                    self.__dict__ == other.__dict__)
        else:
            return False

    def match(self, constructor) -> bool:
        if self.type == self._NOTHING_TYPE:
            return constructor == self.nothing
        else:
            return constructor == self.just

    @classmethod
    def just(cls: Type, value: A) -> M:
        return cls(cls._JUST_TYPE, value)

    @classmethod
    def nothing(cls: Type) -> M:
        return cls(cls._NOTHING_TYPE)


Just = Maybe.just  # type: Callable[[A], Maybe[A]]
Nothing = Maybe.nothing  # type: Callable[[], Maybe[A]]


def _mappend(a: Maybe[A], b: Maybe[A]) -> Maybe[A]:
    if a == Nothing():
        return b
    elif b == Nothing():
        return a
    else:
        return Just(mappend(a.value, b.value))


def _sappend(a: Maybe[A], b: Maybe[A]) -> Maybe[A]:
    if a.match(Nothing):
        return b
    elif b.match(Nothing):
        return a
    else:
        return Just(sappend(a.value, b.value))


def _fmap(f: Callable, x: Maybe[A])-> Maybe[B]:
    return Just(f(x.value)) if x.match(Just) else Nothing()


def _apply(f, x: Maybe[A]) -> Maybe[B]:
    if f.match(Just) and x.match(Just):
        return Just(f.value(x.value))
    else:
        return Nothing()


def _bind(m: Maybe[A], f: Callable[[Any], Maybe[B]]) -> Maybe[B]:
    if m.match(Nothing):
        return Nothing()
    else:
        return f(m.value)


functor.instance(Maybe, _fmap)
semigroup.instance(Maybe, _sappend)
monoid.instance(Maybe, lambda: Nothing(), _mappend)
applicative.instance(Maybe, Just, _apply)
monad.instance(Maybe, Just, _bind)


def maybe(default: B, f: Callable, x: Maybe[A]) -> B:
    """
    Given a default value, a function, and a Maybe object, return the default
    if the Maybe object is Nothing, otherwise call the function with the value
    in the Maybe object, call the function on it, and return the result.

    :param default: This is the value that gets returned if ``x`` is Nothing
    :param f: When x matches Just, this function is called on the value in x,
        and the result is returned
    :param x: a Maybe object
    :returns: Whatever type ``default`` or the return type of ``f`` is
    """
    if x.match(Just):
        return f(x.value)
    else:
        return default
