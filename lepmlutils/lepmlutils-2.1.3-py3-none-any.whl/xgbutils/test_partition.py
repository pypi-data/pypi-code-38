import unittest
import os
import pandas as pd
from .gridsearcher import GridSearcher
from .partition import Partition

class TestPartition(unittest.TestCase):
    def setUp(self):
        pass

    def test_partitions_correctly(self):
        dirname = os.path.dirname(__file__)
        dataset = pd.read_csv(dirname + "/resources/train.csv")
        p = Partition(dataset, 5)

        count = 0
        for partition in p:
            count += 1
            rows, cols = partition["test"].shape
            self.assertEqual(12, cols)
            self.assertLess(176, rows)

            rows, cols = partition["train"].shape
            self.assertEqual(12, cols)
            self.assertLess(710, rows)

        self.assertEqual(count, 5)
