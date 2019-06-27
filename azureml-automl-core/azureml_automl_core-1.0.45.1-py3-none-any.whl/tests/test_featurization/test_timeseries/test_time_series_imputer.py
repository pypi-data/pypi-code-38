import unittest
import warnings

import pandas as pd
from pandas.util.testing import assert_frame_equal
import numpy as np

from azureml.automl.core.featurizer.transformer.timeseries.time_series_imputer import TimeSeriesImputer
from azureml.automl.core.featurizer.transformer.timeseries.forecasting_pipeline import AzureMLForecastPipeline
from automl.client.core.common.time_series_data_frame import TimeSeriesDataFrame

warnings.filterwarnings("ignore")


class TestTSImputer(unittest.TestCase):
    """Unit tests for the tsimputer."""

    # Construct a sample dataframe: df1
    # Notice that df1 is not a regular time series, because for store 'a',
    # the row for date '2017-01-03' is missing.
    data1 = pd.DataFrame(
        {'store': ['a', 'a', 'b', 'b', 'c', 'c', 'c', 'd',
                   'd', 'd', 'd', 'd', 'd', 'd', 'd'],
         'date': pd.to_datetime(
            ['2017-01-02', '2017-01-04', '2017-01-01', '2017-01-02',
             '2017-01-01', '2017-01-02', '2017-01-03', '2017-01-01',
             '2017-01-02', '2017-01-03', '2017-01-04', '2017-01-05',
             '2017-01-06', '2017-01-07', '2017-01-08']),
         'sales': [1, np.nan, 2, np.nan, 6, 7, np.nan, 10, 11, 15, 13, 14,
                   np.nan, np.nan, 15],
         'price': [np.nan, 3, np.nan, 4, 3, 6, np.nan, 2, 6, 3, 5, 5,
                   np.nan, np.nan, 6]})
    df1 = TimeSeriesDataFrame(data1, grain_colnames=['store'],
                              time_colname='date', ts_value_colname='sales')

    df_with_origin = pd.DataFrame({
        'Store': ['a'] * 8,
        'Date': pd.DatetimeIndex(['2017-01-08', '2017-01-15',
                                  '2017-01-15', '2017-01-22',
                                  '2017-01-29', '2017-01-22',
                                  '2017-01-29', '2017-02-05']),
        'Origin_Date': pd.DatetimeIndex(['2017-01-01', '2017-01-01',
                                         '2017-01-08', '2017-01-08',
                                         '2017-01-08', '2017-01-15',
                                         '2017-01-15', '2017-01-15']),
        'Order_Number': [1, 1, np.nan, np.nan, np.nan, 5, 5, 5],
        'Sales': [1, np.nan, np.nan, 3, np.nan, 3, np.nan, 5],
        'Random_Var': [4, np.nan, 2, np.nan, 4, 5, 6, np.nan]
    })

    no_grain_df = df1.sort_index().loc[pd.IndexSlice[:, 'c'], :].reset_index(
        level='store', drop=True)

    def test_impute_single_value(self):
        """
        This method tests imputing a single column 'sales' with option 'default'
        """
        self.imputer1 = TimeSeriesImputer(input_column='sales',
                                          option='interpolate', method='linear')
        self.transform1 = self.imputer1.transform(TestTSImputer.df1)
        expected_data = pd.DataFrame(
            {'store': ['a', 'a', 'a', 'b', 'b', 'c', 'c', 'c', 'd',
                       'd', 'd', 'd', 'd', 'd', 'd', 'd'],
             'date': pd.to_datetime(
                ['2017-01-02', '2017-01-03', '2017-01-04', '2017-01-01', '2017-01-02',
                 '2017-01-01', '2017-01-02', '2017-01-03', '2017-01-01',
                 '2017-01-02', '2017-01-03', '2017-01-04', '2017-01-05',
                 '2017-01-06', '2017-01-07', '2017-01-08']),
             'sales': [1, 1, 1, 2, 2, 6, 7, 7, 10, 11, 15, 13, 14,
                       14.333333, 14.666667, 15],
             'price': [np.nan, np.nan, 3, np.nan, 4, 3, 6, np.nan, 2, 6, 3, 5, 5,
                       np.nan, np.nan, 6]})
        expected_output = TimeSeriesDataFrame(expected_data, grain_colnames=['store'],
                                              time_colname='date', ts_value_colname='sales')
        assert_frame_equal(self.transform1.sort_index(),
                           expected_output.sort_index())

    def test_impute_single_value_explicit_freq(self):
        """
        This method tests imputing a single column 'sales' with option 'default'
        and the `freq` explicitly stated.
        """
        self.imputer2 = TimeSeriesImputer(input_column='sales',
                                          option='interpolate',
                                          method='linear', freq='D')
        self.transform2 = self.imputer2.transform(TestTSImputer.df1)
        expected_data = pd.DataFrame(
            {'store': ['a', 'a', 'a', 'b', 'b', 'c', 'c', 'c', 'd',
                       'd', 'd', 'd', 'd', 'd', 'd', 'd'],
             'date': pd.to_datetime(
                ['2017-01-02', '2017-01-03', '2017-01-04', '2017-01-01', '2017-01-02',
                 '2017-01-01', '2017-01-02', '2017-01-03', '2017-01-01',
                 '2017-01-02', '2017-01-03', '2017-01-04', '2017-01-05',
                 '2017-01-06', '2017-01-07', '2017-01-08']),
             'sales': [1, 1, 1, 2, 2, 6, 7, 7, 10, 11, 15, 13, 14,
                       14.333333, 14.666667, 15],
             'price': [np.nan, np.nan, 3, np.nan, 4, 3, 6, np.nan, 2, 6, 3, 5, 5,
                       np.nan, np.nan, 6]})
        expected_output = TimeSeriesDataFrame(expected_data, grain_colnames=['store'],
                                              time_colname='date', ts_value_colname='sales')
        assert_frame_equal(self.transform2.sort_index(),
                           expected_output.sort_index())

    def test_impute_single_value_explicit(self):
        """
        This method tests imputing a single value for single column 'sales' with all arguments
        explicitly stated.
        """
        self.imputer3 = TimeSeriesImputer(input_column='sales',
                                          option='interpolate', method='linear',
                                          limit_direction='both')
        self.transform3 = self.imputer3.transform(TestTSImputer.df1)
        expected_data = pd.DataFrame(
            {'store': ['a', 'a', 'a', 'b', 'b', 'c', 'c', 'c', 'd',
                       'd', 'd', 'd', 'd', 'd', 'd', 'd'],
             'date': pd.to_datetime(
                ['2017-01-02', '2017-01-03', '2017-01-04', '2017-01-01', '2017-01-02',
                 '2017-01-01', '2017-01-02', '2017-01-03', '2017-01-01',
                 '2017-01-02', '2017-01-03', '2017-01-04', '2017-01-05',
                 '2017-01-06', '2017-01-07', '2017-01-08']),
             'sales': [1, 1, 1, 2, 2, 6, 7, 7, 10, 11, 15, 13, 14,
                       14.333333, 14.666667, 15],
             'price': [np.nan, np.nan, 3, np.nan, 4, 3, 6, np.nan, 2, 6, 3, 5, 5,
                       np.nan, np.nan, 6]})
        expected_output = TimeSeriesDataFrame(expected_data, grain_colnames=['store'],
                                              time_colname='date', ts_value_colname='sales')
        assert_frame_equal(self.transform3.sort_index(),
                           expected_output.sort_index())

    def test_impute_list(self):
        """
        This method tests imputing multiple value columns
        """
        self.imputer4 = TimeSeriesImputer(input_column=['sales', 'price'],
                                          option='interpolate',
                                          method='linear',
                                          limit_direction='both')
        self.transform4 = self.imputer4.transform(TestTSImputer.df1)
        expected_data = pd.DataFrame(
            {'store': ['a', 'a', 'a', 'b', 'b', 'c', 'c', 'c', 'd',
                       'd', 'd', 'd', 'd', 'd', 'd', 'd'],
             'date': pd.to_datetime(
                ['2017-01-02', '2017-01-03', '2017-01-04', '2017-01-01', '2017-01-02',
                 '2017-01-01', '2017-01-02', '2017-01-03', '2017-01-01',
                 '2017-01-02', '2017-01-03', '2017-01-04', '2017-01-05',
                 '2017-01-06', '2017-01-07', '2017-01-08']),
             'sales': [1, 1, 1, 2, 2, 6, 7, 7, 10, 11, 15, 13, 14,
                       14.333333, 14.666667, 15],
             'price': [3, 3, 3, 4, 4, 3, 6, 6, 2, 6, 3, 5, 5,
                       5.333333, 5.666667, 6]})
        expected_output = TimeSeriesDataFrame(expected_data, grain_colnames=['store'],
                                              time_colname='date', ts_value_colname='sales')
        if pd.__version__ >= '0.20.2':
            assert_frame_equal(self.transform4.sort_index(),
                               expected_output.sort_index())

    def test_impute_method(self):
        """
        This method tests imputing with method specified
        """
        self.imputer5 = TimeSeriesImputer(input_column=['sales'],
                                          option='interpolate', method='barycentric')
        self.transform5 = self.imputer5.transform(TestTSImputer.df1)
        expected_data = pd.DataFrame(
            {'store': ['a', 'a', 'a', 'b', 'b', 'c', 'c', 'c', 'd',
                       'd', 'd', 'd', 'd', 'd', 'd', 'd'],
             'date': pd.to_datetime(
                ['2017-01-02', '2017-01-03', '2017-01-04', '2017-01-01', '2017-01-02',
                 '2017-01-01', '2017-01-02', '2017-01-03', '2017-01-01',
                 '2017-01-02', '2017-01-03', '2017-01-04', '2017-01-05',
                 '2017-01-06', '2017-01-07', '2017-01-08']),
             'sales': [1, 1, 1, 2, 2, 6, 7, 8, 10, 11, 15, 13, 14,
                       26.904762, 42.428571, 15],
             'price': [np.nan, np.nan, 3, np.nan, 4, 3, 6, np.nan, 2, 6, 3, 5, 5,
                       np.nan, np.nan, 6]})
        expected_output = TimeSeriesDataFrame(expected_data, grain_colnames=['store'],
                                              time_colname='date', ts_value_colname='sales')
        assert_frame_equal(self.transform5.sort_index(),
                           expected_output.sort_index())

    def test_impute_fill(self):
        """
        This method tests imputing with fill forward specified
        """
        self.imputer6 = TimeSeriesImputer(input_column=['sales'], option='fillna',
                                          method='ffill')
        self.transform6 = self.imputer6.transform(TestTSImputer.df1)
        expected_data = pd.DataFrame(
            {'store': ['a', 'a', 'a', 'b', 'b', 'c', 'c', 'c', 'd',
                       'd', 'd', 'd', 'd', 'd', 'd', 'd'],
             'date': pd.to_datetime(
                ['2017-01-02', '2017-01-03', '2017-01-04', '2017-01-01', '2017-01-02',
                 '2017-01-01', '2017-01-02', '2017-01-03', '2017-01-01',
                 '2017-01-02', '2017-01-03', '2017-01-04', '2017-01-05',
                 '2017-01-06', '2017-01-07', '2017-01-08']),
             'sales': [1., 1, 1, 2, 2, 6, 7, 7, 10, 11, 15, 13, 14,
                       14, 14, 15],
             'price': [np.nan, np.nan, 3, np.nan, 4, 3, 6, np.nan, 2, 6, 3, 5, 5,
                       np.nan, np.nan, 6]})
        expected_output = TimeSeriesDataFrame(expected_data, grain_colnames=['store'],
                                              time_colname='date', ts_value_colname='sales')
        assert_frame_equal(self.transform6.sort_index(),
                           expected_output.sort_index())

    def test_impute_fill_zero(self):
        """
        This method tests imputing with fill specified
        """
        self.imputer7 = TimeSeriesImputer(input_column=['sales'], option='fillna',
                                          value=0)
        self.transform7 = self.imputer7.transform(TestTSImputer.df1)
        expected_data = pd.DataFrame(
            {'store': ['a', 'a', 'a', 'b', 'b', 'c', 'c', 'c', 'd',
                       'd', 'd', 'd', 'd', 'd', 'd', 'd'],
             'date': pd.to_datetime(
                ['2017-01-02', '2017-01-03', '2017-01-04', '2017-01-01', '2017-01-02',
                 '2017-01-01', '2017-01-02', '2017-01-03', '2017-01-01',
                 '2017-01-02', '2017-01-03', '2017-01-04', '2017-01-05',
                 '2017-01-06', '2017-01-07', '2017-01-08']),
             'sales': [1., 0, 0, 2, 0, 6, 7, 0, 10, 11, 15, 13, 14,
                       0, 0, 15],
             'price': [np.nan, np.nan, 3, np.nan, 4, 3, 6, np.nan, 2, 6, 3, 5, 5,
                       np.nan, np.nan, 6]})
        expected_output = TimeSeriesDataFrame(expected_data, grain_colnames=['store'],
                                              time_colname='date', ts_value_colname='sales')
        assert_frame_equal(self.transform7.sort_index(),
                           expected_output.sort_index())

    def test_impute_extend_forward(self):
        """
        This method tests extending data from a specified date
        """
        self.imputer8 = TimeSeriesImputer(input_column=['sales'], option='fillna',
                                          value=0, origin='2016-12-28')
        self.transform8 = self.imputer8.transform(TestTSImputer.df1)
        expected_data = pd.DataFrame(
            {'store': ['a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'b', 'b', 'b', 'b', 'b', 'b',
                       'c', 'c', 'c', 'c', 'c', 'c', 'c', 'd', 'd', 'd', 'd', 'd', 'd',
                       'd', 'd', 'd', 'd', 'd', 'd'],
             'date': pd.to_datetime(
                ['2016-12-28', '2016-12-29', '2016-12-30', '2016-12-31', '2017-01-01',
                 '2017-01-02', '2017-01-03', '2017-01-04', '2016-12-28',
                 '2016-12-29', '2016-12-30', '2016-12-31', '2017-01-01', '2017-01-02',
                 '2016-12-28', '2016-12-29', '2016-12-30', '2016-12-31',
                 '2017-01-01', '2017-01-02', '2017-01-03', '2016-12-28',
                 '2016-12-29', '2016-12-30', '2016-12-31', '2017-01-01',
                 '2017-01-02', '2017-01-03', '2017-01-04', '2017-01-05',
                 '2017-01-06', '2017-01-07', '2017-01-08']),
             'sales': [0, 0, 0, 0, 0, 1., 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 6, 7, 0, 0,
                       0, 0, 0, 10, 11, 15, 13, 14, 0, 0, 15],
             'price': [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 3, np.nan,
                       np.nan, np.nan, np.nan, np.nan, 4, np.nan, np.nan,
                       np.nan, np.nan, 3, 6, np.nan, np.nan, np.nan,
                       np.nan, np.nan, 2, 6, 3, 5, 5, np.nan, np.nan, 6]})
        expected_output = TimeSeriesDataFrame(expected_data, grain_colnames=['store'],
                                              time_colname='date', ts_value_colname='sales')
        assert_frame_equal(self.transform8.sort_index(),
                           expected_output.sort_index())

    def test_impute_extend_backwards(self):
        """
        This method tests extending data to a specified date
        """
        self.imputer9 = TimeSeriesImputer(input_column=['sales'], option='fillna',
                                          value=0, end='2017-01-10')
        self.transform9 = self.imputer9.transform(TestTSImputer.df1)
        expected_data = pd.DataFrame(
            {'store': ['a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'b',
                       'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'c',
                       'c', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'd',
                       'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd', 'd'],
             'date': pd.to_datetime(
                ['2017-01-02', '2017-01-03', '2017-01-04', '2017-01-05',
                 '2017-01-06', '2017-01-07', '2017-01-08', '2017-01-09',
                 '2017-01-10', '2017-01-01', '2017-01-02', '2017-01-03',
                 '2017-01-04', '2017-01-05', '2017-01-06', '2017-01-07',
                 '2017-01-08', '2017-01-09', '2017-01-10', '2017-01-01',
                 '2017-01-02', '2017-01-03', '2017-01-04', '2017-01-05',
                 '2017-01-06', '2017-01-07', '2017-01-08', '2017-01-09',
                 '2017-01-10', '2017-01-01', '2017-01-02', '2017-01-03',
                 '2017-01-04', '2017-01-05', '2017-01-06', '2017-01-07',
                 '2017-01-08', '2017-01-09', '2017-01-10']),
             'sales': [1., 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 7, 0, 0,
                       0, 0, 0, 0, 0, 0, 10, 11, 15, 13, 14, 0, 0, 15, 0, 0],
             'price': [np.nan, np.nan, 3, np.nan, np.nan, np.nan, np.nan,
                       np.nan, np.nan, np.nan, 4, np.nan, np.nan, np.nan, np.nan,
                       np.nan, np.nan, np.nan, np.nan, 3, 6, np.nan, np.nan, np.nan, np.nan,
                       np.nan, np.nan, np.nan, np.nan, 2, 6, 3, 5, 5,
                       np.nan, np.nan, 6, np.nan, np.nan]})
        expected_output = TimeSeriesDataFrame(expected_data, grain_colnames=['store'],
                                              time_colname='date', ts_value_colname='sales')
        assert_frame_equal(self.transform9.sort_index(),
                           expected_output.sort_index())

    def test_impute_no_grain(self):
        """
        Test that imputation works when the grain isn't set
        """

        # Make an imputer that fills NAs with zeros (at daily frequency)
        imputer = TimeSeriesImputer(input_column=['sales'], option='fillna',
                                    freq='D', value=0.0)

        # Make a single series tsdf with no grain set
        dat = pd.DataFrame({'date': pd.to_datetime(['2017-01-02', '2017-01-04']),
                            'sales': [1., np.nan],
                            'price': [np.nan, 3.]})

        tsdf = TimeSeriesDataFrame(dat, time_colname='date',
                                   ts_value_colname='sales')

        tsdf_xformed = imputer.transform(tsdf)

        # Make expected output
        dat_expected = pd.DataFrame({'date': pd.to_datetime(['2017-01-02',
                                                             '2017-01-03',
                                                             '2017-01-04']),
                                     'sales': [1., 0., 0.],
                                     'price': [np.nan, np.nan, 3.]})

        tsdf_expected = TimeSeriesDataFrame(dat_expected,
                                            time_colname='date',
                                            ts_value_colname='sales')

        # Test equality
        assert_frame_equal(tsdf_xformed, tsdf_expected)

    def test_impute_period(self):
        """
        This method tests extending data to a specified date
        """
        data2 = pd.DataFrame(
            {'store': ['a', 'a', 'a', 'b', 'b'],
             'brand': ['a', 'a', 'a', 'b', 'b'],
             'date': pd.PeriodIndex(
                ['2011-12', '2012-02', '2012-03', '2012-02', '2012-03'],
                dtype='period[M]', freq='M'),
             'sales': [1, np.nan, 5, 2, np.nan],
             'price': [np.nan, 2, 3, np.nan, 4]})
        df2 = TimeSeriesDataFrame(data2, grain_colnames=['store', 'brand'],
                                  time_colname='date', ts_value_colname='sales')
        self.imputer10 = TimeSeriesImputer(input_column=['sales'],
                                           option='fillna', value=0)
        if pd.__version__ >= '0.20.0':
            self.transform10 = self.imputer10.transform(df2)
            expected_data = pd.DataFrame(
                {'store': ['a', 'a', 'a', 'a', 'b', 'b'],
                 'brand': ['a', 'a', 'a', 'a', 'b', 'b'],
                 'date': pd.PeriodIndex(
                    ['2011-12', '2012-01', '2012-02', '2012-03', '2012-02', '2012-03'],
                    dtype='period[M]', freq='M'),
                 'sales': [1, 0, 0, 5, 2, 0],
                 'price': [np.nan, np.nan, 2, 3, np.nan, 4]})
            expected_output = TimeSeriesDataFrame(expected_data,
                                                  grain_colnames=['store', 'brand'],
                                                  time_colname='date', ts_value_colname='sales')
            expected_output['sales'] = expected_output['sales'].astype('float')
            assert_frame_equal(self.transform10.sort_index(),
                               expected_output.sort_index())

    def test_impute_pipeline(self):
        """
        This method tests imputing a single column 'sales' in a pipeline with option 'default'
        """
        pipeline_ml = AzureMLForecastPipeline(
            steps=[('impute_values', TimeSeriesImputer(
                input_column='sales', option='interpolate', method='linear'))])
        self.transform1 = pipeline_ml.fit_transform(TestTSImputer.df1)
        expected_data = pd.DataFrame(
            {'store': ['a', 'a', 'a', 'b', 'b', 'c', 'c', 'c', 'd',
                       'd', 'd', 'd', 'd', 'd', 'd', 'd'],
             'date': pd.to_datetime(
                ['2017-01-02', '2017-01-03', '2017-01-04', '2017-01-01', '2017-01-02',
                 '2017-01-01', '2017-01-02', '2017-01-03', '2017-01-01',
                 '2017-01-02', '2017-01-03', '2017-01-04', '2017-01-05',
                 '2017-01-06', '2017-01-07', '2017-01-08']),
             'sales': [1, 1, 1, 2, 2, 6, 7, 7, 10, 11, 15, 13, 14,
                       14.333333, 14.666667, 15],
             'price': [np.nan, np.nan, 3, np.nan, 4, 3, 6, np.nan, 2, 6, 3, 5, 5,
                       np.nan, np.nan, 6]})
        expected_output = TimeSeriesDataFrame(expected_data, grain_colnames=['store'],
                                              time_colname='date', ts_value_colname='sales')
        assert_frame_equal(self.transform1.sort_index(),
                           expected_output.sort_index())

    def test_impute_dict_input_option_fillna(self):
        """
        Test the TimeSeriesImputer work properly when receiving a dictionary
        input in keyword argument value with option='fillna'
        """
        datetime_input = pd.DatetimeIndex(
            ['2018-03-16', '2018-03-19', '2018-03-20',
             '2018-03-16', '2018-03-19'])
        df = pd.DataFrame({'Store': [1, 1, 1, 2, 2],
                           'Datetime': datetime_input,
                           'Sales': [0, np.nan, 2, 3, 4],
                           'Price': [0, 1, 2, 3, np.nan],
                           'feature1': [0, 1, 2, 3, np.nan]})

        tsdf = TimeSeriesDataFrame(df, time_colname='Datetime',
                                   grain_colnames='Store',
                                   ts_value_colname='Sales')
        imputer = TimeSeriesImputer(input_column=['Sales', 'Price'],
                                    option='fillna',
                                    value={'Sales': 199, 'Price': -199},
                                    freq='B')
        imputed_ts = imputer.transform(tsdf)

        tsdf = tsdf.sort_index()
        imputed_ts = imputed_ts.sort_index()

        # test whether the na value is imiputed properly
        self.assertTrue(imputed_ts['Sales'].loc[tsdf.index[tsdf['Sales'].isnull(
        )]].values[0] == 199)
        self.assertTrue(imputed_ts['Price'].loc[tsdf.index[tsdf['Price'].isnull(
        )]].values[0] == -199)

        # columns not in input column should not be imputed
        self.assertTrue(pd.isnull(imputed_ts['feature1'].loc[tsdf.index[tsdf[
            'Price'].isnull()]].values[0]))

    def test_imputation_origin_time(self):
        """
        Test TimeSeriesImputer on data with origin_time.
        """
        df_with_origin_tsdf = TimeSeriesDataFrame(
            TestTSImputer.df_with_origin, time_colname='Date',
            grain_colnames='Store',
            origin_time_colname='Origin_Date')

        ts_imputer1 = TimeSeriesImputer(
            input_column=['Order_Number', 'Sales', 'Random_Var'],
            option='interpolate', method='linear')
        ts_imputer1_transform = ts_imputer1.fit(df_with_origin_tsdf).transform(
            df_with_origin_tsdf)

        expected_df = pd.DataFrame({
            'Store': ['a'] * 8,
            'Date': pd.DatetimeIndex(['2017-01-08', '2017-01-15',
                                      '2017-01-15', '2017-01-22',
                                      '2017-01-29', '2017-01-22',
                                      '2017-01-29', '2017-02-05']),
            'Origin_Date': pd.DatetimeIndex(['2017-01-01', '2017-01-01',
                                             '2017-01-08', '2017-01-08',
                                             '2017-01-08', '2017-01-15',
                                             '2017-01-15', '2017-01-15']),
            'Order_Number': [1, 1, 3, 3, 3, 5, 5, 5],
            'Sales': [1, 2, 2, 3, 4, 3, 4, 5],
            'Random_Var': [4, 4, 2, 3, 4, 5, 6, 6]
        })

        expected_tsdf = TimeSeriesDataFrame(
            expected_df, time_colname='Date', grain_colnames='Store',
            origin_time_colname='Origin_Date')
        self.assertTrue(ts_imputer1_transform.equals(expected_tsdf))

        # test no grain
        df_with_origin_tsdf_no_grain = df_with_origin_tsdf.reset_index(
            level='Store', drop=True)
        ts_imputer1_transform_no_grain = ts_imputer1.fit(
            df_with_origin_tsdf_no_grain).transform(
            df_with_origin_tsdf_no_grain)
        expected_tsdf_no_grain = expected_tsdf.reset_index(
            level='Store', drop=True)
        expected_tsdf_no_grain.group_colnames = None
        self.assertTrue(ts_imputer1_transform_no_grain.equals(
            expected_tsdf_no_grain))

    def test_imputation_origin_time_impute_by_horizon(self):
        """
        Test TimeSeriesImputer on data with origin_time with
        impute_by_horizon as True.
        """
        df_with_origin_tsdf = TimeSeriesDataFrame(
            TestTSImputer.df_with_origin, time_colname='Date',
            grain_colnames='Store',
            origin_time_colname='Origin_Date')

        ts_imputer1 = TimeSeriesImputer(
            input_column=['Order_Number', 'Sales', 'Random_Var'],
            option='interpolate', method='linear', impute_by_horizon=True)
        ts_imputer1_transform = ts_imputer1.fit(df_with_origin_tsdf).transform(
            df_with_origin_tsdf)

        expected_df = pd.DataFrame({
            'Store': ['a'] * 8,
            'Date': pd.DatetimeIndex(['2017-01-08', '2017-01-15',
                                      '2017-01-15', '2017-01-22',
                                      '2017-01-29', '2017-01-22',
                                      '2017-01-29', '2017-02-05']),
            'Origin_Date': pd.DatetimeIndex(['2017-01-01', '2017-01-01',
                                             '2017-01-08', '2017-01-08',
                                             '2017-01-08', '2017-01-15',
                                             '2017-01-15', '2017-01-15']),
            'Order_Number': [1, 1, 3, 3, 3, 5, 5, 5],
            'Sales': [1, 2, 2, 3, 4, 3, 4, 5],
            'Random_Var': [4, np.nan, 2, np.nan, 4, 5, 6, 4]
        })

        expected_tsdf = TimeSeriesDataFrame(
            expected_df, time_colname='Date', grain_colnames='Store',
            origin_time_colname='Origin_Date')
        self.assertTrue(ts_imputer1_transform[expected_tsdf.columns].equals(
            expected_tsdf))


if __name__ == '__main__':
    unittest.main()
