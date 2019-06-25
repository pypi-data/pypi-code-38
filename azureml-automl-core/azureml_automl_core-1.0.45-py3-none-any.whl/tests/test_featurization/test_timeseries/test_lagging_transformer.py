import unittest

import pandas as pd
import numpy as np
from scipy import sparse

from azureml.automl.core import preprocess as pp


class LaggingTransformTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(LaggingTransformTests, self).__init__(*args, **kwargs)

    def test_dataframe(self):
        tr = pp.LaggingTransformer(3)
        x = pd.DataFrame(data=[[0, 1, 2], [3, 4, 5], [6, 7, 8]],
                         columns=['a', 'b', 'c'])
        expected_engineered_feature_names = ['a', 'b', 'c',
                                             'a_lag_1', 'b_lag_1', 'c_lag_1',
                                             'a_lag_2', 'b_lag_2', 'c_lag_2',
                                             'a_lag_3', 'b_lag_3', 'c_lag_3']
        expected_output = pd.DataFrame([[0, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                        [3, 4, 5, 0, 1, 2, 0, 0, 0, 0, 0, 0],
                                        [6, 7, 8, 3, 4, 5, 0, 1, 2, 0, 0, 0]])

        output = pd.DataFrame(tr.fit_transform(x).astype(np.int64))
        self.assertTrue(output.equals(expected_output))

        # Check engineered feature names
        self.assertListEqual(expected_engineered_feature_names, tr.get_engineered_feature_names())

    def test_sparse_dataframe(self):
        tr = pp.LaggingTransformer(1)
        x = pd.SparseDataFrame(data=[[0, 1, 2], [3, 4, 5], [6, 7, 8]], columns=['a', 'b', 'c'])
        expected_engineered_feature_names = ['a', 'b', 'c',
                                             'a_lag_1', 'b_lag_1', 'c_lag_1']
        expected_output = pd.SparseDataFrame([[0, 1, 2, np.nan, np.nan, np.nan],
                                              [3, 4, 5, 0, 1, 2],
                                              [6, 7, 8, 3, 4, 5]])

        output = pd.SparseDataFrame(tr.fit_transform(x).astype(np.int64))
        self.assertTrue(output.shape[0], expected_output.shape[0])
        self.assertTrue(output.shape[1], expected_output.shape[1])

        # Check engineered feature names
        self.assertListEqual(expected_engineered_feature_names,
                             tr.get_engineered_feature_names())

    def test_numpy(self):
        tr = pp.LaggingTransformer(1)
        x = np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8]])
        expected_output = np.array([[0, 1, 2, 0, 0, 0],
                                    [3, 4, 5, 0, 1, 2],
                                    [6, 7, 8, 3, 4, 5]])
        expected_engineered_feature_names = ['C1', 'C2', 'C3',
                                             'C1_lag_1', 'C2_lag_1', 'C3_lag_1']

        self.assertTrue(np.all(tr.fit_transform(x) == expected_output))

        # Check engineered feature names
        self.assertListEqual(expected_engineered_feature_names,
                             tr.get_engineered_feature_names())

    def test_numpy_with_single_column(self):
        tr = pp.LaggingTransformer(1)
        x = np.array([[0], [3], [6]])
        expected_output = np.array([[0, 0],
                                    [3, 0],
                                    [6, 3]])
        expected_engineered_feature_names = ['C1',
                                             'C1_lag_1']

        self.assertTrue(np.all(tr.fit_transform(x) == expected_output))

        # Check engineered feature names
        self.assertListEqual(expected_engineered_feature_names,
                             tr.get_engineered_feature_names())

    def test_sparse(self):
        tr = pp.LaggingTransformer(1)
        x = np.array([[0, 1, 2], [3, 4, 5], [6, 7, 8]])
        x = sparse.csr_matrix(x)
        expected_output = np.array([[0, 1, 2, 0, 0, 0],
                                    [3, 4, 5, 0, 1, 2],
                                    [6, 7, 8, 3, 4, 5]])
        expected_engineered_feature_names = ['C1', 'C2', 'C3',
                                             'C1_lag_1', 'C2_lag_1', 'C3_lag_1']

        expected_output = sparse.csr_matrix(expected_output)

        self.assertEqual((tr.fit_transform(x) != expected_output).nnz, 0)

        # Check engineered feature names
        self.assertListEqual(expected_engineered_feature_names,
                             tr.get_engineered_feature_names())


if __name__ == "__main__":
    unittest.main()
