from typing import Iterable, TypeVar, Callable, Any, overload

T = TypeVar('T')


@overload
def afiv_max_t(iterable: Iterable[T], key: Callable[[T], Any], default: T) -> T:
    return default


def afiv_max_t(iterable: Iterable[T], key: Callable[[T], Any], default: T) -> T:
    return default
