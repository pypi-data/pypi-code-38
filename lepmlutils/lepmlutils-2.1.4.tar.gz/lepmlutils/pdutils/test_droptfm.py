import unittest
import os
import pandas as pd
from .droptfm import DropTfm
from .taggeddataframe import TaggedDataFrame

class TestDropTransform(unittest.TestCase):
    def setUp(self):
        dirname = os.path.dirname(__file__)
        self.dataset = TaggedDataFrame(pd.read_csv(dirname + "/resources/train.csv"))
    
    def test_drops_properly(self):
        self.assertEqual(12, self.dataset.frame.shape[1])

        tfm = DropTfm(["Cabin", "Sex"])
        tfm.operate(self.dataset)
        self.assertEqual(10, self.dataset.frame.shape[1])
        self.assertEqual(10, len(self.dataset.retrive()))

        self.assertRaises(KeyError, tfm.re_operate, self.dataset)


    
