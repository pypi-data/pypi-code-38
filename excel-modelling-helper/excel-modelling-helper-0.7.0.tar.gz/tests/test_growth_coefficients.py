import unittest
from datetime import datetime
import numpy as np
import pandas as pd

from excel_helper import ParameterRepository, ExcelParameterLoader, Parameter


class MyTestCase(unittest.TestCase):

    def test_negative_growth(self):
        """
        If start and end are one month apart, we expect an array of one row of ones of sample size for the ref month
        and one row with CAGR applied

        :return:
        """
        # samples = 3
        # alpha = -0.1  # 100 percent p.a.
        # ref_date = date(2009, 1, 1)
        # start_date = date(2009, 1, 1)
        # end_date = date(2010, 1, 1)
        # a = growth_coefficients(start_date, end_date, ref_date, alpha, samples)
        # print(a)
        # assert np.all(a[0] == np.ones((samples, 1)))
        # assert np.all(a[-1] == np.ones((samples, 1)) * 1 + alpha)

        ref_date = datetime(2014, 1, 1)
        ref_value = 9e-6
        p = Parameter('test', module_name='numpy.random', distribution_name='normal',
                      param_a=ref_value, param_b=9e-8, cagr=-0.2, ref_date=ref_date)

        date_values = [(datetime(2012, 1, 1), 1.30E-05), (datetime(2015, 1, 1), 7.20E-06),
                       (datetime(2016, 1, 1), 5.76E-06), (datetime(2017, 1, 1), 4.61E-06)]

        settings = {
            'use_time_series': True,
            'times': pd.date_range(date_values[0][0], '2017-01-01', freq='MS'),
            'sample_size': 1,
            'sample_mean_value': True
        }

        a = p(settings)

        a.mean(level='time').to_csv('check_cagr.csv')
        print(a.mean(level='time'))

        assert (a > 0).all()

        for date_value in date_values:
            assert np.all(np.abs(a.loc[date_value[0]] - date_value[1]) < 0.00001)

        assert np.all(a.loc[ref_date] == ref_value)

        # january = res.loc[[datetime(2009, 1, 1)]]
        # assert np.all(np.equal(january, np.ones(january.shape)))
        #
        # april = res.loc[[datetime(2009, 4, 1)]]
        # diff = april - np.ones(april.shape) * pow(1.1, 3. / 12)
        #
        # assert np.all(np.less(diff, np.ones(april.shape) * 0.00001))
        #
        # assert np.abs(res.loc[[datetime(2009, 4, 1)]][0] - pow(1.1, 3. / 12)) < 0.00001

    def test_ref_date_in_middle(self):
        """
        If start and end are one month apart, we expect an array of one row of ones of sample size for the ref month
        and one row with CAGR applied

        :return:
        """

        ref_date = datetime(2016, 1, 1)
        ref_value = 1.
        p = Parameter('test', module_name='numpy.random', distribution_name='normal',
                      param_a=ref_value, param_b=ref_value / 10, cagr=1, ref_date=ref_date)

        settings = {
            'use_time_series': True,
            'times': pd.date_range(datetime(2016, 1, 1), '2016-12-31', freq='MS'),
            'sample_size': 2,
            'sample_mean_value': True
        }

        a = p(settings)

        a.mean(level='time')  # .to_csv('check_cagr.csv')
        print(a.mean(level='time'))

    def test_ref_date_in_month_two(self):
        """
        If start and end are one month apart, we expect an array of one row of ones of sample size for the ref month
        and one row with CAGR applied

        :return:
        """

        ref_date = datetime(2016, 2, 1)
        ref_value = 1.
        p = Parameter('test', module_name='numpy.random', distribution_name='normal',
                      param_a=ref_value, param_b=ref_value / 10, cagr=0, ref_date=ref_date)

        settings = {
            'use_time_series': True,
            'times': pd.date_range(datetime(2016, 1, 1), '2016-12-31', freq='MS'),
            'sample_size': 2,
            'sample_mean_value': True
        }

        a = p(settings)

        a.mean(level='time')  # .to_csv('check_cagr.csv')
        print(a.mean(level='time'))

    def test_ref_date_at_start(self):
        """
        If start and end are one month apart, we expect an array of one row of ones of sample size for the ref month
        and one row with CAGR applied

        :return:
        """

        ref_date = datetime(2016, 1, 1)
        ref_value = 1.
        p = Parameter('test', module_name='numpy.random', distribution_name='normal',
                      param_a=ref_value, param_b=ref_value / 10, cagr=0, ref_date=ref_date)

        settings = {
            'use_time_series': True,
            'times': pd.date_range(datetime(2016, 1, 1), '2016-12-31', freq='MS'),
            'sample_size': 2,
            'sample_mean_value': True
        }

        a = p(settings)

        a.mean(level='time')  # .to_csv('check_cagr.csv')
        print(a.mean(level='time'))

    def test_ref_date_at_end(self):
        """
        If start and end are one month apart, we expect an array of one row of ones of sample size for the ref month
        and one row with CAGR applied

        :return:
        """

        ref_date = datetime(2016, 12, 31)
        ref_value = 1.
        p = Parameter('test', module_name='numpy.random', distribution_name='normal',
                      param_a=ref_value, param_b=ref_value / 10, cagr=0, ref_date=ref_date)

        settings = {
            'use_time_series': True,
            'times': pd.date_range(datetime(2016, 1, 1), '2016-12-31', freq='MS'),
            'sample_size': 2,
            'sample_mean_value': True
        }

        a = p(settings)

        a.mean(level='time')  # .to_csv('check_cagr.csv')
        print(a.mean(level='time'))

    def test_ref_date_before(self):
        """
        If start and end are one month apart, we expect an array of one row of ones of sample size for the ref month
        and one row with CAGR applied

        :return:
        """

        ref_date = datetime(2015, 6, 30)
        ref_value = 1.
        p = Parameter('test', module_name='numpy.random', distribution_name='normal',
                      param_a=ref_value, param_b=ref_value / 10, cagr=0.1, ref_date=ref_date)

        settings = {
            'use_time_series': True,
            'times': pd.date_range(datetime(2016, 1, 1), '2016-12-31', freq='MS'),
            'sample_size': 2,
            'sample_mean_value': True
        }

        a = p(settings)

        a.mean(level='time')  # .to_csv('check_cagr.csv')
        print(a.mean(level='time'))

    def test_ref_date_after(self):
        """
        If start and end are one month apart, we expect an array of one row of ones of sample size for the ref month
        and one row with CAGR applied

        :return:
        """

        ref_date = datetime(2017, 6, 30)
        ref_value = 1.
        p = Parameter('test', module_name='numpy.random', distribution_name='normal',
                      param_a=ref_value, param_b=ref_value / 10, cagr=.1, ref_date=ref_date)

        settings = {
            'use_time_series': True,
            'times': pd.date_range(datetime(2016, 1, 1), '2016-12-31', freq='MS'),
            'sample_size': 2,
            'sample_mean_value': True
        }

        a = p(settings)

        a.mean(level='time')  # .to_csv('check_cagr.csv')
        print(a.mean(level='time'))


if __name__ == '__main__':
    unittest.main()
