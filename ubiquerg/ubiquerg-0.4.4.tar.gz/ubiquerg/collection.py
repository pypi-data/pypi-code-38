""" Tools for working with collections """

import itertools
import sys
if sys.version_info < (3, 3):
    from collections import Iterable
else:
    from collections.abc import Iterable

__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"


__all__ = ["is_collection_like", "powerset"]


def is_collection_like(c):
    """
    Determine whether an object is collection-like.

    :param object c: Object to test as collection
    :return bool: Whether the argument is a (non-string) collection
    """
    return isinstance(c, Iterable) and not isinstance(c, str)


def powerset(items, min_items=None, include_full_pop=True, nonempty=False):
    """
    Build the powerset of a collection of items.

    :param Iterable[object] items: "Pool" of all items, the population for
        which to build the power set.
    :param int min_items: Minimum number of individuals from the population
        to allow in any given subset.
    :param bool include_full_pop: Whether to include the full population in
        the powerset (default True to accord with genuine definition)
    :param bool nonempty: force each subset returned to be nonempty
    :return list[object]: Sequence of subsets of the population, in
        nondecreasing size order
    :raise TypeError: if minimum item count is specified but is not an integer
    :raise ValueError: if minimum item count is insufficient to guarantee
        nonempty subsets
    """
    if min_items is None:
        min_items = 1 if nonempty else 0
    else:
        if not isinstance(min_items, int):
            raise TypeError("Min items count for each subset isn't an integer: "
                            "{} ({})".format(min_items, type(min_items)))
        if nonempty and min_items < 1:
            raise ValueError("When minimum item count is {}, nonempty subsets "
                             "cannot be guaranteed.".format(min_items))
    # Account for iterable burn possibility; besides, collection should be
    # relatively small if building the powerset.
    items = list(items)
    n = len(items)
    if n == 0 or n < min_items:
        return []
    max_items = len(items) + 1 if include_full_pop else len(items)
    return list(itertools.chain.from_iterable(
            itertools.combinations(items, k)
            for k in range(min_items, max_items)))
