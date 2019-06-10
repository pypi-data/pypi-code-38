import unittest

import pandas as pd
import numpy as np


from azureml.automl.core import preprocess as pp


class ImputationMarkerTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(ImputationMarkerTests, self).__init__(*args, **kwargs)
        self.imputation_marker_transformer = pp.ImputationMarker()

    def test_imputation_marker_for_non_nan_data(self):
        non_nan_dataframe = pd.DataFrame([0, 1, 2, 3, 4])
        expected_imputation_marker_array = np.array(
            [[False], [False], [False], [False], [False]])

        # Get the imputation marker array
        actual_imputation_marker_array = \
            self.imputation_marker_transformer.fit_transform(
                non_nan_dataframe)
        self.assertTrue(
            np.all(
                expected_imputation_marker_array ==
                actual_imputation_marker_array))

    def test_imputation_marker_for_some_nan_data(self):
        some_nan_dataframe = pd.DataFrame([0, 1, np.nan, 3, 4])
        expected_imputation_marker_array = np.array(
            [[False], [False], [True], [False], [False]])

        # Get the imputation marker array
        actual_imputation_marker_array = \
            self.imputation_marker_transformer.fit_transform(
                some_nan_dataframe)
        self.assertTrue(
            np.all(
                expected_imputation_marker_array ==
                actual_imputation_marker_array))

    def test_imputation_marker_for_all_nan_data(self):
        all_nan_dataframe = pd.DataFrame(
            [np.nan, np.nan, np.nan, np.nan, np.nan])
        expected_imputation_marker_array = np.array(
            [[True], [True], [True], [True], [True]])

        # Get the imputation marker array
        actual_imputation_marker_array = \
            self.imputation_marker_transformer.fit_transform(
                all_nan_dataframe)
        self.assertTrue(
            np.all(
                expected_imputation_marker_array ==
                actual_imputation_marker_array))


if __name__ == "__main__":
    unittest.main()
