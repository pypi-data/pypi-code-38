import datetime
import inspect
import numpy as np
import os
import pandas as pd
import unittest
import warnings

from itertools import product
from math import ceil
from numpy.ma.testutils import assert_array_equal
from pandas.tseries.frequencies import to_offset
from pandas.util.testing import assert_frame_equal, assert_series_equal, assert_index_equal
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from azureml.automl.core.featurizer.transformer.timeseries.stl_featurizer import STLFeaturizer
from automl.client.core.common.forecasting_ts_utils import get_stl_decomposition
from automl.client.core.common.constants import TimeSeriesInternal
from automl.client.core.common.exceptions import DataException, ConfigException, ClientException
from automl.client.core.common.forecasting_exception import NotSupportedException
from automl.client.core.common.time_series_data_frame import TimeSeriesDataFrame

from ... import utilities

from ...test_data.dow_jones.load_dow_jones_data import load_dow_jones_dataset
from pandas.tests.util.test_testing import TestAssertFrameEqual


class TestFTKSTLFeaturizer(unittest.TestCase):
    """Test STL Decomposition"""

    train = None
    test = None

    @staticmethod
    def get_train_test():
        """Return train and test data sets."""
        if TestFTKSTLFeaturizer.test is None:
            TestFTKSTLFeaturizer.train, TestFTKSTLFeaturizer.test = load_dow_jones_dataset()
            TestFTKSTLFeaturizer.train =\
                TestFTKSTLFeaturizer.train[TestFTKSTLFeaturizer.train.grain_index.isin(['AAPL', 'MSFT'])]
            TestFTKSTLFeaturizer.test =\
                TestFTKSTLFeaturizer.test[TestFTKSTLFeaturizer.test.grain_index.isin(['AAPL', 'MSFT'])]
        return TestFTKSTLFeaturizer.train, TestFTKSTLFeaturizer.test

    def test_stl_featurizer(self):
        """Test that featurizer returns expected data and seasonality is set."""
        train_df, _ = TestFTKSTLFeaturizer.get_train_test()
        featurizer = STLFeaturizer(seasonality=4)
        result = featurizer.fit_transform(train_df)

        # Make sure the result has the same rows
        assert_index_equal(train_df.sort_index().index, result.sort_index().index)

        # Check that trend and season columns were made and have valid values
        self.assertIn('revenue_season', result.columns)
        self.assertIn('revenue_trend', result.columns)
        self.assertFalse(any(pd.isna(result.revenue_season)))
        self.assertFalse(any(pd.isna(result.revenue_trend)))

    def test_stl_featurizer_no_trend_feature(self):
        """Test that featurizer returns expected data and seasonality is set."""
        train_df, test_df = TestFTKSTLFeaturizer.get_train_test()
        featurizer = STLFeaturizer(seasonal_feature_only=True, seasonality=4)
        result = featurizer.fit_transform(train_df)

        # Make sure the result has the same rows
        assert_index_equal(train_df.sort_index().index, result.sort_index().index)

        # Check that trend and season columns were made and have valid values
        self.assertIn('revenue_season', result.columns)
        self.assertNotIn('revenue_trend', result.columns)
        self.assertFalse(any(pd.isna(result.revenue_season)))

        result_test = featurizer.transform(test_df)
        self.assertIn('revenue_season', result_test.columns)
        self.assertNotIn('revenue_trend', result_test.columns)
        self.assertFalse(any(pd.isna(result_test.revenue_season)))

    def test_set_seasonality_2(self):
        """Another test for fixed seasonality."""
        train_df, _ = TestFTKSTLFeaturizer.get_train_test()
        featurizer = STLFeaturizer(seasonality=3)
        result = featurizer.fit_transform(train_df)
        self.check_seasonality(result, 3)

    def test_infer_seasonality(self):
        """Test if seasonality is inferred correctly."""
        featurizer = STLFeaturizer()
        train_df = utilities.get_dataset('ausbeer')
        train_df = train_df.assign(grain='ausbeer_grain')
        train_df2 = utilities.get_dataset('a10')
        train_df2_1 = train_df2.assign(grain='a10_1')
        train_df2_2 = train_df2.assign(grain='a10_2')
        ausbeer_tsdf = TimeSeriesDataFrame(train_df, time_colname='date',
                                           grain_colnames=['grain'],
                                           ts_value_colname='quantity')
        featurizer.fit(ausbeer_tsdf)
        self.assertEqual(featurizer.seasonality, 4, "The seasonality is incorrect.")
        # To create two different seasonality we need to make fake index for train_df
        # It needs to be monthly, because otherwise imputer will fix the frequency and
        # warning will not be thrown.
        train_df['date'] = pd.date_range('1956-01-01', freq='MS', periods=train_df.shape[0])
        # Check if multiple seasonality are inferred correctly.
        mul_df = pd.concat([train_df2_1, train_df, train_df2_2])
        mul_tsdf = TimeSeriesDataFrame(mul_df, time_colname='date',
                                       grain_colnames=['grain'],
                                       ts_value_colname='quantity')
        featurizer._seasonality = -1

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            featurizer.fit(mul_tsdf)
            # in case there are more than one warnings thrown, we only
            # examine whether there is one of the warnings exactly from the
            # stl featurizer and is user warning.
            self.assertTrue(
                any(['Different grains have different seasonality' in str(wi.message)
                     for wi in w]))
        self.assertEqual(featurizer.seasonality, 12, "The seasonality is incorrect.")
        featurizer.fit(ausbeer_tsdf)
        # Now the seasonality should not be set because it was set in previous test.
        self.assertEqual(featurizer.seasonality, 12, "The seasonality is incorrect.")

    def test_raises(self):
        """Test that if transformer is not fitted the error will be raised."""
        train_df, _ = TestFTKSTLFeaturizer.get_train_test()
        featurizer = STLFeaturizer()
        with self.assertRaises(ClientException):
            featurizer.transform(train_df)

    def test_short_frame(self):
        """Test if attempt to get seasonality from one value raises exception."""
        featurizer = STLFeaturizer()
        data = {
            'date': ['2001-01-01', '2001-01-01', '2001-01-02',
                     '2001-01-03', '2001-01-04', '2001-01-05',
                     '2001-01-06'],
            'grains': ['test1', 'test2', 'test2', 'test2', 'test2', 'test2', 'test2'],
            'sales': np.repeat(42, 7)
        }
        tsdf_invalid = TimeSeriesDataFrame(data, time_colname='date',
                                           grain_colnames=['grains'],
                                           ts_value_colname='sales')
        with self.assertRaises(DataException):
            featurizer.fit(tsdf_invalid)

    def test_transform(self):
        """
        Check that fit_transform returns the same seasonality
        as transform.
        """
        train_df, _ = TestFTKSTLFeaturizer.get_train_test()
        featurizer = STLFeaturizer(seasonality=4)
        result = featurizer.fit_transform(train_df)
        result.sort_index(inplace=True)
        # To avoid warnings about 0 horizon create the new data frame.
        one_grain = train_df[train_df.grain_index.isin(['MSFT'])]
        period = one_grain.time_index.values[1] - one_grain.time_index.values[0]

        def move_dates(X):
            start = np.datetime64('2015-01-01')
            end = start + X.shape[0] * period
            data = {
                'quarter_start': pd.date_range(start, end, freq='QS'),
                'company_ticker': X.grain_index.values,
                'revenue': X.ts_value.values
            }
            return TimeSeriesDataFrame(data, time_colname='quarter_start',
                                       grain_colnames=['company_ticker'],
                                       ts_value_colname='revenue')
        rpl_dict = []
        for grain in train_df.groupby_grain():
            rpl_dict.append(move_dates(grain[1]))
        replaced = pd.concat(rpl_dict)
        result_new_dates = featurizer.transform(replaced)
        result_new_dates.sort_index(inplace=True)
        assert_array_equal(
            result['revenue_season'].values,
            result_new_dates['revenue_season'].values,
            "Seasonalities should be equal.")

    def test_artifical_data(self):
        """Test STL decomposition on the artificial data."""
        data_train = {
            'date': pd.date_range('1969-01-01', '1983-01-01', freq='YS'),
            'grain': np.repeat('some_grain', 15),
            'sketch': np.repeat(np.NaN, 15),
        }
        df_train = pd.DataFrame(data_train)
        # Let seasonality will be two and it will be a sequence (-1.5, 1.5)
        df_train['sketch'] = df_train.index.values * 2 + 3 * (df_train.index.values % 2)
        tsdf_train = TimeSeriesDataFrame(df_train, time_colname='date',
                                         grain_colnames='grain',
                                         ts_value_colname='sketch')

        data_test = {
            'date': pd.date_range('1998-01-01', '1999-01-01', freq='YS'),
            'grain': np.repeat('some_grain', 2),
            'sketch': np.repeat(np.NaN, 2),
        }
        tsdf_test = TimeSeriesDataFrame(data_test, time_colname='date',
                                        grain_colnames='grain',
                                        ts_value_colname='sketch')
        featurizer = STLFeaturizer()
        tsdf_trans = featurizer.fit_transform(tsdf_train)
        result = featurizer.transform(tsdf_test)

        # Check that the trend was extrapolated by transform
        # The test data trend should be strictly greater than the final train value
        latest_train_trend = tsdf_trans.sort_values(by=['date']).sketch_trend[-1]
        self.assertTrue(all(result.sketch_trend > latest_train_trend))

        # Ensure that the correct seasonality was inferred
        self.assertEqual(featurizer.seasonality, 2)

    def test_short_artifical_data(self):
        """Test if short artificial data raise """
        data_train = {
            'date': pd.date_range('1969-01-01', '1970-01-01', freq='YS'),
            'grain': np.repeat('some_grain', 2),
            'sketch': [0, 3],
        }
        tsdf_train = TimeSeriesDataFrame(data_train, time_colname='date',
                                         grain_colnames='grain',
                                         ts_value_colname='sketch')
        featurizer = STLFeaturizer(seasonality=2)
        with self.assertRaises(DataException):
            featurizer.fit(tsdf_train)

    def test_wrong_data_type(self):
        """Test if seasonality is integer"""
        with self.assertRaises(ConfigException):
            STLFeaturizer(seasonality='QS')

    def test_no_trend_model(self):
        """Artificially set model to None."""
        train_df, test_df = TestFTKSTLFeaturizer.get_train_test()
        featurizer = STLFeaturizer(seasonality=4)
        featurizer.fit(train_df)
        for k in featurizer._es_models.keys():
            featurizer._es_models[k] = None
        featurizer._trend_model = None
        result = featurizer.transform(test_df)
        self.assertTrue(all([np.isnan(trend) for trend in result['revenue_trend'].values]),
                        'STL generated trend with no model.')

    def test_generate_df(self):
        """Test our utility finction to generate trended data frames."""
        X_train, y_train, X_test, y_test = get_seasonal_trended_data(grains_per_col=2, seasonality=3)
        df_expected_test = pd.DataFrame({
            'date': list(pd.date_range('2000-01-01', periods=12, freq='D')) * 2,
            'grain': np.repeat(['grain_0', 'grain_1'], 12)
        })
        assert_frame_equal(df_expected_test, X_train, check_like=True)
        y_exp = np.array([1, 4, 7, 7, 10, 13, 13, 16, 19, 19, 22, 25,
                          2, 5, 8, 8, 11, 14, 14, 17, 20, 20, 23, 26])
        assert_array_equal(y_exp, y_train, "y_train are not equal.")
        # Check the test.
        df_expected_test = pd.DataFrame({
            'date': list(pd.date_range('2000-01-13', periods=6, freq='D')) * 2,
            'grain': np.repeat(['grain_0', 'grain_1'], 6)
        })
        assert_frame_equal(df_expected_test, X_test, check_like=True)
        y_exp = np.array([25, 28, 31, 31, 34, 37,
                          26, 29, 32, 32, 35, 38])
        assert_array_equal(y_exp, y_test, "y_train are not equal.")
        # Check multiple grain columns with different periodicity.
        X_train, y_train, _, _ = get_seasonal_trended_data(train_len=6,
                                                           test_len=2,
                                                           grain_columns=['a', 'b'],
                                                           grains_per_col=2,
                                                           seasonality=2,
                                                           freq='W')
        df_expected_test = pd.DataFrame({
            'date': list(pd.date_range('2000-01-01', periods=6, freq='W')) * 4,
            'a': np.repeat(['a_0', 'a_1'], 12),
            'b': np.repeat(['b_0', 'b_1'] * 2, 6)
        })
        assert_frame_equal(df_expected_test, X_train, check_like=True)
        y_exp = np.array([1, 4, 5, 8, 9, 12,
                          2, 5, 6, 9, 10, 13,
                          3, 6, 7, 10, 11, 14,
                          4, 7, 8, 11, 12, 15])
        assert_array_equal(y_exp, y_train, "y_train are not equal.")

    def test_stl_with_origin(self):
        """Test if the stl ignores the origin and featurizes the data frame."""
        X_train, y_train, X_test, y_test = get_seasonal_trended_data(
            grains_per_col=1,
            seasonality=3,
            freq="M")
        X_train['y'] = y_train
        X_train_2 = X_train.copy()
        X_train['origin'] = pd.date_range(start=X_train['date'].min() - to_offset('M'), periods=X_train.shape[0])
        X_train['horyzon'] = 0
        X_train_2['origin'] = pd.date_range(start=X_train['date'].min() - 2 * to_offset('M'), periods=X_train.shape[0])
        X_train_2['horyzon'] = 1
        X_train = pd.concat([X_train, X_train_2])
        tsdf_train = TimeSeriesDataFrame(X_train,
                                         time_colname='date',
                                         grain_colnames='grain',
                                         ts_value_colname='y',
                                         origin_time_colname='origin')
        X_test_2 = X_test.copy()
        X_test['origin'] = pd.date_range(start=X_test['date'].min() - to_offset('M'), periods=X_test.shape[0])
        X_test['horyzon'] = 0
        X_test_2['origin'] = pd.date_range(start=X_test['date'].min() - 2 * to_offset('M'), periods=X_test.shape[0])
        X_test_2['horyzon'] = 1
        X_test = pd.concat([X_test, X_test_2])
        # Note we have no y_test.
        stl = STLFeaturizer()
        with self.assertRaises(ClientException):
            stl.fit_transform(tsdf_train)

    def test_preview_columns(self):
        """Test if stl returns correct preview columns."""
        X_train, X_test = self._get_tsdfs(train_len=100,
                                          test_len=20,
                                          grain_columns=['grain'],
                                          grains_per_col=1,
                                          seasonality=2,
                                          freq='D')
        stl = STLFeaturizer()
        cols = stl.preview_column_names(X_train)
        expected = ['y' + TimeSeriesInternal.STL_SEASON_SUFFIX,
                    'y' + TimeSeriesInternal.STL_TREND_SUFFIX]
        self.assertEqual(cols, expected, 'Wrong column preview.')
        cols = stl.preview_column_names(tsdf=None, target='zzz')
        expected = ['zzz' + TimeSeriesInternal.STL_SEASON_SUFFIX,
                    'zzz' + TimeSeriesInternal.STL_TREND_SUFFIX]
        self.assertEqual(cols, expected, 'Wrong column preview.')

    def test_preview_column_raises(self):
        """Test if erroneous inpyt raises an error."""
        """Test if stl returns correct preview columns."""
        X_train, X_test = self._get_tsdfs(train_len=100,
                                          test_len=20,
                                          grain_columns=['grain'],
                                          grains_per_col=1,
                                          seasonality=2,
                                          freq='D')
        stl = STLFeaturizer()
        with self.assertRaises(DataException):
            stl.preview_column_names(X_train, target='zzz')
        with self.assertRaises(DataException):
            stl.preview_column_names(tsdf=None, target=None)

    def test_multi_column_grains(self):
        """Test on data frame with multiple grain columns."""
        X_train, X_test = self._get_tsdfs(train_len=100,
                                          test_len=20,
                                          grain_columns=['a', 'b'],
                                          grains_per_col=2,
                                          seasonality=5,
                                          freq='B')
        stl = STLFeaturizer()
        X_multi_ft = stl.fit_transform(X_train)
        X_multi_t = stl.transform(X_test)
        for grain, one_train in X_train.groupby_grain():
            one_test = X_test.subset_by_grains([grain])
            X_ft = X_multi_ft.subset_by_grains([grain])
            X_t = X_multi_t.subset_by_grains([grain])
            self._do_one_grain(one_train, one_test,
                               X_ft, X_t,
                               5,
                               'additive')

    def test_multiple_grains(self):
        """Test stl on multiple grains."""
        X_train, X_test = self._get_tsdfs(train_len=100,
                                          test_len=20,
                                          grain_columns=['grain'],
                                          grains_per_col=2,
                                          seasonality=7,
                                          freq='Q')
        stl = STLFeaturizer()
        X_multi_ft = stl.fit_transform(X_train)
        X_multi_t = stl.transform(X_test)
        for grain, one_train in X_train.groupby_grain():
            one_test = X_test.subset_by_grains(grain)
            X_ft = X_multi_ft.subset_by_grains(grain)
            X_t = X_multi_t.subset_by_grains(grain)
            self._do_one_grain(one_train, one_test,
                               X_ft, X_t,
                               7,
                               'additive')

    def test_ano_ts_value(self):
        """Test if the absence of target column imposes problem."""
        X_train, X_test = self._get_tsdfs(train_len=100,
                                          test_len=20,
                                          grain_columns=['grain'],
                                          grains_per_col=1,
                                          seasonality=12,
                                          freq='M')
        X_train['something'] = 42
        X_test['something'] = 42
        X_test.ts_value_column_name = None
        X_test.drop('y', inplace=True, axis=1)
        stl = STLFeaturizer()
        X_ft = stl.fit_transform(X_train)
        X_train.ts_value_column_name = None
        X_train.drop('y', inplace=True, axis=1)
        X_tt = stl.transform(X_train)
        assert_array_equal(X_tt['y_season'], X_ft['y_season'], 'Transform and fit_transform are different.')
        assert_array_equal(X_tt['y_trend'], X_ft['y_trend'], 'Transform and fit_transform are different.')
        stl.transform(X_test)

    def test_one_grain(self):
        """Test if stl transform work for multiple conditions."""
        for frequency in ['H', 'D', 'W', 'M', 'Y']:
            for seasonality in [1, 2, 3, 4, 7]:
                X_train, X_test = self._get_tsdfs(train_len=100,
                                                  test_len=20,
                                                  grain_columns=['grain'],
                                                  grains_per_col=1,
                                                  seasonality=seasonality,
                                                  freq=frequency)
                stl = STLFeaturizer()
                X_ft = stl.fit_transform(X_train)
                self.assertEqual(stl.seasonality, seasonality, "The seasonality is incorrect.")
                X_t = stl.transform(X_test)
                self._do_one_grain(X_train, X_test,
                                   X_ft, X_t,
                                   seasonality)

    def test_raises_if_grain_not_fitted(self):
        """Test if error is raised if grain was not fitted."""
        X_train, X_test = self._get_tsdfs(train_len=100,
                                          test_len=20,
                                          grain_columns=['grain'],
                                          grains_per_col=1,
                                          seasonality=5,
                                          freq='D')
        stl = STLFeaturizer()
        stl.fit(X_train)
        X_train_2 = pd.DataFrame(X_train).reset_index(drop=False)
        X_train_2['grain'] = 'test'
        X_train_2 = TimeSeriesDataFrame(X_train_2,
                                        time_colname='date',
                                        grain_colnames='grain',
                                        ts_value_colname='y')
        with self.assertRaises(DataException):
            stl.transform(X_train_2)
        X_test_2 = pd.DataFrame(X_test).reset_index(drop=False)
        X_test_2['grain'] = 'test'
        X_test_2 = TimeSeriesDataFrame(X_test_2,
                                       time_colname='date',
                                       grain_colnames='grain',
                                       ts_value_colname='y')
        with self.assertRaises(DataException):
            stl.transform(X_test_2)

    def test_transform_on_training(self):
        """Test if transform on training set is treated as fit_transform."""
        X_train, X_test = self._get_tsdfs(train_len=100,
                                          test_len=20,
                                          grain_columns=['grain'],
                                          grains_per_col=2,
                                          seasonality=5,
                                          freq='D')
        stl = STLFeaturizer()
        X_ft = stl.fit_transform(X_train)
        X_t = stl.transform(X_train)
        assert_frame_equal(X_ft, X_t)
        X_t = stl.transform(X_train)
        # begin = 2000-01-01
        test = X_train[np.in1d(X_train.time_index,
                               pd.date_range(pd.Timestamp('2000-02-01'), pd.Timestamp('2000-02-29'), freq='D'))]
        expected = X_ft[np.in1d(X_ft.time_index,
                                pd.date_range(pd.Timestamp('2000-02-01'), pd.Timestamp('2000-02-29'), freq='D'))]
        expected.sort_index(inplace=True)
        X_t = stl.transform(test)
        X_t.sort_index(inplace=True)
        assert_frame_equal(expected, X_t)

    def test_overlap_train_test(self):
        """Test input between train and test."""
        X_train, X_test = self._get_tsdfs(train_len=60,
                                          test_len=31,
                                          grain_columns=['grain'],
                                          grains_per_col=2,
                                          seasonality=5,
                                          freq='D')
        stl = STLFeaturizer()
        X_ft = stl.fit_transform(X_train)
        X_t = stl.transform(X_test)
        # Create data setr containing part from train and part from test.
        part1 = X_train[np.in1d(X_train.time_index,
                                pd.date_range(pd.Timestamp('2000-02-01'), X_train.time_index.max(), freq='D'))]
        part2 = X_test[np.in1d(X_test.time_index,
                               pd.date_range(X_train.time_index.min(), pd.Timestamp('2000-03-15'), freq='D'))]
        test_ts = pd.concat([part1, part2])
        result = stl.transform(test_ts)
        exp1 = X_ft[np.in1d(X_ft.time_index,
                            pd.date_range(pd.Timestamp('2000-02-01'), X_ft.time_index.max(), freq='D'))]
        exp2 = X_t[np.in1d(X_t.time_index,
                           pd.date_range(X_t.time_index.min(), pd.Timestamp('2000-03-15'), freq='D'))]
        expected_ts = pd.concat([exp1, exp2])
        expected_ts.sort_index(inplace=True)
        assert_frame_equal(expected_ts, result)

    def test_early_date(self):
        """Test if trying to forecast at date earlier then in training set raises exception."""
        X_train, X_test = self._get_tsdfs(train_len=60,
                                          test_len=31,
                                          grain_columns=['grain'],
                                          grains_per_col=1,
                                          seasonality=5,
                                          freq='AS-JAN')
        stl = STLFeaturizer()
        stl.fit_transform(X_train)
        df = pd.DataFrame(X_test).reset_index(drop=False)
        df['date'] = pd.date_range(X_train.time_index.min() - 5 * to_offset('AS-JAN'),
                                   periods=df.shape[0],
                                   freq='AS-JAN')
        X_test = TimeSeriesDataFrame(df,
                                     time_colname='date',
                                     grain_colnames='grain',
                                     ts_value_colname='y')
        with self.assertRaises(DataException):
            stl.transform(X_test)

    def test_nans_at_y_begin(self):
        """Test nans at the begin of series."""
        self.do_test_nans_in_y(True, False, False)

    def test_nans_in_y_mid(self):
        """Test nans in the middle of series."""
        self.do_test_nans_in_y(False, True, False)

    def test_nans_in_y_end(self):
        """Test nans at the middle of series."""
        self.do_test_nans_in_y(False, False, True)

    def do_test_nans_in_y(self, begin=False, middle=False, end=False):
        """Test if stl works in presence of NaNs in y."""
        X_train, X_test = self._get_tsdfs(train_len=60,
                                          test_len=31,
                                          grain_columns=['grain'],
                                          grains_per_col=1,
                                          seasonality=5,
                                          freq='AS-JAN')
        stl = STLFeaturizer()
        y = X_train.ts_value.values.astype(float)
        if begin:
            y[0] = np.NaN
        if middle:
            y[30] = np.NaN
        if end:
            y[y.shape[0] - 1] = np.NaN
        X_train[X_train.ts_value_colname] = y
        X_before = X_train.copy()
        # Should not fail.
        stl.fit_transform(X_train)
        # Check that initial data frame was not modified.
        assert_frame_equal(X_before, X_train)
        self.assertEqual(stl.seasonality, 5, "Wrong inference of seasonality.")
        stl.transform(X_test)

    def test_target_imputation(self):
        """Test if imputation works as expected."""
        X_train, _ = self._get_tsdfs(train_len=60,
                                     test_len=31,
                                     grain_columns=['grain'],
                                     grains_per_col=3,
                                     seasonality=5,
                                     freq='AS-JAN')
        # Replace multiple values with nan to check how
        # imputation works. Also
        dfs = []
        for grain, X in X_train.groupby_grain():
            y = X.ts_value.values.astype(float)
            y[:10] = np.nan
            y[20:30] = np.nan
            y[50:] = np.nan
            X[X.ts_value_colname] = y
            dfs.append(X)
        X_train = pd.concat(dfs)
        stl = STLFeaturizer()
        stl.fit(X_train)
        tr = stl._get_imputed_df(X_train)
        # Check if the imputation is correct.
        for grain, X in tr.groupby_grain():
            y = X.ts_value.values
            self.assertTrue(all(val == 0 for val in y[:10]), "Wrong imputation at the beginning.")
            self.assertTrue(all(val == y[19] for val in y[20:30]), "Wrong imputation in the middle.")
            self.assertTrue(all(val == y[49] for val in y[50:]), "Wrong imputation at the end.")

    def _do_one_grain(self,
                      X_train, X_test,
                      X_ft_tr, X_tr,
                      seasonality,
                      model='additive'):
        """Test if seasonality is correct on just one grain."""
        ERROR_TEMPL = "The stl {} returned incorrect {}. seasonality: {}, model: {}."
        decomp = self._get_stl_decomposition(X_train, seasonality, model)
        assert_array_equal(decomp[STLFeaturizer.TREND_COMPONENT_NAME], X_ft_tr['y_trend'],
                           ERROR_TEMPL.format('fit_transform', 'trend', seasonality, model))
        assert_array_equal(decomp[STLFeaturizer.SEASONAL_COMPONENT_NAME], X_ft_tr['y_season'],
                           ERROR_TEMPL.format('fit_transform', 'seasonality', seasonality, model))
        # Now test the trend prediction in the absence of ts_values.
        non_nan_trend = \
            decomp[STLFeaturizer.TREND_COMPONENT_NAME][~np.isnan(decomp[STLFeaturizer.TREND_COMPONENT_NAME])]
        ets_model = \
            ExponentialSmoothing(non_nan_trend,
                                 trend='add' if model == 'additive' else 'mul',
                                 seasonal=None)  # Assume no season for trend.
        ets_model = ets_model.fit(use_boxcox=False, use_basinhopping=False)
        # Assume ExponentialSmoothing returns ground truth.
        y_true = ets_model.forecast(steps=X_test.shape[0])
        # We want to set ts_value_colname to None to emulate
        # what we will have in the automl transformation.
        X_test.ts_value_colname = None
        # continue seasonality where we have ended.
        expected_start = X_train.shape[0] % seasonality
        expected_seasonality = \
            decomp[STLFeaturizer.SEASONAL_COMPONENT_NAME][expected_start:expected_start + X_test.shape[0]]
        assert_array_equal(expected_seasonality, X_tr['y_season'],
                           ERROR_TEMPL.format('transform', 'seasonality', seasonality, model))
        assert_array_equal(y_true, X_tr['y_trend'],
                           ERROR_TEMPL.format('transform', 'trend', seasonality, model))

    def _get_stl_decomposition(self,
                               tsdf: TimeSeriesDataFrame,
                               freq: int,
                               model: str):
        """Convenience method to generate stl."""
        df = pd.DataFrame(tsdf.copy())
        # We have a grain in index and we want to remove it.
        df.reset_index(level=tsdf.grain_colnames, drop=True, inplace=True)
        df.sort_index(inplace=True)
        # seasonal_decompose is our ground truth.
        # seasonal_decompose calls seasonality "freq".
        seas, trend, _ = get_stl_decomposition(df['y'].values, seasonality=freq)
        return {STLFeaturizer.TREND_COMPONENT_NAME: trend, STLFeaturizer.SEASONAL_COMPONENT_NAME: seas}

    def whether_user_warning_from_stl_featurizer(self, w):
        """
        If there is a warning that is UserWarning and coming from
        stl_featurizer.py, return True.
        """
        if issubclass(w.category, UserWarning) \
                and 'stl_featurizer.py' in w.filename:
            return True

    def check_seasonality(self, df, freq):
        """
        Check if the data frame contains the valid seasonality.

        :param  df: The data frame.
        :type df: TimeSeriesDataFrame
        :param freq: The seasonality.
        :type freq: pandas.DateOffset

        """
        msft = df[df.grain_index.isin(['MSFT'])][0:2 * freq]
        assert_array_equal(msft['revenue_season'][0:freq].values, msft['revenue_season'][freq:2 * freq].values)

    def _get_tsdfs(self,
                   train_len: int = 12,
                   test_len: int = 6,
                   date_column_name: str = 'date',
                   grain_columns: list = ['grain'],
                   target_column_name: str = 'y',
                   grains_per_col: int = 1,
                   seasonality: int = 2,
                   freq: str = 'D'):
        """
        Convenience function to return TimeSeriesData frame instead of DataFrames.

        :param train_len: The length of training data.
        :type train_len: int
        :param test_len: The length of test data.
        :type test_len: int
        :param date_column_name: The name of a date column.
        :type date_column_name: str
        :param grain_columns: The names of grain columns.
        :type grain_columns: list
        :param target_column_name: The name of a target column to be used.
        :type target_column_name: str
        :param grain_number: the number of grains.
        :type: grain_number: int
        :param freq: string denoting the pandas offset.
        :type freq: str
        :returns: The tuple with X_train, X_test.
        :rtype: tuple

        """
        X_train, y_train, X_test, y_test = get_seasonal_trended_data(
            train_len=train_len,
            test_len=test_len,
            date_column_name=date_column_name,
            grain_columns=grain_columns,
            grains_per_col=grains_per_col,
            seasonality=seasonality,
            freq=freq)
        X_train[target_column_name] = y_train
        X_test[target_column_name] = y_test
        tsdf_train = TimeSeriesDataFrame(X_train,
                                         time_colname=date_column_name,
                                         grain_colnames=grain_columns,
                                         ts_value_colname=target_column_name)
        tsdf_test = TimeSeriesDataFrame(X_test,
                                        time_colname=date_column_name,
                                        grain_colnames=grain_columns,
                                        ts_value_colname=target_column_name)
        return tsdf_train, tsdf_test


