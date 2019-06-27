import unittest
import pandas as pd
import numpy as np
from pandas.util.testing import assert_frame_equal

from azureml.automl.core.featurizer.transformer.timeseries.max_horizon_featurizer import MaxHorizonFeaturizer
from azureml.automl.core.featurizer.transformer.timeseries.forecasting_pipeline import AzureMLForecastPipeline
from automl.client.core.common.exceptions import DataException
from automl.client.core.common.time_series_data_frame import TimeSeriesDataFrame


class TestMaxHorizonFeaturizer(unittest.TestCase):
    """Test the MaxHorizonFeaturizer."""

    def setUp(self):
        train_df = pd.DataFrame({'date': pd.date_range('2012', periods=3, freq='YS'),
                                 'type': [1, 1, 2],
                                 'value': np.arange(3)})

        self.train_tsdf = TimeSeriesDataFrame(data=train_df,
                                              grain_colnames=['type'],
                                              time_colname='date',
                                              ts_value_colname='value')

    def test_featurizer(self):
        """Test that transform outputs give expected results."""
        max_horizon_featurizer = MaxHorizonFeaturizer(2, origin_time_colname='origin', horizon_colname='horizon')

        # Test the preview column method
        preview_column_list = max_horizon_featurizer.preview_column_names(self.train_tsdf)
        self.assertEqual(len(preview_column_list), 1)
        self.assertEqual(preview_column_list[0], 'horizon')

        tsdf_xform = max_horizon_featurizer.fit_transform(self.train_tsdf)

        src_time_index = pd.date_range('2012', periods=3, freq='YS')
        df_h1 = pd.DataFrame({'date': src_time_index,
                              'origin': src_time_index.shift(-1, freq='YS'),
                              'horizon': [1] * 3,
                              'type': [1, 1, 2],
                              'value': np.arange(3)})
        df_h2 = pd.DataFrame({'date': src_time_index,
                              'origin': src_time_index.shift(-2, freq='YS'),
                              'horizon': [2] * 3,
                              'type': [1, 1, 2],
                              'value': np.arange(3)})

        expected_result = TimeSeriesDataFrame(data=pd.concat((df_h1, df_h2)),
                                              grain_colnames=['type'],
                                              time_colname='date',
                                              origin_time_colname='origin',
                                              ts_value_colname='value')

        # Test that the transform produces the correct result
        tsdf_xform.sort_index(inplace=True, axis=0)
        tsdf_xform.sort_index(inplace=True, axis=1)
        expected_result.sort_index(inplace=True, axis=0)
        expected_result.sort_index(inplace=True, axis=1)

        assert_frame_equal(tsdf_xform, expected_result)

    def test_raises(self):
        """Test that expected exceptions are raised for error conditions."""
        src_time_index = pd.date_range('2012', periods=3, freq='YS')
        df_h1 = pd.DataFrame({'date': src_time_index,
                              'origin': src_time_index.shift(-1, freq='YS'),
                              'horizon': [1] * 3,
                              'type': [1, 1, 2],
                              'value': np.arange(3)})

        tsdf_origins = TimeSeriesDataFrame(data=df_h1,
                                           grain_colnames=['type'],
                                           time_colname='date',
                                           origin_time_colname='origin',
                                           ts_value_colname='value')

        with self.assertRaises(DataException):
            MaxHorizonFeaturizer(2).fit_transform(tsdf_origins)
