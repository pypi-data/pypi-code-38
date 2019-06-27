import unittest
import os
from sklearn import neighbors
from .help import *
from .globals import *

class TestHelp(unittest.TestCase):
    def setUp(self):
        self.dirname = os.path.dirname(__file__)
        self.dataset = pd.read_csv(self.dirname + "/resources/train.csv")
        self.houses = pd.read_csv(self.dirname + "/resources/houses_train.csv")
        self.houses_test = pd.read_csv(self.dirname + "/resources/houses_t.csv")

    def test_most_related(self):
        cols = most_related_columns(self.houses, "SalePrice", 20)
        self.assertEqual(20, len(cols))
        self.assertEqual("SalePrice", cols[0])
        self.assertEqual("OverallQual", cols[1])
        self.assertEqual("GrLivArea", cols[2])
        self.assertEqual("GarageCars", cols[3])

    def test_all_cols_except(self):
        self.assertFalse("True" in self.dataset.columns.values)
        self.assertFalse("True" in self.dataset.columns.values)
        cols = all_cols_except(self.dataset, ["Cabin", "Sex"])
        self.assertEqual(10, len(cols))
        self.assertFalse("Cabin" in cols)
        self.assertFalse("Sex" in cols)
    
    def test_dummify(self):
        self.assertEqual(12, self.dataset.shape[1])

        dummify(self.dataset, ["Embarked", "Sex"])
        self.assertEqual(15, self.dataset.shape[1])

        dummify(self.houses, self.houses.loc[:, self.houses.dtypes == "object"].columns.values)
        self.assertEqual(290, self.houses.shape[1])

    def test_dummify_errors(self):
        dummify(self.dataset, ["Embarked", "Sex"])
        self.assertRaises(KeyError, dummify, self.dataset, ["Embarked", "Sex"])

        self.assertRaises(ValueError, dummify, self.dataset, ["Age"])

    def test_dummify_on_converted_cols(self):
        self.assertEqual(12, self.dataset.shape[1])
        self.dataset["Age"] = self.dataset["Age"].astype(str)
        dummify(self.dataset, ["Age", "Sex"])
        self.assertEqual(101, self.dataset.shape[1])

    def test_setting_true_nas(self):
        self.assertEqual(690, self.houses["FireplaceQu"].isna().sum())
        self.assertEqual(259, self.houses["LotFrontage"].isna().sum())
        self.assertEqual(19, self.houses.isna().any().sum())
        set_true_na(self.houses, self.houses.columns.values)
        self.assertEqual(690, (self.houses["FireplaceQu"] == UNKNOWN_STR_VAL).sum())
        self.assertEqual(259, (self.houses["LotFrontage"] == UNKNOWN_NUM_VAL).sum())

        self.assertEqual(0, self.houses.isna().any().sum())
    

    def test_downsize(self):
        self.assertEqual(self.dataset.dtypes[0], "int64")
        self.assertEqual(self.dataset.dtypes[5], "float64")

        downsize(self.dataset)

        self.assertEqual(self.dataset.dtypes[0], "int32")
        self.assertEqual(self.dataset.dtypes[5], "float32")


    def test_setting_true_nas_errors(self):
        self.houses["FireplaceQu"] = self.houses["FireplaceQu"].astype("category")
        self.assertRaises(AssertionError, set_true_na, self.houses, self.houses.columns.values)

    def test_setting_true_nas_unknown_already_present(self):
        self.houses.at[100, "FireplaceQu"] = UNKNOWN_STR_VAL
        self.assertRaises(AssertionError, set_true_na, self.houses, self.houses.columns.values)

    def test_est_impute(self):
        est = neighbors.KNeighborsClassifier()
        convert_to_cat_codes(self.houses, str_cols(self.houses))
        fill_ordinal_na(self.houses, int_cols(self.houses))
        self.assertEqual(1369, (self.houses["Alley"] == CATEGORICAL_BAD_VALUE).sum())
        self.assertEqual(690, (self.houses["FireplaceQu"] == CATEGORICAL_BAD_VALUE).sum())
        self.assertEqual(313, (self.houses["FireplaceQu"] == 4).sum())
        self.assertEqual(380, (self.houses["FireplaceQu"] == 2).sum())

        cls_impute(est, self.houses, ["Alley", "FireplaceQu"])
        self.assertEqual(0, (self.houses["Alley"] == CATEGORICAL_BAD_VALUE).sum())
        self.assertEqual(0, (self.houses["FireplaceQu"] == CATEGORICAL_BAD_VALUE).sum())
        self.assertEqual(485, (self.houses["FireplaceQu"] == 4).sum())
        self.assertEqual(855, (self.houses["FireplaceQu"] == 2).sum())

        est = neighbors.KNeighborsRegressor()
        self.assertEqual(259, (self.houses["LotFrontage"] == ORDINAL_BAD_VALUE).sum())
        reg_impute(est, self.houses, ["LotFrontage"])
        self.assertEqual(0, (self.houses["LotFrontage"] == ORDINAL_BAD_VALUE).sum())     

    def test_est_impute_col_ignore(self):
        est = neighbors.KNeighborsClassifier()
        convert_to_cat_codes(self.houses, str_cols(self.houses))
        fill_ordinal_na(self.houses, int_cols(self.houses))
        self.houses["OverallCond"] = float('nan')
        self.assertRaises(ValueError, cls_impute, est, self.houses, ["Alley", "FireplaceQu"])

        cls_impute(est, self.houses, ["Alley", "FireplaceQu"], ignore=["OverallCond"])



    def test_categorize_strings(self):
        self.assertEqual(19, self.houses.isna().any().sum())
        self.assertEqual(43, len(self.houses.select_dtypes(include="object").columns))
        self.assertEqual(1369, self.houses["Alley"].isna().sum())
        
        convert_to_cat_codes(self.houses, str_cols(self.houses))
        self.assertEqual(0, len(self.houses.select_dtypes(include="object").columns))
        self.assertEqual(0, self.houses["Alley"].isna().sum())
        self.assertEqual(1369, (self.houses["Alley"] == CATEGORICAL_BAD_VALUE).sum())
        self.assertEqual(3, self.houses.isna().any().sum())

    def test_ordinal_fill(self):
        self.assertEqual(19, self.houses.isna().any().sum())
        fill_ordinal_na(self.houses, int_cols(self.houses))
        self.assertEqual(16, self.houses.isna().any().sum())

    def test_ordinal_fill_errors(self):
        self.houses.at[99, "LotFrontage"] = ORDINAL_BAD_VALUE
        self.assertRaises(AssertionError, fill_ordinal_na, self.houses, ["LotFrontage"])
    
    def test_non_numeric(self):
        self.assertEqual(5, len(str_cols(self.dataset)))

        self.dataset["Age"] = self.dataset["Age"].astype("category") 
        self.assertEqual(6, len(str_cols(self.dataset)))

        self.dataset["Sex"] = self.dataset["Sex"].astype("category") 
        self.assertEqual(6, len(str_cols(self.dataset)))

        self.dataset["Sex"] = self.dataset["Sex"].cat.codes
        self.assertEqual(5, len(str_cols(self.dataset)))
    
    def test_encode_int(self):
        self.assertEqual(43, len(self.houses.select_dtypes(include="object").columns))
        self.assertEqual(146, (self.houses["ExterCond"] == "Gd").sum())
        qual_map = {"NA": -1, "Po": 0, "Fa": 1, "TA": 2, "Gd": 3, "Ex": 4}
        exp_map = {"NA": -1, "No": 0, "Mn": 1, "Av": 2, "Gd": 3}
        slope_map = {"NA": -1, "Gtl": 0, "Mod": 1, "Sev": 2}
        func_map ={"NA": -1, "Sal":1, "Sev":2, "Maj2":3, "Maj1":4, "Mod":5, "Min2":6, "Min1":7, "Typ":8}

        str_ord_cats = [
            'FireplaceQu', 'BsmtQual', 'BsmtCond', 'GarageQual', 'GarageCond', 
            'ExterQual', 'ExterCond','HeatingQC',  'KitchenQual', 
            'Functional', 'BsmtExposure', 'LandSlope', 
        ]

        manual_enc = {
            "FireplaceQu": qual_map,
            "BsmtQual": qual_map,
            "BsmtQual": qual_map,
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

        encode_to_int(self.houses, manual_enc)
        self.assertEqual(146, (self.houses["ExterCond"] == 3).sum())
        self.assertEqual(32, len(self.houses.select_dtypes(include="object").columns))

        

        







    
