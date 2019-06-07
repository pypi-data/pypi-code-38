import unittest

import pandas as pd

from bdacore.preprocessing.ts.rolling import RollingWindower
from bdacore.outliers.utils import mad


class TestComputeMAV(unittest.TestCase):
    def test_compute_moving_average(self):
        df = pd.DataFrame({'data': [0, 1, 2, 3, 4], 'data_bis': [3, 1, 0, 4, 1]})

        roller = RollingWindower(windows=[3], min_periods=1)

        # compute potential differences -> test will fail if a difference is present
        df_mean = pd.DataFrame({'mean_3_data': [0, 0.5, 1, 2, 3], 'mean_3_data_bis': [3, 2, 4 / 3.0, 5 / 3.0, 5 / 3.0]})
        df_test = df_mean.sub(roller.transform(df))
        self.assertEqual(df_test.sum().sum(), 0)

    def test_compute_moving_average_and_differences(self):
        df = pd.DataFrame({'data': [0, 1, 2, 3, 4], 'data_bis': [3, 1, 0, 4, 1]})

        df_mean_diff = pd.DataFrame(
            {'mean_diff_2_data': [0, 0.5, 0.5, 0.5, 0.5],
             'mean_diff_2_data_bis': [0, -1, -0.5, 2, -1.5],
             'mean_diff_5_data': [0, 0.5, 1, 1.5, 2],
             'mean_diff_5_data_bis': [0, -1, -4 / 3.0, 2, -0.8]})

        roller = RollingWindower(windows=[2, 5], diff_mode=True)

        df_test = df_mean_diff.sub(roller.transform(df))
        self.assertEqual(df_test.sum().sum(), 0)

    def test_compute_custom_function(self):
        df = pd.DataFrame({'data': [0, 1, 2, 3, 4], 'data_bis': [3, 1, 0, 4, 1]})

        roller = RollingWindower(operation=mad, windows=[3], min_periods=1)

        # compute potential differences -> test will fail if a difference is present
        df_mad_true = pd.DataFrame({'mad_3_data': [0, 0.5, 1, 1, 1], 'mad_3_data_bis': [0, 1, 1, 1, 1]})
        df_mad = roller.transform(df)
        df_test = df_mad_true.sub(df_mad)
        self.assertEqual(df_test.sum().sum(), 0)

    def test_compute_moving_average_with_datetime(self):
        df_ts = pd.DataFrame({'data': [0, 1, 2, 3, 4]},
                             index=[pd.Timestamp('20130101 09:00:00'),
                                    pd.Timestamp('20130101 09:00:02'),
                                    pd.Timestamp('20130101 09:00:03'),
                                    pd.Timestamp('20130101 09:00:05'),
                                    pd.Timestamp('20130101 09:00:06')])

        df_mean_ts = pd.DataFrame(
            {'mean_5s_data': [0, 0.5, 1, 2, 2.5],
             'mean_2s_data': [0, 1, 1.5, 3, 3.5]},
            index=[pd.Timestamp('20130101 09:00:00'),
                   pd.Timestamp('20130101 09:00:02'),
                   pd.Timestamp('20130101 09:00:03'),
                   pd.Timestamp('20130101 09:00:05'),
                   pd.Timestamp('20130101 09:00:06')]
        )

        roller = RollingWindower(windows=['5s', '2s'])

        df_test = df_mean_ts.sub(roller.transform(df_ts))
        self.assertEqual(df_test.sum().sum(), 0)
