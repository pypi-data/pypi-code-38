import unittest
from .randsearcher import RandSearcher
from .searcher import Searcher

class TestRandSearcher(unittest.TestCase):
    def setUp(self):
        self.params = {
            "a": [2, 4, 6],
            "b": [11, 22, 33]
        }

    def test_iterates_correctly(self):
        srch: Searcher = RandSearcher(self.params)

        srch.__iter__()

        for candidates in srch:
            self.assertTrue("a" in candidates.keys())
            self.assertTrue("b" in candidates.keys())

    def test_iterates_exhaustively(self):
        srch: Searcher = RandSearcher(self.params)

        seen_vals = {}

        for _ in range(60):
            results = next(srch)
            self.assertGreaterEqual(6, results["a"])
            self.assertGreaterEqual(33, results["b"])
            self.assertLessEqual(2, results["a"])
            self.assertLessEqual(11, results["b"])
            seen_vals[hash(frozenset(results.items()))] = True
        
        self.assertEqual(9, len(seen_vals))

        self.assertRaises(StopIteration, srch.__next__)

    def test_works_with_small_params(self):
        params = {
            "a": [2.3],
            "b": [11.0]
        }
        
        srch: Searcher = RandSearcher(params)

        first_candidates = next(srch)

        self.assertDictEqual({
            "a": 2.3,
            "b": 11.0
        }, first_candidates)

        second_candidates = next(srch)

        self.assertDictEqual({
            "a": 2.3,
            "b": 11.0
        }, second_candidates)


    def test_works_with_lots_of_params(self):
        self.params["c"] = [100, 101, 102, 103, 105, 109, 110]
        self.params["d"] = [100.1, 101.2, 102.3, 103.4]
        srch: Searcher = RandSearcher(self.params)

        count = 0
        for _ in srch:
            count += 1
        
        self.assertEqual(60, count)
