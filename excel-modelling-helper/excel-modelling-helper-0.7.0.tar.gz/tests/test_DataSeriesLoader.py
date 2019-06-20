import unittest
from datetime import datetime

import numpy as np
import pandas as pd

from excel_helper.helper import DataSeriesLoader


class TestDataFrameWithCAGRCalculation(unittest.TestCase):
    def test_simple_CAGR(self):
        """
        Basic test case, applying CAGR to a Pandas Dataframe.

        :return:
        """
        # the time axis of our dataset
        times = pd.date_range('2009-01-01', '2009-04-01', freq='MS')
        # the sample axis our dataset
        samples = 2

        dfl = DataSeriesLoader.from_excel('test.xlsx', times, size=samples, sheet_index=0)
        res = dfl['static_one']
        print (res)
        assert res.loc[[datetime(2009, 1, 1)]][0] == 1
        assert np.abs(res.loc[[datetime(2009, 4, 1)]][0] - pow(1.1, 3. / 12)) < 0.00001

    def test_CAGR_ref_date_within_bounds(self):
        """
        Basic test case, applying CAGR to a Pandas Dataframe.

        :return:
        """
        # the time axis of our dataset
        times = pd.date_range('2009-01-01', '2009-04-01', freq='MS')
        # the sample axis our dataset
        samples = 2

        dfl = DataSeriesLoader.from_excel('test.xlsx', times, size=samples, sheet_index=0)
        res = dfl['static_one']

        assert res.loc[[datetime(2009, 1, 1)]][0] == 1
        assert np.abs(res.loc[[datetime(2009, 4, 1)]][0] - pow(1.1, 3. / 12)) < 0.00001

    def test_CAGR_ref_date_before_start(self):
        """
        Basic test case, applying CAGR to a Pandas Dataframe.

        :return:
        """
        # the time axis of our dataset
        times = pd.date_range('2009-01-01', '2009-04-01', freq='MS')
        # the sample axis our dataset
        samples = 2

        dfl = DataSeriesLoader.from_excel('test.xlsx', times, size=samples, sheet_index=0)
        # equivalent to dfl['test_ref_date_before_start']
        self.assertRaises(AssertionError, dfl.__getitem__, 'test_ref_date_before_start')

    def test_CAGR_ref_date_after_end(self):
        """
        Basic test case, applying CAGR to a Pandas Dataframe.

        :return:
        """
        # the time axis of our dataset
        times = pd.date_range('2009-01-01', '2009-04-01', freq='MS')
        # the sample axis our dataset
        samples = 2

        dfl = DataSeriesLoader.from_excel('test.xlsx', times, size=samples, sheet_index=0)
        # equivalent to dfl['test_ref_date_before_start']
        self.assertRaises(AssertionError, dfl.__getitem__, 'test_ref_date_after_end')

    def test_simple_CAGR_from_pandas(self):
        times = pd.date_range('2009-01-01', '2009-04-01', freq='MS')

        xls = pd.ExcelFile('test.xlsx')
        df = xls.parse('Sheet1')
        ldr = DataSeriesLoader.from_dataframe(df, times, size=2)
        res = ldr['static_one']

        assert res.loc[[datetime(2009, 1, 1)]][0] == 1
        assert np.abs(res.loc[[datetime(2009, 4, 1)]][0] - pow(1.1, 3. / 12)) < 0.00001

    def test_simple_CAGR_mm(self):
        """
        Basic test case, applying CAGR to a Pandas Dataframe.

        :return:
        """
        # the time axis of our dataset
        times = pd.date_range('2015-01-01', '2016-01-01', freq='MS')
        # the sample axis our dataset
        samples = 2

        dfl = DataSeriesLoader.from_excel('test.xlsx', times, size=samples, sheet_index=0)
        res = dfl['mm']
        print(res)
        # assert res.loc[[datetime(2009, 1, 1)]][0] == 1
        # assert np.abs(res.loc[[datetime(2009, 4, 1)]][0] - pow(1.1, 3. / 12)) < 0.00001


if __name__ == '__main__':
    unittest.main()
