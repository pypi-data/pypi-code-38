import unittest
import os
import pandas as pd
from .addcoltfm import AddColTfm
from .taggeddataframe import TaggedDataFrame
from .coltag import ColTag

class TestAddColTfm(unittest.TestCase):
    def setUp(self):
        dirname = os.path.dirname(__file__)
        self.dataset = TaggedDataFrame(pd.read_csv(dirname + "/resources/train.csv"))

    def test_adds_colum_and_tages_properly(self):
        tfm = AddColTfm("Age_Fare", ["Age", "Fare"])
       
        self.assertEqual(12, self.dataset.frame.shape[1])
        tfm.operate(self.dataset)
        self.assertEqual(13, self.dataset.frame.shape[1])
        self.assertEqual(ColTag.engineered, self.dataset.tags["Age_Fare"][0])
        self.assertEqual(1, len(self.dataset.tags["Age_Fare"]))
    
    def test_error(self):
        tfm = AddColTfm("Age_Fare", ["BadCol", "Fare"])

        self.assertRaises(KeyError, tfm.operate, self.dataset)
        
        self.assertRaises(ValueError, AddColTfm, "Age_Fare", ["Fare"])






