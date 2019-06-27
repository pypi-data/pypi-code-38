import unittest
from typing import Type
from .gridsearcher import GridSearcher
from .searcher import Searcher

class TestGridSearcher(unittest.TestCase):
    def setUp(self):
        self.params = {
            "a": [2, 4, 6],
            "b": [11, 22, 33]
        }

    def test_iterates_correctly(self):
        srch: Searcher = GridSearcher(self.params)

        srch.__iter__()

        for candidates in srch:
            self.assertTrue("a" in candidates.keys())
            self.assertTrue("b" in candidates.keys())

    def test_iterates_exhaustively(self):
        srch = GridSearcher(self.params)

        first_candidates = next(srch)

        self.assertDictEqual({
            "a": 2,
            "b": 11
        }, first_candidates)

        second_candidates = next(srch)


        self.assertDictEqual({
            "a": 2,
            "b": 22
        }, second_candidates)

        for i in range(6):
            next(srch)

        first_candidates = next(srch)

        self.assertDictEqual({
            "a": 6,
            "b": 33
        }, first_candidates)

        self.assertRaises(StopIteration, srch.__next__)

    def test_works_with_small_params(self):
        params = {
            "a": [2.3],
            "b": [11.0]
        }
        
        srch: Searcher = GridSearcher(params)

        first_candidates = next(srch)

        self.assertDictEqual({
            "a": 2.3,
            "b": 11.0
        }, first_candidates)
        self.assertRaises(StopIteration, srch.__next__)

    def test_works_with_lots_of_params(self):
        self.params["c"] = [100, 101, 102, 103]
        self.params["d"] = [100.1, 101.2, 102.3, 103.4]
        srch: Searcher = GridSearcher(self.params)

        count = 0
        for _ in srch:
            count += 1
        
        self.assertEqual(144, count)
