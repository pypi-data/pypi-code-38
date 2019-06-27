import unittest

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from azureml.automl.core.featurizer.transformer.timeseries.grain_index_featurizer import GrainIndexFeaturizer
from automl.client.core.common.forecasting_exception import AzureMLForecastException
from automl.client.core.common.time_series_data_frame import TimeSeriesDataFrame

from ...test_data.dominicks_oj import load_dominicks_oj_dataset


class TestFTKMLTransformsGrainIndexFeaturizer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.oj_train_tsdf, cls.oj_test_tsdf = \
            load_dominicks_oj_dataset()

        # Remove WeekFirstDay column
        # It causes problems since it is a date
        cls.oj_train_tsdf.drop('WeekFirstDay', axis=1, inplace=True)
        cls.oj_test_tsdf.drop('WeekFirstDay', axis=1, inplace=True)

        # Extract a subset
        store_list = [2, 5]
        brand_list = ['dominicks', 'tropicana']
        slicer = pd.IndexSlice[:, store_list, brand_list]
        cls.oj_train_tsdf.sort_index(inplace=True)
        cls.oj_train_slice = cls.oj_train_tsdf.loc[slicer, :]
        cls.oj_test_tsdf.sort_index(inplace=True)
        cls.oj_test_slice = cls.oj_test_tsdf.loc[slicer, :]

        cls.oj_freq = 'W-WED'

    def test_grain_index_featurizer_grain_only(self):

        grain_featurizer = GrainIndexFeaturizer(grain_feature_prefix='grain',
                                                prefix_sep='_')

        new_tsdf = grain_featurizer.fit_transform(self.oj_train_slice)

        # Make sure there are two new feature columns
        self.assertTrue('grain_store' in new_tsdf.columns)
        self.assertTrue('grain_brand' in new_tsdf.columns)

        # Make sure they have dtype='category'
        category_tsdf = new_tsdf.select_dtypes(include=['category'])
        self.assertTrue('grain_store' in category_tsdf.columns)
        self.assertTrue('grain_brand' in category_tsdf.columns)

        # Make sure the values are the same as the original index values
        for gr in ('store', 'brand'):
            gr_index_values = (self.oj_train_slice.
                               index.get_level_values(gr)).values
            feat_values = new_tsdf['grain_' + gr].values
            self.assertTrue(np.array_equal(feat_values, gr_index_values))

    def test_grain_index_featurizer_column_overwrite(self):
        """
        Test featurizer when an existing column has the same name
        as one of the grain features
        """

        # Pre-empt the transform and add a grain feature manually
        new_assign = {'grain_store':
                      self.oj_train_slice.index.get_level_values('store')}
        my_tsdf = self.oj_train_slice.assign(**new_assign)

        grain_featurizer = GrainIndexFeaturizer(grain_feature_prefix='grain',
                                                prefix_sep='_',
                                                overwrite_columns=False)

        with self.assertRaises(AzureMLForecastException):
            grain_featurizer.fit_transform(my_tsdf)

    def test_no_grain_index(self):
        """
        Test that function returns original frame when no
        grain index
        """
        # Create example dataset with no grain
        example_data = TimeSeriesDataFrame(
            {'date': pd.date_range(start='1/1/2018', periods=10),
             'value': list(range(10)),
             'feature': list(range(-5, 5))},
            time_colname='date', ts_value_colname='value'
        )

        # Grain featurizer
        grain_featurizer = GrainIndexFeaturizer()

        new_tsdf = grain_featurizer.fit_transform(example_data)

        # Check two frames are equal
        for name in example_data._metadata:
            self.assertEqual(getattr(example_data, name, None),
                             getattr(new_tsdf, name, None))
        assert_frame_equal(example_data, new_tsdf)


if __name__ == '__main__':
    unittest.main()
