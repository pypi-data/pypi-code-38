import unittest
import os
from .lepdataframe import LepDataFrame
from .badindicatortfm import BadIndicatorTfm
from .medianreplacetfm import MedianReplaceTfm
from .categorizetfm import CategorizeTfm
from .coltag import ColTag
import pandas as pd

class TestLepDataFrame(unittest.TestCase):
    def setUp(self):
        self.dirname = os.path.dirname(__file__)
        self.dataset = pd.read_csv(self.dirname + "/resources/train.csv")
        self.houses = pd.read_csv(self.dirname + "/resources/houses_train.csv")
        self.houses_test = pd.read_csv(self.dirname + "/resources/houses_t.csv")

    def test_applies_transform(self):
        l = LepDataFrame(self.dataset)
        tfm = BadIndicatorTfm()
        l.apply(tfm)

        self.assertEqual(15, len(l.frame.columns))
    
    def test_copies_transform(self):
        l = LepDataFrame(self.dataset)
        tfm = BadIndicatorTfm()
        l.apply(tfm)
        self.assertEqual(15, len(l.frame.columns))

        l2 = LepDataFrame(pd.read_csv(self.dirname + "/resources/train.csv"))
        l2.copy_from(l)
        self.assertEqual(15, len(l2.frame.columns))

        less_bad_df = pd.read_csv(self.dirname + "/resources/train.csv")
        less_bad_df["Embarked"].fillna("Q", inplace=True)
        self.assertEqual(2, less_bad_df.isna().any().sum())

        l3 = LepDataFrame(less_bad_df)
        l3.copy_from(l2)
        self.assertEqual(15, len(l3.frame.columns))

    def test_applies_sequences(self):
        seq = [
            BadIndicatorTfm(),
            MedianReplaceTfm(),
            CategorizeTfm(self.dataset.select_dtypes(include="object").columns.values),
        ]
        l = LepDataFrame(self.dataset)
        l.apply_sequence(seq)
        self.assertEqual(15, len(l.frame.columns))
        self.assertEqual(0, l.frame.isna().any().sum())

    def test_reapplies_sequences(self):
        seq = [
            BadIndicatorTfm(),
            MedianReplaceTfm(),
            CategorizeTfm(self.houses.select_dtypes(include="object").columns.values),
        ]
        l = LepDataFrame(self.houses)
        l.apply_sequence(seq)
        self.assertEqual(100, len(l.frame.columns))
        self.assertEqual(0, l.frame.isna().any().sum())

        test = LepDataFrame(self.houses_test)
        test.copy_from(l)
        self.assertEqual(99, len(test.frame.columns))
        self.assertEqual(0, test.frame.isna().any().sum())

        cols = l.retrive([], [ColTag.mapping])
        cols = l.retrive([], [ColTag.categorized])
        self.assertEqual(100, len(cols))

        cols = test.retrive([], [ColTag.mapping])
        cols = test.retrive([], [ColTag.categorized])
        self.assertEqual(99, len(cols))



