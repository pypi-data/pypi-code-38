import unittest
import os
import pandas as pd
from .medianreplacetfm import MedianReplaceTfm
from .taggeddataframe import TaggedDataFrame
from .coltag import ColTag

class TestColumnReplace(unittest.TestCase):
    def setUp(self):
        dirname = os.path.dirname(__file__)
        self.dataset = TaggedDataFrame(pd.read_csv(dirname + "/resources/train.csv"))
        self.dataset_test = TaggedDataFrame(pd.read_csv(dirname + "/resources/test.csv"))
        self.houses = TaggedDataFrame(pd.read_csv(dirname + "/resources/houses_train.csv"))
    
    def test_raises_adds_bad_value_columns(self):
        self.assertEqual(3, self.dataset.frame.isna().any().sum())
        self.assertEqual(25, (self.dataset.frame["Age"] == 28.0).sum())
        self.assertEqual(687, self.dataset.frame["Cabin"].isna().sum())
        self.assertEqual(2, self.dataset.frame["Embarked"].isna().sum())
        self.assertEqual(0, len(self.houses.tagged_as(ColTag.modified)))

        tfm = MedianReplaceTfm()
        tfm.operate(self.dataset)
        self.assertEqual(0, self.dataset.frame.isna().any().sum())
        self.assertEqual(202, (self.dataset.frame["Age"] == 28.0).sum())
        self.assertEqual(687, (self.dataset.frame["Cabin"] == "unknown").sum())
        self.assertEqual(2, (self.dataset.frame["Embarked"] == "unknown").sum())
        self.assertEqual(3, len(self.dataset.tagged_as(ColTag.modified)))

    def test_re_adds_first_values(self):
        tfm = MedianReplaceTfm()
        tfm.operate(self.dataset)
        self.assertEqual(202, (self.dataset.frame["Age"] == 28.0).sum())

        self.assertEqual(7, (self.dataset_test.frame["Age"] == 28.0).sum())
        tfm.re_operate(self.dataset_test)
        self.assertEqual(93, (self.dataset_test.frame["Age"] == 28.0).sum())

    def test_raises_adds_bad_value_columns_for_house_data(self):
        self.assertEqual(19, self.houses.frame.isna().any().sum())
        self.assertEqual(0, len(self.houses.tagged_as(ColTag.modified)))
        tfm = MedianReplaceTfm()
        tfm.operate(self.houses)
        self.assertEqual(0, self.houses.frame.isna().any().sum())
        self.assertEqual(19, len(self.houses.tagged_as(ColTag.modified)))


    def test_raises_adds_bad_value_columns_no_existing_unknowns(self):
        tfm = MedianReplaceTfm()

        self.dataset.frame.loc[0, "Cabin"] = "unknown"
        self.assertRaises(AssertionError, tfm.operate, self.dataset)
