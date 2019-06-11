import unittest
import os
import pandas as pd
from .help import merged

class TestHelp(unittest.TestCase):
    def setUp(self):
        self.dirname = os.path.dirname(__file__)
        self.houses = pd.read_csv(self.dirname + "/resources/houses_train.csv")
        self.houses_test = pd.read_csv(self.dirname + "/resources/houses_t.csv")

    def test_can_extract(self):
        self.assertEqual(1460, self.houses.shape[0])
        self.assertEqual(1459, self.houses_test.shape[0])
        df = merged(self.houses, self.houses_test, ["SalePrice"])
        self.assertEqual(2919, df.shape[0])

        df2 = df[["OverallQual", "YearBuilt"]]
        self.assertEqual(2919, df2.shape[0])

        self.assertTrue("SalePrice" not in df.columns.values)



    
