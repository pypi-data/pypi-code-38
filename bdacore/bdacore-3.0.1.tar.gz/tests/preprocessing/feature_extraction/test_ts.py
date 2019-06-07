import unittest

import pandas as pd
from pandas.util.testing import assert_frame_equal

from bdacore.preprocessing.feature_extraction import transform_datetxt2int, create_diff_shift_features


class TestTSFeatureExtraction(unittest.TestCase):
    def test_datetext_to_int(self):
        # given
        df = pd.DataFrame({'Date': ['2017-01-04', '2017-03-24']})

        # when
        transform_datetxt2int(df, 'Date', format='%Y-%m-%d')

        # then
        df_expected = pd.DataFrame({'Date': [20170104, 20170324]})

        assert_frame_equal(df_expected, df)

    def test_create_diff_shift_features(self):
        # given
        df = pd.DataFrame({'Ventes-1': [12, 10],
                           'Ventes-2': [8, 15],
                           })

        # when
        create_diff_shift_features(df, cols=list(df.columns))

        # then
        df_expected = pd.DataFrame({'Ventes-1': [12, 10],
                                    'Ventes-2': [8, 15],
                                    'diff_Ventes-2_Ventes-1': [-4, 5]
                                    })

        assert_frame_equal(df_expected, df)
