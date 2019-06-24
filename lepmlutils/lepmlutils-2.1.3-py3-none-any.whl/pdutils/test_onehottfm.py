import unittest
import os
import pandas as pd
from .coltag import ColTag
from .onehottfm import OnehotTfm
from .taggeddataframe import TaggedDataFrame

class TestOnehotTransform(unittest.TestCase):
    def setUp(self):
        dirname = os.path.dirname(__file__)
        self.dataset = TaggedDataFrame(pd.read_csv(dirname + "/resources/train.csv"))
        self.test = TaggedDataFrame(pd.read_csv(dirname + "/resources/test.csv"))
        self.houses_train = TaggedDataFrame(pd.read_csv(dirname + "/resources/houses_train.csv"))
        self.houses_test = TaggedDataFrame(pd.read_csv(dirname + "/resources/houses_t.csv"))
    
    def test_adds_columns(self):
        self.assertEqual(12, self.dataset.frame.shape[1])

        tfm = OnehotTfm(["Embarked", "Sex"])
        tfm.operate(self.dataset)
        self.assertEqual(15, self.dataset.frame.shape[1])
        self.assertEqual(5, len(self.dataset.tagged_as(ColTag.engineered)))
        self.assertEqual(5, len(self.dataset.tagged_as(ColTag.onehot)))
        self.assertEqual(10, len(self.dataset.tagged_as(ColTag.original)))

        tfm.re_operate(self.test)
        self.assertEqual(14, self.test.frame.shape[1])

    def test_not_too_many(self):
        tfm = OnehotTfm(self.houses_train.frame.loc[:, self.houses_train.frame.dtypes == "object"].columns.values)
        tfm.operate(self.houses_train)
        self.assertEqual(290, self.houses_train.frame.shape[1])

        tfm.re_operate(self.houses_test)
        self.assertEqual(289, self.houses_test.frame.shape[1])

    def test_works_on_converted_columns(self):
        self.assertEqual(12, self.dataset.frame.shape[1])
        self.dataset.frame["Age"] = self.dataset.frame["Age"].astype(str)
        tfm = OnehotTfm(["Age", "Sex"])
        tfm.operate(self.dataset)
        self.assertEqual(101, self.dataset.frame.shape[1])

    def test_raises_errors(self):
        tfm = OnehotTfm(["Embarked", "Sex"])
        tfm.operate(self.dataset)
        self.assertRaises(KeyError, tfm.operate, self.dataset)

        tfm = OnehotTfm(["Age"])
        self.assertRaises(ValueError, tfm.operate, self.dataset)
    
