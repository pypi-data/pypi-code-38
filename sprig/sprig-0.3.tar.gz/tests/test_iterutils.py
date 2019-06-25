from typing import Any, Callable, Iterable, List, TypeVar

from sprig import iterutils

T = TypeVar('T')


def _merge(iterables, key=lambda x: x):
    """Convenience wrapper around `imerge` that exhausts the iterator and returns a
    list.
    """
    return list(iterutils.imerge(iterables, key))


def test_imerge_handles_empty_input():
    assert _merge([]) == []


def test_imerge_handles_empty_iterator():
    assert _merge([[], [1, 2]]) == [1, 2]


def test_imerge_handles_shallow_iterators():
    assert _merge([[1], [4], [2], [3]]) == [1, 2, 3, 4]


def test_imerge_handles_ties_of_uncomparable_items():
    actual = _merge([[{0: 2}, {0: 4}], [{0: 2}, {0: 3}]], key=lambda x: x[0])
    expected = [{0: 2}, {0: 2}, {0: 3}, {0: 4}]
    assert actual == expected


def test_imerge_is_not_eager():
    # 3 allows the implementation 1 item look ahead and the test to consume 1 item to
    # trigger generator setup
    a = iter(range(3))
    b = iter(range(3))

    next(iterutils.imerge([a, b]))

    # One list will be shorter than the other but neither will have been exhausted
    assert list(a)
    assert list(b)
