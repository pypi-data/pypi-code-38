import unittest
import os
import pandas as pd
from .coltag import ColTag
from .typetfm import TypeTfm
from .taggeddataframe import TaggedDataFrame

class TestTypeTransform(unittest.TestCase):
    def setUp(self):
        dirname = os.path.dirname(__file__)
        self.dataset = TaggedDataFrame(pd.read_csv(dirname + "/resources/train.csv"))
        self.test = TaggedDataFrame(pd.read_csv(dirname + "/resources/test.csv"))
    
    def test_converts_columns(self):
        self.assertEqual(2, self.dataset.frame.loc[:, self.dataset.frame.dtypes == float].shape[1])
        self.assertEqual(5, self.dataset.frame.loc[:, self.dataset.frame.dtypes == "object"].shape[1])
        self.assertEqual(0, len(self.dataset.tagged_as(ColTag.modified)))

        tfm = TypeTfm(["Age", "Fare"], "object")
        tfm.operate(self.dataset)

        self.assertEqual(0, self.dataset.frame.loc[:, self.dataset.frame.dtypes == float].shape[1])
        self.assertEqual(7, self.dataset.frame.loc[:, self.dataset.frame.dtypes == "object"].shape[1])
        self.assertEqual(2, len(self.dataset.tagged_as(ColTag.modified)))

        tfm = TypeTfm(["Age"], float)
        tfm.operate(self.dataset)
        self.assertEqual(1, self.dataset.frame.loc[:, self.dataset.frame.dtypes == float].shape[1])
        self.assertEqual(6, self.dataset.frame.loc[:, self.dataset.frame.dtypes == "object"].shape[1])