def get_seasonal_trended_data(train_len: int = 12,
                              test_len: int = 6,
                              date_column_name: str = 'date',
                              grain_columns: list = ['grain'],
                              grains_per_col: int = 1,
                              seasonality: int = 2,
                              freq: str = 'D',
                              target_colname='y'):
    """
    Get the multiple grain data with seasn and trend.

    :param train_len: The length of training data.
    :type train_len: int
    :param test_len: The length of test data.
    :type test_len: int
    :param date_column_name: The name of a date column.
    :type date_column_name: str
    :param grain_columns: The names of grain columns.
    :type grain_columns: list
    :param grain_number: the number of grains.
    :type: grain_number: int
    :param freq: string denoting the pandas offset.
    :type freq: str
    :returns: The tuple with X_train, y_train, X_test, y_test.
    :rtype: tuple

    """
    grains = {}
    for gcol in grain_columns:
        grains[gcol] = ['{}_{}'.format(gcol, i) for i in range(grains_per_col)]

    dfs_train = []
    dfs_test = []
    int_seed = 1
    df_len = train_len + test_len
    for grain in product(*list(grains.values())):
        targets = [2 * val + (val % seasonality) + int_seed for val in range(df_len)]
        int_seed += 1
        df = pd.DataFrame({
            date_column_name: pd.date_range('2000-01-01', periods=df_len, freq=freq),
            target_colname: targets
        })
        for i in range(len(grain_columns)):
            if isinstance(grain, tuple):
                df[grain_columns[i]] = grain[i]
            else:
                df[grain_columns[i]] = grain
        df_one = df.copy()
        df_one.set_index(date_column_name, inplace=True)
        dfs_train.append(df[:train_len])
        dfs_test.append(df[train_len:])
    X_test = pd.concat(dfs_test).reset_index(drop=True)
    y_test = X_test.pop(target_colname).values
    X_train = pd.concat(dfs_train).reset_index(drop=True)
    y_train = X_train.pop(target_colname).values
    return X_train, y_train, X_test, y_test


if __name__ == "__main__":
    unittest.main()
