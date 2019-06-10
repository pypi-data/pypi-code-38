import unittest

import numpy as np
from sklearn.preprocessing import Imputer


class NumericalImputerTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(NumericalImputerTests, self).__init__(*args, **kwargs)
        self.imputer = Imputer()

    def test_missing_vals(self):
        x = np.array([1, 2, 4, 4, np.nan])
        x_t = self.imputer.fit_transform(x.reshape(-1, 1))
        self.assertEqual(x_t[4], 2.75)

    def test_train_test_missing_vals(self):
        # Test the training set. The missing value should be
        # imputed with the mean.
        x_train = np.array([1, 2, 4, 4, np.nan])
        x_train_t = self.imputer.fit_transform(x_train.reshape(-1, 1))
        self.assertEqual(x_train_t[4], 2.75)

        # Test the test set. The missing value should be
        # imputed with the mean learned during training.
        x_test = np.array([1, 2, 5, 5, np.nan])
        x_test_t = self.imputer.transform(x_test.reshape(-1, 1))
        self.assertEqual(x_test_t[4], 2.75)


if __name__ == "__main__":
    unittest.main()
