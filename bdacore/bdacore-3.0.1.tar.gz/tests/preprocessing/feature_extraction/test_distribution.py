import unittest

import pandas as pd
from pandas.util.testing import assert_frame_equal

from bdacore.preprocessing.feature_extraction import DistributionTransformer


class TestDistribution(unittest.TestCase):
    def test_distribution_transformer_should_produce_df_distribution_per_column_for_int_window(self):
        # given
        df = pd.DataFrame({'sales': [3, 10, 12, 23, 48, 19, 21]})

        # when
        distrib_transformer = DistributionTransformer(3)
        df_distrib = distrib_transformer.fit_transform(df)

        # then
        df_expected = pd.DataFrame({'sales_bin_1': [0, 1, 1, 2, 1, 2, 2],
                                    'sales_bin_2': [0, 0, 0, 0, 1, 0, 0],
                                    'sales_bin_3': [1, 0, 0, 0, 0, 0, 0],
                                    'sales_bin_4': [0, 1, 2, 1, 1, 1, 1]})

        assert_frame_equal(df_expected, df_distrib)
