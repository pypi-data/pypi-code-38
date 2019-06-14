from unittest import TestCase
from functools import reduce
from operator import mul

from ..get_kth_combination import get_kth_combination


class GetKthCombinationTestCase(TestCase):

    def test_get_kth_combination(self):
        iterables = [[1, 2, 3], ['A', 'B', 'C'], ['I', 'II']]
        expected_outputs = [
            [1, 'A', 'I'],
            [2, 'A', 'I'],
            [3, 'A', 'I'],
            [1, 'B', 'I'],
            [2, 'B', 'I'],
            [3, 'B', 'I'],
            [1, 'C', 'I'],
            [2, 'C', 'I'],
            [3, 'C', 'I'],
            [1, 'A', 'II'],
            [2, 'A', 'II'],
            [3, 'A', 'II'],
            [1, 'B', 'II'],
            [2, 'B', 'II'],
            [3, 'B', 'II'],
            [1, 'C', 'II'],
            [2, 'C', 'II'],
            [3, 'C', 'II'],
        ]

        for i, expected_output in enumerate(expected_outputs):
            with self.subTest(k=i):
                output = get_kth_combination(iterables, i)
                self.assertEqual(expected_output, output)

        # no duplicated output when k <= n_combinations
        n_combinations = reduce(mul, [len(e) for e in iterables])
        self.assertEqual(
            len(
                set(
                    [
                        str(get_kth_combination(iterables, k))
                        for k in range(n_combinations)
                    ],
                ),
            ),
            n_combinations,
        )
