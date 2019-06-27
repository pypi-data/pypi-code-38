import unittest
import os
from .skewtfm import SkewTfm 
from .taggeddataframe import TaggedDataFrame
from .coltag import ColTag
from .help import *
import pandas as pd
from scipy import stats

class TestSkewTfm(unittest.TestCase):
    def setUp(self):
        self.dirname = os.path.dirname(__file__)
        self.dataset = TaggedDataFrame(pd.read_csv(self.dirname + "/resources/train.csv"))

    def test_skews(self):
        tfm = SkewTfm(["Age", "Fare"])
        self.assertAlmostEqual(0.3882898514698657 , stats.skew(self.dataset.frame["Age"].dropna()))
        self.assertAlmostEqual(4.7792532923723545 , stats.skew(self.dataset.frame["Fare"].dropna()))
        tfm.operate(self.dataset)
        self.assertAlmostEqual(0.3882898514698657 , stats.skew(self.dataset.frame["Age"].dropna()))
        self.assertAlmostEqual(0.39426283638993376 , stats.skew(self.dataset.frame["Fare"].dropna()))

        self.assertEqual(1, len(self.dataset.tagged_as(ColTag.modified)))

