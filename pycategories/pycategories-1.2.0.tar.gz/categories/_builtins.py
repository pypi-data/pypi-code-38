"""
Define instances for some Python built-in types like list and str
"""
from typing import Callable, List, TypeVar

from functools import reduce

from categories import applicative, functor, mappend, mempty
from categories import monad, monoid
from categories import semigroup, sappend


A = TypeVar('A')
B = TypeVar('B')


def _list_apply(f: List[Callable[[A], B]], x: List[A]) -> List[B]:
    return [g(i) for g in f for i in x]


# Instances for list:
semigroup.instance(list, lambda x, y: x + y)
monoid.instance(list, lambda: [], lambda x, y: x + y)
functor.instance(list, lambda f, xs: list(map(f, xs)))
applicative.instance(list, lambda x: [x], _list_apply)
monad.instance(list,
               lambda x: [x],
               lambda xs, f: reduce(lambda a, b: a + b, list(map(f, xs))))


# Instances for str:
semigroup.instance(str, lambda x, y: x + y)
monoid.instance(str, lambda: '', lambda x, y: x + y)
functor.instance(str, lambda f, xs: ''.join(map(f, xs)))


def _tuple_mappend(x, y):
    """Elements in x and y must have Monoid instances defined"""
    if x == ():
        return y
    elif y == ():
        return x
    elif len(x) != len(y):
        raise TypeError("tuples passed to mappend must have the same length")
    return tuple(map(lambda a: mappend(*a), zip(x, y)))


def _tuple_sappend(x, y):
    """Elements in x and y must have Semigroup instances defined"""
    if x == ():
        return y
    elif y == ():
        return x
    elif len(x) != len(y):
        raise TypeError("tuples passed to sappend must have the same length")
    return tuple(map(lambda a: sappend(*a), zip(x, y)))


"""
This copies the Haskell instances of Functor, Applicative, and Monad for
tuples, which only applies to 2-tuples.  If desired, someone can define
their own instances of Functor and Applicative that operate on n-tuples and
it will override these instances.
"""


def _check_tuple_length(xs):
    if len(xs) != 2:
        raise TypeError("Functor instance is only defined for 2-tuples")


def _tuple_fmap(f, xs):
    _check_tuple_length(xs)
    return (xs[0], f(xs[1]))


def _tuple_pure(x, type_form):
    return (mempty(type_form), x)


def _tuple_apply(fs, xs):
    _check_tuple_length(xs)
    return (mappend(fs[0], xs[0]), fs[1](xs[1]))


def _tuple_bind(x, m):
    _check_tuple_length(x)
    val = m(x[1])
    return (mappend(x[0], val[0]), val[1])


# Instances for tuple:
semigroup.instance(tuple, _tuple_sappend)
monoid.instance(tuple, lambda: (), _tuple_mappend)
functor.instance(tuple, _tuple_fmap)
applicative.instance(tuple, _tuple_pure, _tuple_apply)
monad.instance(tuple, _tuple_pure, _tuple_bind)
