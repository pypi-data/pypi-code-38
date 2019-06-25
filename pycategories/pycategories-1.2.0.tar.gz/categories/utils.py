from typing import Any, Callable, TypeVar

from functools import reduce
from infix import make_infix


A = TypeVar('A')
B = TypeVar('B')


def funcall(f: Callable, *args) -> Any:
    return f(*args)


def id_(x: Any) -> Any:
    """The identity function.  Returns whatever argument it's called with."""
    return x


"""
unit is an old name for id_ from v1.1.0 and earlier
and it will be removed in a future version:
"""
unit = id_


def flip(f: Callable[[A, B], Any]) -> Callable[[B, A], Any]:
    """
    Return a function that reverses the arguments it's called with.

    :param f: A function that takes exactly two arguments
    :Example:

       >>> exp = lambda x, y: x ** y
       >>> flip_exp = flip(exp)
       >>> exp(2, 3)
       8
       >>> flip_exp(2, 3)
       9
    """
    return lambda x, y: f(y, x)


@make_infix('or')
def compose(*fs) -> Callable:
    """
    Return a function that is the composition of the functions in ``fs``.
    All functions in ``fs`` must take a single argument.

    Adapted from this StackOverflow answer:
    https://stackoverflow.com/a/34713317

    :Example:

       >>> compose(f, g)(x) == f(g(x))
    """
    return lambda x: reduce(flip(funcall), reversed(fs), x)


cp = compose
