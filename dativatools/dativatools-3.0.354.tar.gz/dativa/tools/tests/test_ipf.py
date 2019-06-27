import numpy as np
from dativa.tools.pandas import Ipf
import pandas as pd
import unittest
import logging
import os


class FastIPFTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.base_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "test_data",
            "ipf_data")

        m = np.array([1., 2., 1., 3., 5., 5., 6., 2., 2., 1., 7., 2.,
                      5., 4., 2., 5., 5., 5., 3., 8., 7., 2., 7., 6.], )
        dma_l = [501, 501, 501, 501, 501, 501, 501, 501, 501, 501, 501, 501,
                 502, 502, 502, 502, 502, 502, 502, 502, 502, 502, 502, 502]
        size_l = [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4,
                  1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4]

        age_l = ['20-25', '30-35', '40-45',
                 '20-25', '30-35', '40-45',
                 '20-25', '30-35', '40-45',
                 '20-25', '30-35', '40-45',
                 '20-25', '30-35', '40-45',
                 '20-25', '30-35', '40-45',
                 '20-25', '30-35', '40-45',
                 '20-25', '30-35', '40-45']

        df = pd.DataFrame()
        df['dma'] = dma_l
        df['size'] = size_l
        df['age'] = age_l
        df['total'] = m

        cls.df = df

        xipp = df.groupby('dma')['total'].sum()
        xpjp = df.groupby('size')['total'].sum()
        xppk = df.groupby('age')['total'].sum()
        # xijp = df.groupby(['dma', 'size'])['total'].sum()
        # xpjk = df.groupby(['size', 'age'])['total'].sum()
        # xppk = df.groupby('age')['total'].sum()

        xipp.loc[501] = 52
        xipp.loc[502] = 48

        xpjp.loc[1] = 20
        xpjp.loc[2] = 30
        xpjp.loc[3] = 35
        xpjp.loc[4] = 15

        xppk.loc['20-25'] = 35
        xppk.loc['30-35'] = 40
        xppk.loc['40-45'] = 25

        cls.aggregates = [xipp, xpjp, xppk]
        cls.dimensions = [['dma'], ['size'], ['age']]

    def test_ipf(self):
        ipf = Ipf(self.aggregates,
                  self.dimensions, 'total')

        df = ipf.run(self.df)

        reference_df = pd.read_csv(os.path.join(self.base_path, 'ipf_data.csv'))

        pd.testing.assert_frame_equal(df, reference_df)

    def test_marginals_len_not_implemented(self):
        ipf = Ipf(self.aggregates,
                  self.dimensions + [['two', 'dimensions']], 'total')

        with self.assertRaises(NotImplementedError):
            ipf.run(self.df)

    def test_attribute_not_in_target_marginals(self):

        df2 = self.df.copy()
        df2['dma'] = df2['dma'] + 10
        df = pd.concat([self.df, df2], sort=False)

        agg = self.aggregates.copy()

        ipf = Ipf(agg,
                  self.dimensions,
                  'total')

        with self.assertRaises(ValueError):
            df = ipf.run(df)

    def test_attribute_not_in_df(self):
        """Non-zero attribute '{0}' in target marginal '{1}' is not present in passed DataFrame"""

        df = self.df[self.df['size'] != 2]  # remove one marginal
        ipf = Ipf(self.aggregates,
                  self.dimensions[:-1], 'total')

        with self.assertRaises(ValueError):
            ipf.run(df)

    def test_marginal_is_not_present_in_aggregates(self):
        agg = self.aggregates.copy()

        agg[1] = pd.Series(['null'])  # replace one aggregate

        ipf = Ipf(agg,
                  self.dimensions,
                  'total')

        with self.assertRaises(ValueError):
            ipf.run(self.df)

    def test_conv_below_threshold(self):

        ipf = Ipf(self.aggregates,
                  self.dimensions,
                  'total',
                  convergence_rate=100,  # artificially high convergence rate
                  rate_tolerance=1e-20,  # artificially low tolerance
                  validate_marginals=True)

        with self.assertLogs('dativa.tools.fastipf', level=logging.WARNING) as l:
            ipf.run(self.df)

        self.assertEqual([
            'WARNING:dativa.tools.fastipf:ipf converged: convergence_rate below threshold'], l.output)

    def test_maximum_iterations_reached(self):
        ipf = Ipf(self.aggregates,
                  self.dimensions,
                  'total',
                  max_iteration=2, # only iterate twice
                  validate_marginals=True)

        with self.assertLogs('dativa.tools.fastipf', level=logging.WARNING) as l:
            ipf.run(self.df)

        self.assertEqual(['WARNING:dativa.tools.fastipf:Maximum iterations reached'], l.output)

    def test_conv_rate_below_tolerance(self):
        ipf = Ipf(self.aggregates,
                  self.dimensions,
                  'total',
                  convergence_rate=2e-30,  # too low conv rate
                  rate_tolerance=1000,  # too high tolerance
                  validate_marginals=True)

        with self.assertLogs('dativa.tools.fastipf', level=logging.WARNING) as l:
            ipf.run(self.df)

        self.assertEqual(['WARNING:dativa.tools.fastipf:ipf converged: convergence_rate not updating or below rate_tolerance'], l.output)