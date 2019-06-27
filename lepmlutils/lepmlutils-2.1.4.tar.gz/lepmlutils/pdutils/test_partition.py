from .help import *
from .partition import Partition
import os
from scipy import stats
import unittest

class TestPartition(unittest.TestCase):
    def test_takes_empty_lists(self):
        self.assertEqual(3, self.titanic.isna().any().sum())
        imp = Partition(
            self.titanic,
            ["Pclass"],
            [],
            [],
            ["Cabin", "Embarked", "Name", "Sex", "Ticket"],
            {}
        )


    def test_initializes(self):
        imp = Partition(
            self.houses,
            self.int_ord_cats,
            self.int_unord_cats,
            self.str_ord_cats,
            self.str_unord_cats,
            self.manual_enc
        )
    
        self.assertRaises(
            AssertionError, 
            Partition,             
            self.houses,
            self.int_ord_cats,
            self.int_unord_cats,
            self.str_ord_cats + ["SomeNewCol"],
            self.str_unord_cats,
            self.manual_enc)

        self.assertRaises(
            AssertionError, 
            Partition,             
            self.houses,
            self.int_ord_cats,
            self.int_unord_cats,
            self.str_ord_cats,
            self.str_unord_cats + ["SomeNewCol"],
            self.manual_enc)

        self.assertRaises(
            AssertionError, 
            Partition,             
            self.houses,
            self.int_ord_cats,
            self.int_unord_cats + ["SomeNewCol"],
            self.str_ord_cats,
            self.str_unord_cats,
            self.manual_enc)

        self.assertRaises(
            AssertionError, 
            Partition,             
            self.houses,
            self.int_ord_cats + ["SomeNewCol"],
            self.int_unord_cats,
            self.str_ord_cats,
            self.str_unord_cats,
            self.manual_enc)

        self.assertRaises(
            AssertionError, 
            Partition,             
            self.houses,
            self.int_ord_cats,
            self.int_unord_cats,
            self.str_ord_cats[1:],
            self.str_unord_cats,
            self.manual_enc)

        self.assertRaises(
            AssertionError, 
            Partition,             
            self.houses,
            self.int_ord_cats,
            self.int_unord_cats,
            self.str_ord_cats,
            self.str_unord_cats[1:],
            self.manual_enc)

        val = self.manual_enc.pop("BsmtQual")

        self.assertRaises(
            AssertionError, 
            Partition,             
            self.houses,
            self.int_ord_cats,
            self.int_unord_cats,
            self.str_ord_cats,
            self.str_unord_cats,
            self.manual_enc)

        self.manual_enc["BsmtQual"] = val 

        imp = Partition(
            self.houses,
            self.int_ord_cats,
            self.int_unord_cats,
            self.str_ord_cats,
            self.str_unord_cats,
            self.manual_enc
        )

        self.manual_enc["newCol"] = {}

        self.assertRaises(
            AssertionError, 
            Partition,             
            self.houses,
            self.int_ord_cats,
            self.int_unord_cats,
            self.str_ord_cats,
            self.str_unord_cats,
            self.manual_enc)

    def setUp(self):
        self.dirname = os.path.dirname(__file__)
        self.titanic = pd.read_csv(self.dirname + "/resources/train.csv")
        self.houses = pd.read_csv(self.dirname + "/resources/houses_train.csv")
        self.houses_test = pd.read_csv(self.dirname + "/resources/houses_t.csv")
        self.int_unord_cats = [
            'MSSubClass'
        ]
        self.int_ord_cats = [
            "GarageYrBlt",
            "YearBuilt",
            "OverallQual",
            'MoSold',
            "YearRemodAdd",
            'OverallCond', 
            'YrSold',
        ]

        self.str_ord_cats = [
            'FireplaceQu', 'BsmtQual', 'BsmtCond', 'GarageQual', 'GarageCond',
            'ExterQual', 'ExterCond','HeatingQC',  'KitchenQual', 
            'Functional', 'BsmtExposure', 'LandSlope', 
        ]
        self.str_unord_cats = [
            'MSZoning', 'Alley', 'LotShape', 'LotConfig', 'Neighborhood', 
            'BldgType', 'HouseStyle', 'RoofStyle', 'RoofMatl', 'Exterior1st', 
            'Exterior2nd','MasVnrType', 'Foundation', 'BsmtFinType1', 'BsmtFinType2',
            'Heating','CentralAir', 'Electrical', 'GarageType', "Condition1", "Condition2", 
            'GarageFinish', 'PavedDrive', 'Fence', 'MiscFeature', 'SaleType', "SaleCondition",
            "LandContour", 'PoolQC', 'Street', 'Utilities'
        ]

        qual_map = {"NA": -1, "Po": 0, "Fa": 1, "TA": 2, "Gd": 3, "Ex": 4}
        exp_map = {"NA": -1, "No": 0, "Mn": 1, "Av": 2, "Gd": 3}
        slope_map = {"NA": -1, "Gtl": 0, "Mod": 1, "Sev": 2}
        func_map ={"NA": -1, "Sal":1, "Sev":2, "Maj2":3, "Maj1":4, "Mod":5, "Min2":6, "Min1":7, "Typ":8}

        self.manual_enc = {
            "FireplaceQu": qual_map,
            "BsmtQual": qual_map,
            "BsmtCond": qual_map,
            "GarageQual": qual_map,
            "GarageCond": qual_map,
            "ExterQual": qual_map,
            "ExterCond": qual_map,
            "HeatingQC": qual_map,
            "KitchenQual": qual_map,
            "Functional": func_map,
            "BsmtExposure":exp_map,
            "LandSlope": slope_map    
        }







    
