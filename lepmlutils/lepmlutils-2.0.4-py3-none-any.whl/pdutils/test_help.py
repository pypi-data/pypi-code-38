import unittest
import os
from .help import *

class TestHelp(unittest.TestCase):
    def setUp(self):
        self.dirname = os.path.dirname(__file__)
        self.dataset = pd.read_csv(self.dirname + "/resources/train.csv")
        self.houses = pd.read_csv(self.dirname + "/resources/houses_train.csv")
        self.houses_test = pd.read_csv(self.dirname + "/resources/houses_t.csv")

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
    
    def test_dummify(self):
        self.assertEqual(12, self.dataset.shape[1])

        dummify(self.dataset, ["Embarked", "Sex"])
        self.assertEqual(15, self.dataset.shape[1])

        dummify(self.houses, self.houses.loc[:, self.houses.dtypes == "object"].columns.values)
        self.assertEqual(290, self.houses.shape[1])

    def test_dummify_errors(self):
        dummify(self.dataset, ["Embarked", "Sex"])
        self.assertRaises(KeyError, dummify, self.dataset, ["Embarked", "Sex"])

        self.assertRaises(ValueError, dummify, self.dataset, ["Age"])

    def test_dummify_on_converted_cols(self):
        self.assertEqual(12, self.dataset.shape[1])
        self.dataset["Age"] = self.dataset["Age"].astype(str)
        dummify(self.dataset, ["Age", "Sex"])
        self.assertEqual(101, self.dataset.shape[1])


    
