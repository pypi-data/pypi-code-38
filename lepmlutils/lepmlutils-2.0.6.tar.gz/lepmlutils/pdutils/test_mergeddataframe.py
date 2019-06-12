import unittest
import os
import pandas as pd
from .help import *
from .mergeddataframe import merged_data
from .medianreplacetfm import MedianReplaceTfm

class TestHelp(unittest.TestCase):
    def setUp(self):
        self.dirname = os.path.dirname(__file__)
        self.houses = pd.read_csv(self.dirname + "/resources/houses_train.csv")
        self.houses_test = pd.read_csv(self.dirname + "/resources/houses_t.csv")

    def test_can_stores_data_correctly(self):
        self.assertEqual(1460, self.houses.shape[0])
        self.assertEqual(1459, self.houses_test.shape[0])
        df = merged_data(self.houses, self.houses_test, ["SalePrice"])
        self.assertEqual(2919, df.shape[0])
        
        trn = df.extract_train()
        tst = df.extract_test()
        targs = df.train_targets
        self.assertEqual(1460, trn.shape[0])
        self.assertEqual(1459, tst.shape[0])
        self.assertEqual(1460, targs.shape[0])
        self.assertEqual(1, targs.shape[1])

        df2 = df[["OverallQual", "YearBuilt"]]
        self.assertEqual(2919, df2.shape[0])

        trn = df2.extract_train()
        tst = df2.extract_test()
        targs = df2.train_targets
        self.assertEqual(1460, trn.shape[0])
        self.assertEqual(1459, tst.shape[0])
        self.assertEqual(1460, targs.shape[0])
        self.assertEqual(1, targs.shape[1])

        self.assertTrue("SalePrice" not in df.columns.values)

    def test_dropping_rows(self):
        df = merged_data(self.houses, self.houses_test, ["SalePrice"])
        df.drop([523, 1298], inplace=True)
        self.assertEqual(1458, df.extract_train().shape[0])

    def test_whole_frame_assignment(self):
        df = merged_data(self.houses, self.houses_test, ["SalePrice"])
        dummify(df, df.loc[:, df.dtypes == "object"].columns.values)
        self.assertEqual(289, df.shape[1])
        self.assertEqual(289, df.extract_train().shape[1])

    def test_changes_effect_all_frames(self):
        self.assertEqual(19, self.houses.isna().any().sum())
        self.assertEqual(33, self.houses_test.isna().any().sum())

        df = merged_data(self.houses, self.houses_test, ["SalePrice"])
        df.fillna(0, inplace=True)
        self.assertEqual(0, df.isna().any().sum())
        self.assertEqual(0, df.extract_train().isna().any().sum())
        self.assertEqual(0, df.extract_test().isna().any().sum())
        self.assertEqual(19, self.houses.isna().any().sum())




    
