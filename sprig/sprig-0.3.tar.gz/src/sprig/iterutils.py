"""
Some utility functions for working with iterators.
"""
import heapq
# pylint does not recognize type hints in comments, and
# py35 does not support variable type hints any other way
# TODO: Figure out why `isort` and `yapf` can not agree on this import statement
from typing import Any, Callable, Iterable, Iterator, List, Tuple, TypeVar  # pylint: disable=W0611

T = TypeVar('T')


def imerge(
        iterables: Iterable[Iterable[T]],
        key: Callable[[T], Any] = lambda x: x,
) -> Iterable[T]:
    """Merge individually sorted iterables to a single sorted iterator.

    This is simlar to the merge step in merge-sort except
    * it handles an arbitrary number of iterators, and
    * eagerly consumes only one item from each iterator.

    If the laziness is not needed, it is probably better to concatenate and sort.

    **Sorted normally**

    >>> list(imerge([[1, 4], [2, 3]]))
    [1, 2, 3, 4]

    **Key changes order (Note that the sorted order of inputs is different)s**

    >>> list(imerge([[4, 1], [2, 3]], key=lambda x: (x%2, x)))
    [2, 4, 1, 3]
    """
    if not callable(key):
        raise TypeError("Key must be callable")

    heap = []  # type: List[Tuple[Any, int, T, Iterator[T]]]
    for i, iterable in enumerate(iterables):
        iterator = iter(iterable)
        try:
            v = next(iterator)
        except StopIteration:
            continue
        k = key(v)
        heapq.heappush(heap, (k, i, v, iterator))

    while heap:
        k, i, v, iterator = heapq.heappop(heap)
        yield v
        try:
            v = next(iterator)
        except StopIteration:
            continue

        k = key(v)
        heapq.heappush(heap, (k, i, v, iterator))
