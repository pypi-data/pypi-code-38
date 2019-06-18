import unittest
from typing import Type
from .randgridsearcher import RandGridSearcher
from .searcher import Searcher

class TestRandGridSearcher(unittest.TestCase):
    def setUp(self):
        self.params = {
            "a": [2, 4, 6],
            "b": [11, 22, 33]
        }

    def test_iterates_correctly(self):
        srch: Searcher = RandGridSearcher(self.params)

        srch.__iter__()

        for candidates in srch:
            self.assertTrue("a" in candidates.keys())
            self.assertTrue("b" in candidates.keys())

    def test_iterates_exhaustively(self):
        for _ in range(100):
            srch = RandGridSearcher(self.params)

            first_candidates = next(srch)

            self.assertGreaterEqual(3, first_candidates["a"])
            self.assertLessEqual(2, first_candidates["a"])
            self.assertGreaterEqual(16, first_candidates["b"])
            self.assertLessEqual(11, first_candidates["b"])

            second_candidates = next(srch)

            self.assertGreaterEqual(3, second_candidates["a"])
            self.assertLessEqual(2, second_candidates["a"])
            self.assertGreaterEqual(27, second_candidates["b"])
            self.assertLessEqual(17, second_candidates["b"])

            for i in range(6):
                next(srch)

            last_candidates = next(srch)

            self.assertGreaterEqual(6, last_candidates["a"])
            self.assertLessEqual(5, last_candidates["a"])
            self.assertGreaterEqual(33, last_candidates["b"])
            self.assertLessEqual(27, last_candidates["b"])


            self.assertRaises(StopIteration, srch.__next__)

    def test_works_with_small_params(self):
        params = {
            "a": [2.3],
            "b": [11.0]
        }
        
        srch: Searcher = RandGridSearcher(params)

        first_candidates = next(srch)

        self.assertDictEqual({
            "a": 2.3,
            "b": 11.0
        }, first_candidates)
        self.assertRaises(StopIteration, srch.__next__)

    def test_works_with_lots_of_params(self):
        self.params["c"] = [100, 101, 102, 103]
        self.params["d"] = [100.1, 101.2, 102.3, 103.4]
        srch: Searcher = RandGridSearcher(self.params)

        count = 0
        for _ in srch:
            count += 1
        
        self.assertEqual(144, count)
