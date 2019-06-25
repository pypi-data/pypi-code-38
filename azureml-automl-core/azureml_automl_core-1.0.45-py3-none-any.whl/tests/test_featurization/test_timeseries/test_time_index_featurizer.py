import unittest

import numpy as np
import pandas as pd

from azureml.automl.core.featurizer.transformer.timeseries.time_index_featurizer import TimeIndexFeaturizer
from automl.client.core.common.time_series_data_frame import TimeSeriesDataFrame
from azureml.automl.core.featurizer.transformer.timeseries.forecasting_pipeline import AzureMLForecastPipeline
from automl.client.core.common.constants import TimeSeriesInternal, TimeSeries
from pandas.util.testing import assert_frame_equal


class TestFTKMLTransformsTimeIndexFeaturizer(unittest.TestCase):
    """
    Unit tests for the TimeIndexFeaturizer transform.

    Test constructing features using the transform method and also as
    part of a forecast pipeline. Following tests are implemented:
        1.  Overwrite=False, Prune=False
        2.  Overwrite=True, Prune=False
        3.  Timestamps, Prune=False
        4.  In pipeline, Prune=False
        5.  In pipeline and overwrite=True, Prune=False
        6.  Overwrite=False, Prune=True
        7.  Overwrite=True, Prune=True
        8.  Timestamps, Prune=True
        9.  In pipeline, Prune=True
        10. In pipeline and overwrite=True, Prune=True
        11. Overwrite=False, Prune=True, cutoff=0.5
        12. In pipeline, Overwrite=False, Prune=True, cutoff=0.5
        13. Holiday feature
        14. Other datetime columns
    """

    EXPECTED_NEW_FEATURE_COLUMN_NAMES = {
        'year', 'year_iso', 'half', 'quarter', 'month', 'month_lbl', 'day',
        'hour', 'minute', 'second', 'am_pm', 'am_pm_lbl', 'hour12', 'wday',
        'wday_lbl', 'qday', 'yday', 'week'}
    EXPECTED_PRUNED_FEATURES = {'year_iso', 'quarter', 'month', 'wday', 'qday'}
    EXPECTED_PRUNED_FEATURES_TIMESTAMP = {
        'year', 'hour', 'minute', 'am_pm', 'day', 'second', 'month',
        'quarter', 'qday', 'hour12', 'yday', 'wday', 'half'}
    EXPECTED_PRUNED_FEATURES_CORREL_05 = {'year', 'half', 'hour'}
    EXPECTED_PRUNED_FEATURES_CORREL_14 = {'year_iso', 'quarter', 'week', 'wday', 'half'}
    _datetime_sub_feature_names = {'Year', 'Month', 'Day', 'DayOfWeek', 'DayOfYear', 'QuarterOfYear',
                                   'WeekOfMonth', 'Hour', 'Minute', 'Second'}

    def setUp(self):
        raw_data1 = {'store': ['safeway'] * 3 + ['wholefoods'] * 4,
                     'date': pd.to_datetime(
                         ['2017-01-01', '2017-02-01', '2017-03-01'] * 2 +
                         ['2017-04-01']),
                     'units': range(1, 8),
                     'sales': range(8, 15),
                     'price': [2] * 7,
                     'origin': pd.to_datetime(['2017-01-01'] * 6 + ['2017-04-01'])}
        test_df1 = pd.DataFrame(raw_data1)
        # first tsdf is 'regular'
        self.test_tsdf1 = TimeSeriesDataFrame(
            data=test_df1, grain_colnames=['store'],
            time_colname='date', ts_value_colname='sales',
            origin_time_colname='origin')
        # second tsdf has a 'year' column to test overwrites
        test_df2 = test_df1.copy()
        test_df2['year'] = 2016
        self.test_tsdf2 = TimeSeriesDataFrame(
            data=test_df2, grain_colnames=['store'],
            time_colname='date', ts_value_colname='sales',
            origin_time_colname='origin')
        # third tsdf uses timestamped data with time zones to make sure
        # we work with obscure edge cases
        #
        # TODO: support several time zones gracefully, we currently do not
        #
        raw_data2 = ["2016-03-01T23:01:11", "2016-02-29T04:16:00",
                     "2016-04-02T00:01:22", "2016-03-09T13:01:01",
                     "2016-09-15T12:45:33", "2017-04-12T23:19:59",
                     "2017-08-12T06:42:44", "2017-05-05T14:33:30",
                     "2012-07-23T18:24:55", "2010-06-29T04:59:16"]
        dt = pd.to_datetime(raw_data2)
        dt_pst = dt.tz_localize('America/Los_Angeles')
        test_df3 = pd.DataFrame({'date': dt_pst})
        self.test_tsdf3 = TimeSeriesDataFrame(test_df3, time_colname='date')

        raw_data4 = {'store': ['safeway'] * 3 + ['wholefoods'] * 4,
                     'date': pd.to_datetime(
                         ['2017-01-01', '2017-01-02', '2017-01-03'] * 2 +
                         ['2017-01-04']),
                     'sales': range(8, 15)}
        self.test_tsdf4 = TimeSeriesDataFrame(
            data=pd.DataFrame(raw_data4), grain_colnames=['store'],
            time_colname='date', ts_value_colname='sales')

        raw_data5 = {'store': ['safeway'] * 3 + ['wholefoods'] * 4,
                     'date': pd.to_datetime(
                         ['2017-01-01', '2017-04-02', '2017-07-03'] * 2 +
                         ['2017-10-04']),
                     'shipdate': pd.to_datetime(
                         ['2016-11-11', '2016-12-07'] * 3 +
                         ['2016-10-09']),
                     'instockdate': pd.to_datetime(
                         ['2015-03-20'] * 7),
                     'sales': range(8, 15)}
        self.test_tsdf5 = TimeSeriesDataFrame(
            data=pd.DataFrame(raw_data5), grain_colnames=['store'],
            time_colname='date', ts_value_colname='sales')

        raw_data6 = {'store': ['safeway'] * 3 + ['wholefoods'] * 4,
                     'date': pd.to_datetime(
                         ['2017-04-01', '2017-04-02', '2017-04-03'] * 2 +
                         ['2017-04-04']),
                     'sales': range(8, 15)}
        self.test_tsdf6 = TimeSeriesDataFrame(
            data=pd.DataFrame(raw_data6), grain_colnames=['store'],
            time_colname='date', ts_value_colname='sales')

    # Test 1
    def test_index_featurizer_no_overwrite(self):
        """
        Try to featurize test_tsdf1 where no columns are expected to be
        overwritten. Happy path, this should work smoothly.
        """

        index_featurizer_step = TimeIndexFeaturizer(prune_features=False)
        out_tsdf1 = index_featurizer_step.fit_transform(self.test_tsdf1)
        actual_column_names = set(out_tsdf1.columns)

        self.assertTrue(
            TestFTKMLTransformsTimeIndexFeaturizer
            .EXPECTED_NEW_FEATURE_COLUMN_NAMES
            .issubset(actual_column_names))

    # Test 2
    def test_index_featurizer_with_overwrites(self):
        """
        Try to featurize test_tsdf1 where one column is expected to be
        overwritten. Testing for exception, warning, and eventual success.
        """
        index_featurizer_step1 = TimeIndexFeaturizer(prune_features=False)
        with self.assertRaises(RuntimeError):
            _ = index_featurizer_step1.fit_transform(self.test_tsdf2)
        index_featurizer_step2 = TimeIndexFeaturizer(overwrite_columns=True,
                                                     prune_features=False)
        with self.assertWarns(UserWarning):
            out_tsdf2 = index_featurizer_step2.fit_transform(self.test_tsdf2)
        actual_column_names = set(out_tsdf2.columns)
        self.assertTrue(
            TestFTKMLTransformsTimeIndexFeaturizer
            .EXPECTED_NEW_FEATURE_COLUMN_NAMES
            .issubset(actual_column_names))

    # Test 3
    def test_index_featurizer_with_timestamps(self):
        """
        Try to featurize test_tsdf3 where no columns are expected to be
        overwritten, and which has plenty of hour/minute/second time zones.
        """

        index_featurizer_step = TimeIndexFeaturizer(prune_features=False)
        out_tsdf3 = index_featurizer_step.fit_transform(self.test_tsdf3)
        actual_column_names = set(out_tsdf3.columns)

        self.assertTrue(
            TestFTKMLTransformsTimeIndexFeaturizer
            .EXPECTED_NEW_FEATURE_COLUMN_NAMES
            .issubset(actual_column_names))

    # Test 4
    def test_index_featurizer_in_pipeline(self):
        """
        Plug the index featurizer transform into a pipeline and try it
        """
        pipeline = AzureMLForecastPipeline(
            steps=[('index_features', TimeIndexFeaturizer(prune_features=False))])
        out_tsdf1 = pipeline.fit_transform(self.test_tsdf1)
        actual_column_names = set(out_tsdf1.columns)

        self.assertTrue(
            TestFTKMLTransformsTimeIndexFeaturizer
            .EXPECTED_NEW_FEATURE_COLUMN_NAMES
            .issubset(actual_column_names))

    # Test 5
    def test_index_featurizer_with_overwrite_in_pipeline(self):
        """
        Plug the index featurizer transform into a pipeline and try it, with
        overwrite_columns set to True.
        """
        pipeline1 = AzureMLForecastPipeline(
            steps=[('index_features1',
                    TimeIndexFeaturizer(prune_features=False))])
        with self.assertRaises(RuntimeError):
            _ = pipeline1.fit_transform(self.test_tsdf2)

        pipeline2 = AzureMLForecastPipeline(
            steps=[('index_features2',
                    TimeIndexFeaturizer(overwrite_columns=True,
                                        prune_features=False))])
        with self.assertWarns(UserWarning):
            out_tsdf2 = pipeline2.fit_transform(self.test_tsdf2)
        actual_column_names = set(out_tsdf2.columns)
        self.assertTrue(
            TestFTKMLTransformsTimeIndexFeaturizer
            .EXPECTED_NEW_FEATURE_COLUMN_NAMES
            .issubset(actual_column_names))

    # Test 6
    def test_index_featurizer_with_pruning(self):
        """
        Try to featurize test_tsdf1 where no columns are expected to be
        overwritten and features are pruned.
        """
        index_featurizer_step = TimeIndexFeaturizer()
        out_tsdf1 = index_featurizer_step.fit_transform(self.test_tsdf1)
        actual_column_names = set(out_tsdf1.columns)
        self.assertTrue(
            TestFTKMLTransformsTimeIndexFeaturizer
            .EXPECTED_PRUNED_FEATURES
            .issubset(actual_column_names))

    # Test 7
    def test_index_featurizer_with_overwrites_and_pruning(self):
        """
        Try to featurize test_tsdf1 where one column is expected to be
        overwritten. Testing for exception, warning, and eventual success.
        """

        index_featurizer_step1 = TimeIndexFeaturizer()
        with self.assertRaises(RuntimeError):
            _ = index_featurizer_step1.fit_transform(self.test_tsdf2)
        index_featurizer_step2 = TimeIndexFeaturizer(overwrite_columns=True)
        with self.assertWarns(UserWarning):
            out_tsdf2 = index_featurizer_step2.fit_transform(self.test_tsdf2)
        actual_column_names = set(out_tsdf2.columns)
        self.assertTrue(
            TestFTKMLTransformsTimeIndexFeaturizer
            .EXPECTED_PRUNED_FEATURES
            .issubset(actual_column_names))

    # Test 8
    def test_index_featurizer_with_timestamps_and_pruning(self):
        """
        Try to featurize test_tsdf3 where no columns are expected to be
        overwritten, and which has plenty of hour/minute/second time zones.
        Also perform feature pruning.
        """
        index_featurizer_step = TimeIndexFeaturizer()
        out_tsdf3 = index_featurizer_step.fit_transform(self.test_tsdf3)
        actual_column_names = set(out_tsdf3.columns)
        self.assertTrue(
            TestFTKMLTransformsTimeIndexFeaturizer
            .EXPECTED_PRUNED_FEATURES_TIMESTAMP
            .issubset(actual_column_names))

    # Test 9
    def test_index_featurizer_in_pipeline_and_prune(self):
        """
        Plug the index featurizer transform into a pipeline and try it, also
        perform feature pruning as part of transform.
        """
        pipeline = AzureMLForecastPipeline(
            steps=[('index_features', TimeIndexFeaturizer())])
        out_tsdf1 = pipeline.fit_transform(self.test_tsdf1)
        actual_column_names = set(out_tsdf1.columns)

        self.assertTrue(
            TestFTKMLTransformsTimeIndexFeaturizer
            .EXPECTED_PRUNED_FEATURES
            .issubset(actual_column_names))

    # Test 10
    def test_index_featurizer_with_overwrite_and_prune_in_pipeline(self):
        """
        Plug the index featurizer transform into a pipeline and try it, with
        overwrite_columns set to True and prune_features also set to True
        """
        pipeline1 = AzureMLForecastPipeline(
            steps=[('index_features1', TimeIndexFeaturizer())])
        with self.assertRaises(RuntimeError):
            _ = pipeline1.fit_transform(self.test_tsdf2)

        pipeline2 = AzureMLForecastPipeline(
            steps=[('index_features2',
                    TimeIndexFeaturizer(overwrite_columns=True))])
        with self.assertWarns(UserWarning):
            out_tsdf2 = pipeline2.fit_transform(self.test_tsdf2)
        actual_column_names = set(out_tsdf2.columns)
        self.assertTrue(
            TestFTKMLTransformsTimeIndexFeaturizer
            .EXPECTED_PRUNED_FEATURES
            .issubset(actual_column_names))

    # Test 11
    def test_index_featurizer_with_timestamps_and_custom_cutoff(self):
        """
        Try to featurize test_tsdf3 where no columns are expected to be
        overwritten, and which has plenty of hour/minute/second time zones.
        Also perform feature pruning with a non-default correlation_cutoff.
        """
        # test that correlation_cutoff checks are working
        # must be at least zero
        with self.assertRaises(ValueError):
            _ = TimeIndexFeaturizer(correlation_cutoff=-1)
        # must be no more than 1
        with self.assertRaises(ValueError):
            _ = TimeIndexFeaturizer(correlation_cutoff=2)
        # cannot be none
        with self.assertRaises(ValueError):
            _ = TimeIndexFeaturizer(correlation_cutoff=None)
        # cannot be string
        with self.assertRaises(ValueError):
            _ = TimeIndexFeaturizer(correlation_cutoff='a')
        # even string convertible to number is not allowed
        with self.assertRaises(ValueError):
            _ = TimeIndexFeaturizer(correlation_cutoff='0.7')
        # actual test
        index_featurizer_step = TimeIndexFeaturizer(correlation_cutoff=0.5)
        out_tsdf3 = index_featurizer_step.fit_transform(self.test_tsdf3)
        actual_column_names = set(out_tsdf3.columns)
        # print("a: {}".format(actual_column_names))
        self.assertTrue(
            TestFTKMLTransformsTimeIndexFeaturizer
            .EXPECTED_PRUNED_FEATURES_CORREL_05
            .issubset(actual_column_names))

    # Test 12
    def test_index_featurizer_timestamps_in_pipeline_and_prune(self):
        """
        Plug the index featurizer transform into a pipeline and try it, also
        perform feature pruning with a custom correlation as part of transform.
        Use data with timestamps.
        """
        pipeline = AzureMLForecastPipeline(
            steps=[('index_features',
                    TimeIndexFeaturizer(correlation_cutoff=0.5))])
        out_tsdf1 = pipeline.fit_transform(self.test_tsdf3)
        actual_column_names = set(out_tsdf1.columns)

        self.assertTrue(
            TestFTKMLTransformsTimeIndexFeaturizer
            .EXPECTED_PRUNED_FEATURES_CORREL_05
            .issubset(actual_column_names))

    # Test 13
    def test_index_featurizer_holiday(self):
        """
        Test the enriched holiday names feature.
        """
        index_featurizer_step = TimeIndexFeaturizer(country_or_region='US', freq=self.test_tsdf4.infer_freq())
        out_tsdf4 = index_featurizer_step.fit_transform(self.test_tsdf4)

        actual_column_names = set(out_tsdf4.columns)
        self.assertIn(TimeSeriesInternal.HOLIDAY_COLUMN_NAME, actual_column_names)
        self.assertIn(TimeSeriesInternal.PAID_TIMEOFF_COLUMN_NAME, actual_column_names)

        # Test the feature names are added for model explanation
        preview_time_feature_names = index_featurizer_step.preview_time_feature_names(self.test_tsdf4)
        self.assertIn(TimeSeriesInternal.HOLIDAY_COLUMN_NAME, preview_time_feature_names)
        self.assertIn(TimeSeriesInternal.PAID_TIMEOFF_COLUMN_NAME, preview_time_feature_names)

        # Test the values
        expectedHolidays = ["New Year's Day", "1 day after New Year's Day", "2 days after New Year's Day",
                            "New Year's Day", "1 day after New Year's Day", "2 days after New Year's Day",
                            "3 days after New Year's Day"]
        expectedPaidHolidays = [1, 0, 0, 1, 0, 0, 0]

        self.assertListEqual(expectedHolidays, out_tsdf4[TimeSeriesInternal.HOLIDAY_COLUMN_NAME].values.tolist())
        self.assertListEqual(expectedPaidHolidays,
                             out_tsdf4[TimeSeriesInternal.PAID_TIMEOFF_COLUMN_NAME].values.tolist())

    def test_index_featurizer_no_holiday(self):
        """
        Test the enriched holiday names feature.
        """
        # training data has holidays
        index_featurizer_step = TimeIndexFeaturizer(country_or_region='US', freq=self.test_tsdf4.infer_freq())
        _ = index_featurizer_step.fit_transform(self.test_tsdf4)

        # dataset6 doesn't have holidays, but we should have columns
        out_tsdf6 = index_featurizer_step.transform(self.test_tsdf6)

        actual_column_names = set(out_tsdf6.columns)
        self.assertIn(TimeSeriesInternal.HOLIDAY_COLUMN_NAME, actual_column_names)
        self.assertIn(TimeSeriesInternal.PAID_TIMEOFF_COLUMN_NAME, actual_column_names)

        # Test the feature names are added for model explanation
        preview_time_feature_names = index_featurizer_step.preview_time_feature_names(self.test_tsdf4)
        self.assertIn(TimeSeriesInternal.HOLIDAY_COLUMN_NAME, preview_time_feature_names)
        self.assertIn(TimeSeriesInternal.PAID_TIMEOFF_COLUMN_NAME, preview_time_feature_names)

        # Test the values
        expectedHolidays = [np.nan] * out_tsdf6.shape[0]
        expectedPaidHolidays = [0] * out_tsdf6.shape[0]

        self.assertListEqual(expectedHolidays, out_tsdf6[TimeSeriesInternal.HOLIDAY_COLUMN_NAME].values.tolist())
        self.assertListEqual(expectedPaidHolidays,
                             out_tsdf6[TimeSeriesInternal.PAID_TIMEOFF_COLUMN_NAME].values.tolist())

    # Test 14
    def test_time_featurize_multi_date(self):
        """
        Try to featurize test_tsdf5 where datetime columns exist.
        """
        index_featurizer_step = TimeIndexFeaturizer(datetime_columns=['shipdate', 'instockdate'])
        out_tsdf5 = index_featurizer_step.fit_transform(self.test_tsdf5)
        actual_column_names = set(out_tsdf5.columns)

        self.assertTrue(
            TestFTKMLTransformsTimeIndexFeaturizer
            .EXPECTED_PRUNED_FEATURES_CORREL_14
            .issubset(actual_column_names))

        shipdate_features = {'shipdate' + '_' + s for s in self._datetime_sub_feature_names}
        self.assertTrue(
            shipdate_features.issubset(actual_column_names))

        instockdate_features = {'instockdate' + '_' + s for s in self._datetime_sub_feature_names}
        self.assertTrue(
            instockdate_features.issubset(actual_column_names))

    def test_time_featurize_force_features(self):
        """
        Test that the "force feature" input
        """
        force_features = ['year', 'quarter', 'second']
        index_featurizer_step = TimeIndexFeaturizer(force_feature_list=force_features)

        # Test non-holiday preview method
        non_holiday_features = index_featurizer_step.preview_non_holiday_feature_names(self.test_tsdf1)
        self.assertSetEqual(set(force_features), set(non_holiday_features))

        # Test on transform output
        out_tsdf1 = index_featurizer_step.fit_transform(self.test_tsdf1)
        actual_column_names = set(out_tsdf1.columns)
        self.assertTrue(set(force_features).issubset(actual_column_names))
        removed_feature_set = set(index_featurizer_step.FEATURE_COLUMN_NAMES) - set(force_features)
        self.assertFalse(removed_feature_set.intersection(actual_column_names))

    def test_afeaturize_seconds(self):
        """
        Test that seconds are featurized.
        """
        tsdf = TimeSeriesDataFrame({
            'date': pd.date_range('2000-01-01', periods=5000, freq='U'),
            'grain': 'grain',
            'test': 42,
            'value': np.arange(5000)
        },
            time_colname='date',
            grain_colnames='grain',
            ts_value_colname='value'
        )
        featurizer = TimeIndexFeaturizer()
        out_tsdf1 = featurizer.fit_transform(tsdf)
        # The data frame is not expected to be featurized by microseconds.
        assert_frame_equal(tsdf, out_tsdf1)


if __name__ == '__main__':
    unittest.main()
