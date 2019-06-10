import unittest
import numpy as np
import pandas as pd

from azureml.automl.core.featurizer.transformer.timeseries.numericalize_transformer import NumericalizeTransformer
from automl.client.core.common.time_series_data_frame import TimeSeriesDataFrame


def _get_transform_mapping(domain_array, target_array):
    """
    Private utility for extracting a dict/mapping from
    domain to target values.
    Domain and target are assumed to be the same length
    """
    mapping = {}
    for lvl, val in zip(domain_array, target_array):
        if lvl not in mapping:
            mapping[lvl] = val

    return mapping


class TestFTKMLNumericalizeTransformer(unittest.TestCase):
    """
    Unit tests for the Numericalize transform.

    Test NumericalizeTransformer using the transform method and also as
    part of a forecast pipeline
    """
    def setUp(self):
        train_df = pd.DataFrame({'date': pd.date_range('2012', periods=3, freq='YS'),
                                 'type': [1, 1, 2],
                                 'cat_val': ['a', 'b', 'c'],
                                 'value': np.arange(3)})

        self.train_tsdf = TimeSeriesDataFrame(data=train_df,
                                              grain_colnames=['type'],
                                              time_colname='date',
                                              ts_value_colname='value')

    def test_numericalize_consistency(self):
        """
        Test that the Numericalize transform makes consistent encodings
        when some levels are missing that were in a training set
        """
        encoder = NumericalizeTransformer()
        out_tsdf = encoder.fit_transform(self.train_tsdf)

        # Construct transform mapping for the training set
        train_cat_mapping = _get_transform_mapping(self.train_tsdf.cat_val.values,
                                                   out_tsdf.cat_val.values)

        # Test that the categorical column has been numerically encoded
        train_num_cols = (out_tsdf.select_dtypes(include=[np.number]).columns)
        self.assertTrue('cat_val' in train_num_cols)

        # Transform the test set and get the categorical mapping
        test_df = pd.DataFrame({'date': pd.date_range('2015', periods=2, freq='YS'),
                                'type': [1, 1],
                                'cat_val': ['b', 'c'],
                                'value': np.arange(2)})
        test_tsdf = TimeSeriesDataFrame(data=test_df,
                                        grain_colnames=['type'],
                                        time_colname='date',
                                        ts_value_colname='value')
        test_out = encoder.transform(test_tsdf)
        test_cat_mapping = _get_transform_mapping(test_df.cat_val.values,
                                                  test_out.cat_val.values)

        # Compare the mappings on the intersection of train and test map keys
        common_keys = train_cat_mapping.keys() & test_cat_mapping.keys()
        train_cat_mapping_sub = {lvl: val
                                 for lvl, val in train_cat_mapping.items()
                                 if lvl in common_keys}
        test_cat_mapping_sub = {lvl: val
                                for lvl, val in test_cat_mapping.items()
                                if lvl in common_keys}
        self.assertDictEqual(train_cat_mapping_sub, test_cat_mapping_sub)

    def test_numericalize_missing_level(self):
        """
        Test that the Numericalize transform makes consistent encodings
        when some levels are missing that were in a training set
        """
        train_df = pd.DataFrame({'date': pd.date_range('2012', periods=3, freq='YS'),
                                 'type': [1, 1, 2],
                                 'cat_val': ['a', 'a', 'c'],
                                 'value': np.arange(3)})
        train_tsdf = TimeSeriesDataFrame(data=train_df,
                                         grain_colnames=['type'],
                                         time_colname='date',
                                         ts_value_colname='value')

        test_df = pd.DataFrame({'date': pd.date_range('2015', periods=3, freq='YS'),
                                'type': [1, 1, 2],
                                'cat_val': ['a', 'c', 'b'],
                                'value': np.arange(3)})
        test_tsdf = TimeSeriesDataFrame(data=test_df,
                                        grain_colnames=['type'],
                                        time_colname='date',
                                        ts_value_colname='value')

        encoder = NumericalizeTransformer()
        train_out = encoder.fit_transform(train_tsdf)

        # Construct transform mapping for the training set
        train_cat_mapping = _get_transform_mapping(train_df.cat_val.values,
                                                   train_out.cat_val.values)

        # Transform the test set and get the categorical mapping
        test_out = encoder.transform(test_tsdf)
        test_cat_mapping = _get_transform_mapping(test_df.cat_val.values,
                                                  test_out.cat_val.values)

        # Test that levels present in train are encoded consistently and
        #  that the "missing level" has the integer code for NA (missing value)
        missing_level_map = {lvl: NumericalizeTransformer.NA_CODE
                             for lvl in test_cat_mapping
                             if lvl not in train_cat_mapping}
        expected_cat_mapping = train_cat_mapping.copy()
        expected_cat_mapping.update(missing_level_map)
        self.assertDictEqual(expected_cat_mapping, test_cat_mapping)


if __name__ == '__main__':
    unittest.main()
