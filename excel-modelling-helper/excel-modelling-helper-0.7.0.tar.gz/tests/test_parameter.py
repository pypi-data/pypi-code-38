import unittest

import pandas as pd
from excel_helper import Parameter, DistributionFunctionGenerator, GrowthTimeSeriesGenerator
from scipy import stats


class ParameterTestCase(unittest.TestCase):
    def test_distribution_generate_values(self):
        p = Parameter('test', module_name='numpy.random', distribution_name='normal', param_a=0, param_b=.1)
        settings = {'sample_size': 32}
        a = p(settings)

        assert abs(stats.shapiro(a)[0] - 0.9) < 0.1

    def test_ExponentialGrowthTimeSeriesDistributionFunctionParameter_generate_values(self):
        p = Parameter('test', module_name='numpy.random', distribution_name='normal',
                      param_a=0,
                      param_b=.1)

        settings = {
            'use_time_series': True,
            'times': pd.date_range('2009-01-01',
                                   '2009-03-01',
                                   freq='MS'),
            'sample_size': 5,
            'cagr': 0.1}
        a = p(settings)

        print(a)
        # assert abs(stats.shapiro(a)[0] - 0.9) < 0.1

    def test_ExponentialGrowthTimeSeriesDistributionFunctionParameter_generate_values_uniform(self):
        p = Parameter('test', module_name='numpy.random', distribution_name='uniform',
                      param_a=1,
                      param_b=2)

        settings = {
            'use_time_series': True,
            'times': pd.date_range('2009-01-01',
                                   '2009-03-01',
                                   freq='MS'),
            'sample_size': 5,
            'cagr': 1}
        a = p(settings)

        print(a)
        # assert abs(stats.shapiro(a)[0] - 0.9) < 0.1

    def test_ExponentialGrowthTimeSeriesDistributionFunctionParameter_generate_values_uniform_mean(self):
        p = Parameter('test', module_name='numpy.random', distribution_name='uniform',
                      param_a=1, param_b=2, cagr=.1)

        settings = {
            'use_time_series': True,
            'times': pd.date_range('2009-01-01', '2010-01-01', freq='MS'),
            'sample_size': 1,
            'sample_mean_value': True}
        a = p(settings)

        assert a.iloc[0] * 1.1 == a.iloc[-1]

    def test_normal_zero_variance(self):
        p = Parameter('a', module_name='numpy.random', distribution_name='normal', param_a=0,
                      param_b=0, )
        q = Parameter('b', module_name='numpy.random', distribution_name='normal', param_a=0,
                      param_b=0)
        settings = {'sample_size': 64, }
        a = p(settings) * q(settings)
        # print(a)
        assert abs(stats.shapiro(a)[0] - 0.9) < 0.1

    def test_get_mean_uniform(self):
        p = Parameter('a', module_name='numpy.random', distribution_name='uniform', param_a=2,
                      param_b=4, )
        settings = {
            'sample_size': 5,
            'sample_mean_value': True}
        val = p(settings)
        # print(val)
        assert (val == 3).all()

    def test_get_mean_normal_timeseries(self):
        p = Parameter('test', module_name='numpy.random', distribution_name='normal',
                      param_a=3.,
                      param_b=.1, )

        settings = {
            'use_time_series': True,
            'times': pd.date_range('2009-01-01',
                                   '2009-03-01',
                                   freq='MS'),
            'sample_size': 5,
            'cagr': 0,
            'sample_mean_value': True}
        val = p(settings)
        # print(val)
        assert (val == 3).all()

    def test_get_mean_normal(self):
        p = Parameter('a', module_name='numpy.random', distribution_name='normal', param_a=3, param_b=4, )

        val = p()
        # print(val)
        # assert (val == 3).all()

    def test_get_mean_choice(self):
        p = Parameter('a', module_name='numpy.random', distribution_name='choice', param_a=3, param_b=4, )
        settings = {'sample_mean_value': True, 'sample_size': 3}
        val = p(settings)
        # print(val)
        assert (val == 3.5).all()

    def test_get_mean_numerically(self):
        p = Parameter('a', module_name='numpy.random', distribution_name='normal', param_a=3,
                      param_b=4)
        settings = {'sample_mean_value': True, 'sample_size': 3}
        val = p(settings)
        # print(val)
        assert (val == 3).all()


if __name__ == '__main__':
    unittest.main()
