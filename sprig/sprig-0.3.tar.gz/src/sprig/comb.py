"""
A collection of utils for doing combinatorics.
"""
import collections
import functools
import itertools
import operator
from typing import Generator, Iterable, Tuple, Union


def comb(n, k):
    """Compute binomial coefficient n choose k"""
    if not 0 <= k <= n:
        return 0

    k = min(k, n - k)
    numerator = functools.reduce(operator.mul, range(n, n - k, -1), 1)
    denominator = functools.reduce(operator.mul, range(1, k + 1), 1)
    return numerator // denominator


class Combinations:
    """
    Create an object that represent a collection of combinations.

    Useful for slicing or sampling from series too long to iterate over with
    `itertools.combinations`.
    """

    def __init__(self, s: Iterable, k: int) -> None:
        """
        Return a sequence of all k-combinations from the collection s.
        The sequence is consistent with itertools.combinations but can be
        accessed randomly at near-constant time.
        """
        self._s = list(s)
        self._n = len(self._s)
        self._k = k
        self._len = int(comb(self._n, self._k))

    def __len__(self):
        return self._len

    def __str__(self):
        if self._len == 0:
            return "Combinations({n}, {k}) = ()".format(n=self._n, k=self._k)

        if self._len == 1:
            return "Combinations({n}, {k}) = ({first})".format(
                n=self._n, k=self._k, first=self[0]
            )

        if self._len == 2:
            return "Combinations({n}, {k}) = ({first}, {last})".format(
                n=self._n, k=self._k, first=self[0], last=self[-1]
            )

        return "Combinations({n}, {k}) = ({first}, ..., {last})".format(
            n=self._n, k=self._k, first=self[0], last=self[-1]
        )

    def __iter__(self):
        yield from itertools.combinations(self._s, self._k)

    def __getitem__(
            self,
            index: Union[int, slice],
    ) -> Union[Tuple, Iterable[Tuple]]:
        """
        Get the index'th combination in lexicographical order.

        >>> Combinations(range(5), 3)[0]
        (0, 1, 2)

        >>> Combinations(range(5), 3)[5]
        (0, 3, 4)

        >>> Combinations(range(5), 3)[0:6]
        [(0, 1, 2), (0, 1, 3), (0, 1, 4), (0, 2, 3), (0, 2, 4), (0, 3, 4)]
        """

        # If asked to return a slice, return a list of all indices included in slice
        if isinstance(index, slice):
            return [
                self[i]  # type: ignore
                for i in range(*index.indices(self._len))
            ]

        # Allow negative indexing from the end of the sequence
        if index < 0:
            index += self._len

        if not 0 <= index < self._len:
            raise IndexError(
                "Index {index} out of bounds for {self}. "
                "Must be in range [{start}, {end}].".format(
                    index=index,
                    self=self,
                    start=-self._len,
                    end=self._len - 1
                )
            )

        # Compute the combinadic of the complement of the index
        combinadic = self.gen_combinadic(self._len - 1 - index)

        # Convert the combinadic (descending order) to a combination (ascending order)
        return tuple(self._s[self._n - 1 - i] for i in combinadic)

    def __contains__(self, selection):
        # A selection is a k-combination of a collection iff it contains k
        # elements ...
        subset = collections.Counter(selection)
        if sum(subset.values()) != self._k:
            return False
        # ... and it is a subset of the collection.
        superset = collections.Counter(self._s)
        return all(subset[k] <= superset[k] for k in subset)

    def gen_combinadic(self, index: int) -> Generator[int, None, None]:
        """
        Compute the index'th combinadic.

        e.g. 4 = 4 choose 3 + 1 choose 2 + 0 choose 1, thus

        >>> tuple(Combinations(range(5), 3).gen_combinadic(4))
        (4, 1, 0)
        """

        n = self._n

        for k in range(self._k, 0, -1):
            n, nck = Combinations.max_n_choose_k_below_limit(n, k, index)
            index -= nck
            yield n

    # TODO: PyPy does not like `Dict[int, Dict[Tuple[int, int], int]`
    max_n_cache = collections.defaultdict(dict)  # type: ignore

    @staticmethod
    def max_n_choose_k_below_limit(
            n: int,
            k: int,
            limit: int,
    ) -> Tuple[int, int]:
        """
        Compute the largest n s.t. n choose k < limit.
        Return also the corresponding value of n choose k for optimization.

        e.g. 5 choose 3 = 10 > 5 but 4 choose 3 = 4 < 5, thus

        >>> Combinations.max_n_choose_k_below_limit(5, 3, 5)
        (4, 4)
        """

        for lower, upper in Combinations.max_n_cache[k]:
            if lower <= limit < upper:
                return Combinations.max_n_cache[k][(lower, upper)], lower

        lower = int(comb(n, k))
        if lower > limit:
            n, lower = Combinations.max_n_choose_k_below_limit(n - 1, k, limit)

        upper = int(comb(n + 1, k))

        Combinations.max_n_cache[k][(lower, upper)] = n
        return n, lower
