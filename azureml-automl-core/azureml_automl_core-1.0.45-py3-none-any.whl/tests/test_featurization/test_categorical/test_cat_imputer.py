import unittest

import pandas as pd
import numpy as np

from azureml.automl.core import preprocess as pp


class CatImputerTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(CatImputerTests, self).__init__(*args, **kwargs)
        self.cat_imputer = pp.CatImputer()

    def test_unique_vals(self):
        # Test with numeric strings
        x = pd.Series(['1', '2', '4', '4', np.nan])
        x_t = self.cat_imputer.fit_transform(x)
        self.assertEqual(x_t[4], '4')

        # Test with strings
        x = pd.Series(['bear', 'cat', 'dog', 'dog', np.nan])
        x_t = self.cat_imputer.fit_transform(x)
        self.assertEqual(x_t[4], 'dog')

    def test_missing_val(self):
        # Test with numeric strings
        x = pd.Series(['4', None, None])
        x_t = self.cat_imputer.fit_transform(x)
        self.assertEqual(x_t[1], '4')
        self.assertEqual(x_t[2], '4')

        # Test with strings
        x = pd.Series(['cat', None, None])
        x_t = self.cat_imputer.fit_transform(x)
        self.assertEqual(x_t[1], 'cat')
        self.assertEqual(x_t[2], 'cat')

    def test_all_missing_val(self):
        x = pd.Series([None, None, None, None, None])
        x_t = self.cat_imputer.fit_transform(x)
        self.assertEqual(x_t[4], str(np.nan))

    def test_all_missing_val_in_train_data(self):
        # Test the training set when all entries are missing.
        # The missing value should be 'nan'.
        x_train = pd.Series([None, None, None, None, None])
        x_train_t = self.cat_imputer.fit_transform(x_train)
        self.assertEqual(x_train_t[4], str(np.nan))

        # Test the test set. The missing value should be
        # imputed with 'nan'.
        x_test = pd.Series(['1', '2', '5', '5', np.nan])
        x_test_t = self.cat_imputer.transform(x_test)
        self.assertEqual(x_test_t[4], str(np.nan))

    def test_train_test_missing_vals(self):
        # Test the training set. The missing value should be
        # imputed with the mode.
        x_train = pd.Series(['1', '2', '4', '4', np.nan])
        x_train_t = self.cat_imputer.fit_transform(x_train)
        self.assertEqual(x_train_t[4], '4')

        # Test the test set. The missing value should be
        # imputed with the mode learned during training.
        x_test = pd.Series(['1', '2', '5', '5', np.nan])
        x_test_t = self.cat_imputer.transform(x_test)
        self.assertEqual(x_test_t[4], '4')


if __name__ == "__main__":
    unittest.main()
