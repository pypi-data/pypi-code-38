import unittest
import os
from .help import *

class TestHelp(unittest.TestCase):
    def setUp(self):
        self.dirname = os.path.dirname(__file__)
        self.dataset = pd.read_csv(self.dirname + "/resources/train.csv")
        self.houses = pd.read_csv(self.dirname + "/resources/houses_train.csv")

    def test_most_related(self):
        cols = most_related_columns(self.houses, "SalePrice", 20)
        self.assertEqual(20, len(cols))
        self.assertEqual("SalePrice", cols[0])
        self.assertEqual("OverallQual", cols[1])
        self.assertEqual("GrLivArea", cols[2])
        self.assertEqual("GarageCars", cols[3])

    def test_all_cols_except(self):
        self.assertFalse("True" in self.dataset.columns.values)
        self.assertFalse("True" in self.dataset.columns.values)
        cols = all_cols_except(self.dataset, ["Cabin", "Sex"])
        self.assertEqual(10, len(cols))
        self.assertFalse("Cabin" in cols)
        self.assertFalse("Sex" in cols)


    
