import unittest
import pandas as pd
import numpy as np
from pandas.util.testing import assert_frame_equal

from azureml.automl.core.featurizer.transformer.timeseries.category_binarizer import CategoryBinarizer
from azureml.automl.core.featurizer.transformer.timeseries.forecasting_pipeline import AzureMLForecastPipeline
from automl.client.core.common.time_series_data_frame import TimeSeriesDataFrame


class TestCategoryBinarizer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # Data frame with a numeric feature and two categoricals -
        #  one a string and the other an integer
        cls.dat = {'Date': pd.date_range(start='2013-01',
                                         periods=6, freq='MS'),
                   'Type': ['alpha'] * 3 + ['beta'] * 3,
                   'Value': [1.5] * 6,
                   'NumericFeature': np.arange(6.0),
                   'CatFeature1': ['lv1', 'lv2'] * 3,
                   'CatFeature2': [7, 8] * 3}

        cls.tsdf = TimeSeriesDataFrame(data=cls.dat,
                                       time_colname='Date',
                                       grain_colnames=['Type'],
                                       ts_value_colname='Value')

    def test_catbinarize_fit_transform(self):
        """
        Test that fit/transform returns a TimeSeriesDataFrame
        with the right number of rows
        """

        binarizer = CategoryBinarizer(columns=['CatFeature1', 'CatFeature2'])
        new_tsdf = binarizer.fit_transform(self.tsdf)
        self.assertTrue(isinstance(new_tsdf, TimeSeriesDataFrame))
        self.assertTrue(len(new_tsdf) == len(self.tsdf))

    def test_catbinarize_expected_output(self):
        """
        Test that transform produces expected output
        """

        # Transform given tsdf
        binarizer = CategoryBinarizer(columns=['CatFeature1', 'CatFeature2'],
                                      prefix_sep='_', prefix=None,
                                      drop_first=False)
        my_tsdf = binarizer.fit_transform(self.tsdf)

        # Manually construct expected output
        dat_expect = {'Date': pd.date_range(start='2013-01',
                                            periods=6, freq='MS'),
                      'Type': ['alpha'] * 3 + ['beta'] * 3,
                      'Value': [1.5] * 6,
                      'NumericFeature': np.arange(6.0),
                      'CatFeature1_lv1': [1, 0] * 3,
                      'CatFeature1_lv2': [0, 1] * 3,
                      'CatFeature2_7': [1, 0] * 3,
                      'CatFeature2_8': [0, 1] * 3}

        tsdf_expect = TimeSeriesDataFrame(data=dat_expect,
                                          time_colname='Date',
                                          grain_colnames=['Type'],
                                          ts_value_colname='Value')

        # Sort the columns in both frames prior to comparison
        my_tsdf.sort_index(axis=1, inplace=True)
        tsdf_expect.sort_index(axis=1, inplace=True)

        # Test frame equality
        # Don't care much about column dtype checks here
        assert_frame_equal(my_tsdf, tsdf_expect, check_dtype=False)

        # Test that transform detects a categorical column with
        #  the encode_all_categoricals option
        binarizer = CategoryBinarizer(columns='CatFeature2',
                                      encode_all_categoricals=True,
                                      prefix_sep='_', prefix=None,
                                      drop_first=False)
        my_tsdf = binarizer.fit_transform(self.tsdf)
        my_tsdf.sort_index(axis=1, inplace=True)

        assert_frame_equal(my_tsdf, tsdf_expect, check_dtype=False)

    def test_catbinarize_drop_first_expected_output(self):
        """
        Test that transform produces expected output
        """

        # Transform given tsdf with drop_first=True
        binarizer = CategoryBinarizer(columns=['CatFeature1', 'CatFeature2'],
                                      prefix_sep='_', prefix=None,
                                      drop_first=True)
        my_tsdf = binarizer.fit_transform(self.tsdf)

        # Manually construct expected output
        dat_expect = {'Date': pd.date_range(start='2013-01',
                                            periods=6, freq='MS'),
                      'Type': ['alpha'] * 3 + ['beta'] * 3,
                      'Value': [1.5] * 6,
                      'NumericFeature': np.arange(6.0),
                      'CatFeature1_lv2': [0, 1] * 3,
                      'CatFeature2_8': [0, 1] * 3}

        tsdf_expect = TimeSeriesDataFrame(data=dat_expect,
                                          time_colname='Date',
                                          grain_colnames=['Type'],
                                          ts_value_colname='Value')

        # Sort the columns in both frames prior to comparison
        my_tsdf.sort_index(axis=1, inplace=True)
        tsdf_expect.sort_index(axis=1, inplace=True)

        # Test frame equality
        # Don't care much about column dtype checks here
        assert_frame_equal(my_tsdf, tsdf_expect, check_dtype=False)

    def test_catbinarize_different_levels_in_fit_transform(self):
        """
        Test binarizer when
        1) A categorical variable has levels
           present at fit that aren't present at transform.
        2) A categorical variable has levels present at
           transform that aren't present at fit

        Classic train/test categorical level issues.
        """

        tsdf_train = self.tsdf

        dat_test = {'Date': pd.date_range(start='2013-07',
                                          periods=3, freq='MS'),
                    'Type': ['alpha'] * 3,
                    'Value': [1.5] * 3,
                    'NumericFeature': np.arange(3.0),
                    'CatFeature1': ['lv1'] * 3,
                    'CatFeature2': [7] * 3}

        tsdf_test = TimeSeriesDataFrame(data=dat_test,
                                        time_colname='Date',
                                        grain_colnames=['Type'],
                                        ts_value_colname='Value')

        binarizer = CategoryBinarizer(columns=['CatFeature1', 'CatFeature2'],
                                      prefix_sep='_', prefix=None,
                                      dummy_na=False,
                                      drop_first=True)

        tsdf_binarized_train = binarizer.fit_transform(tsdf_train)
        tsdf_binarized_test = binarizer.transform(tsdf_test)

        # Make sure the same set of columns are present and in the same order
        self.assertListEqual(list(tsdf_binarized_train.columns),
                             list(tsdf_binarized_test.columns))

        # Introduce a new category to the test set
        dat_test = {'Date': pd.date_range(start='2013-07',
                                          periods=3, freq='MS'),
                    'Type': ['alpha'] * 3,
                    'Value': [1.5] * 3,
                    'NumericFeature': np.arange(3.0),
                    'CatFeature1': ['lv3'] * 3,
                    'CatFeature2': [7] * 3}

        tsdf_test = TimeSeriesDataFrame(data=dat_test,
                                        time_colname='Date',
                                        grain_colnames=['Type'],
                                        ts_value_colname='Value')

        tsdf_binarized_test = binarizer.transform(tsdf_test)

        # Set of columns should be the same as in train since
        #  the dummy_na option in the transform is set to False
        #  i.e. the NA entries should be ignored in the dummy coding
        self.assertListEqual(list(tsdf_binarized_train.columns),
                             list(tsdf_binarized_test.columns))

    def test_catbinarize_in_pipeline(self):
        """
        Test binarizer as a step in a pipeline
        """

        binarizer = CategoryBinarizer(columns=['CatFeature1', 'CatFeature2'],
                                      prefix_sep='_', prefix=None,
                                      drop_first=False)

        pline = AzureMLForecastPipeline(steps=[('binarizer', binarizer)])

        my_tsdf = pline.fit_transform(self.tsdf)

        # Manually construct expected output
        dat_expect = {'Date': pd.date_range(start='2013-01',
                                            periods=6, freq='MS'),
                      'Type': ['alpha'] * 3 + ['beta'] * 3,
                      'Value': [1.5] * 6,
                      'NumericFeature': np.arange(6.0),
                      'CatFeature1_lv1': [1, 0] * 3,
                      'CatFeature1_lv2': [0, 1] * 3,
                      'CatFeature2_7': [1, 0] * 3,
                      'CatFeature2_8': [0, 1] * 3}

        tsdf_expect = TimeSeriesDataFrame(data=dat_expect,
                                          time_colname='Date',
                                          grain_colnames=['Type'],
                                          ts_value_colname='Value')

        # Sort the columns in both frames prior to comparison
        my_tsdf.sort_index(axis=1, inplace=True)
        tsdf_expect.sort_index(axis=1, inplace=True)

        # Test frame equality
        # Don't care much about column dtype checks here
        assert_frame_equal(my_tsdf, tsdf_expect, check_dtype=False)

    def test_catbinarize_detect_columns(self):
        """
        Test that a CategoryBinarizer will detect
        categorical columns and encode them.
        Also make sure detection works on re-fit.
        """

        binarizer = CategoryBinarizer(prefix_sep='_', prefix=None,
                                      drop_first=False)
        tsdf1 = binarizer.fit_transform(self.tsdf)

        # Expect that CatFeature1 will be encoded automatically
        #  since it is str type
        self.assertListEqual(binarizer.columns_in_fit, ['CatFeature1'])

        # Check expected output
        dat1_expect = {'Date': pd.date_range(start='2013-01',
                                             periods=6, freq='MS'),
                       'Type': ['alpha'] * 3 + ['beta'] * 3,
                       'Value': [1.5] * 6,
                       'NumericFeature': np.arange(6.0),
                       'CatFeature1_lv1': [1, 0] * 3,
                       'CatFeature1_lv2': [0, 1] * 3,
                       'CatFeature2': [7, 8] * 3}

        tsdf1_expect = TimeSeriesDataFrame(data=dat1_expect,
                                           time_colname='Date',
                                           grain_colnames=['Type'],
                                           ts_value_colname='Value')

        # Sort the columns in both frames prior to comparison
        tsdf1.sort_index(axis=1, inplace=True)
        tsdf1_expect.sort_index(axis=1, inplace=True)

        # Test frame equality
        # Don't care much about column dtype checks here
        assert_frame_equal(tsdf1, tsdf1_expect, check_dtype=False)

        # Add another categorical feature to the TSDF
        extra_cat_tsdf = self.tsdf.copy()
        extra_cat_tsdf['CatFeature3'] = ['t1', 't2'] * 3
        tsdf2 = binarizer.fit_transform(extra_cat_tsdf)

        self.assertSetEqual(set(binarizer.columns_in_fit),
                            set(['CatFeature1', 'CatFeature3']))

        # Check expected output
        dat2_expect = {'Date': pd.date_range(start='2013-01',
                                             periods=6, freq='MS'),
                       'Type': ['alpha'] * 3 + ['beta'] * 3,
                       'Value': [1.5] * 6,
                       'NumericFeature': np.arange(6.0),
                       'CatFeature1_lv1': [1, 0] * 3,
                       'CatFeature1_lv2': [0, 1] * 3,
                       'CatFeature2': [7, 8] * 3,
                       'CatFeature3_t1': [1, 0] * 3,
                       'CatFeature3_t2': [0, 1] * 3}

        tsdf2_expect = TimeSeriesDataFrame(data=dat2_expect,
                                           time_colname='Date',
                                           grain_colnames=['Type'],
                                           ts_value_colname='Value')

        # Sort the columns in both frames prior to comparison
        tsdf2.sort_index(axis=1, inplace=True)
        tsdf2_expect.sort_index(axis=1, inplace=True)

        # Test frame equality
        # Don't care much about column dtype checks here
        assert_frame_equal(tsdf2, tsdf2_expect, check_dtype=False)


if __name__ == '__main__':
    unittest.main()
