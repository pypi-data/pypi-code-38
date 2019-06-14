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
        set_true_nas(self.houses, self.houses.columns.values)
        self.assertEqual(690, (self.houses["FireplaceQu"] == UNKNOWN_STR_VAL).sum())
        self.assertEqual(259, (self.houses["LotFrontage"] == UNKNOWN_NUM_VAL).sum())

        self.assertEqual(0, self.houses.isna().any().sum())
    
    def test_setting_true_nas_errors(self):
        self.houses["FireplaceQu"] = self.houses["FireplaceQu"].astype("category")
        self.assertRaises(AssertionError, set_true_nas, self.houses, self.houses.columns.values)

    def test_setting_true_nas_unknown_already_present(self):
        self.houses.at[100, "FireplaceQu"] = UNKNOWN_STR_VAL
        self.assertRaises(AssertionError, set_true_nas, self.houses, self.houses.columns.values)

    def test_est_impute(self):
        est = neighbors.KNeighborsClassifier()
        categorize_all_strings(self.houses)
        fill_ordinal_na(self.houses)
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

    def test_categorize_strings(self):
        self.assertEqual(19, self.houses.isna().any().sum())
        self.assertEqual(43, len(self.houses.select_dtypes(include="object").columns))
        self.assertEqual(1369, self.houses["Alley"].isna().sum())
        
        categorize_all_strings(self.houses)
        self.assertEqual(0, len(self.houses.select_dtypes(include="object").columns))
        self.assertEqual(0, self.houses["Alley"].isna().sum())
        self.assertEqual(1369, (self.houses["Alley"] == CATEGORICAL_BAD_VALUE).sum())
        self.assertEqual(3, self.houses.isna().any().sum())

    def test_ordinal_fill(self):
        self.assertEqual(19, self.houses.isna().any().sum())
        fill_ordinal_na(self.houses)
        self.assertEqual(16, self.houses.isna().any().sum())

    def test_ordinal_fill_errors(self):
        self.houses[99, "LotFrontage"] = ORDINAL_BAD_VALUE
        self.assertRaises(AssertionError, fill_ordinal_na, self.houses)

    def test_encode_strings_and_na_values(self):
        self.assertEqual(19, self.houses.isna().any().sum())
        encode_string_na(self.houses)
        self.assertEqual(0, self.houses.isna().any().sum())

        self.assertEqual(33, self.houses_test.isna().any().sum())
        encode_string_na(self.houses_test)
        self.assertEqual(0, self.houses_test.isna().any().sum())

        self.assertEqual(3, self.dataset.isna().any().sum())
        encode_string_na(self.dataset)
        self.assertEqual(0, self.dataset.isna().any().sum())
    
    def test_non_numeric(self):
        self.assertEqual(5, len(cat_cols(self.dataset)))

        self.dataset["Age"] = self.dataset["Age"].astype("category") 
        self.assertEqual(6, len(cat_cols(self.dataset)))

        self.dataset["Sex"] = self.dataset["Sex"].astype("category") 
        self.assertEqual(6, len(cat_cols(self.dataset)))

        self.dataset["Sex"] = self.dataset["Sex"].cat.codes
        self.assertEqual(5, len(cat_cols(self.dataset)))
        







    
