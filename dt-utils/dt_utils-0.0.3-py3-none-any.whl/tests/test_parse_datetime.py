# -*- coding:utf-8 -*-

import six
import unittest
from hypothesis import given
import hypothesis.strategies as st
import hypothesis.extra.numpy as np_st

import numpy as np
from dt_utils.parsers import *


class TestParseDatetime(unittest.TestCase):
    @given(st.datetimes(min_value=datetime(1900, 1, 1)))
    def test_single_integer(self, raw_dt):
        for fmt in ('%Y%m%d', '%Y%m%d%H', '%Y%m%d%H%M', '%Y%m%d%H%M%S'):
            dt_num = int(raw_dt.strftime(fmt))
            parsed = T(dt_num)
            self.assertEqual(raw_dt.strftime(fmt), parsed.strftime(fmt), msg='Test Single Integer, fmt: {}, raw: {}, parsed: {}'.format(fmt, raw_dt, parsed))

    @given(st.datetimes(min_value=datetime(1900, 1, 1)))
    def test_single_str(self, raw_dt):
        for fmt in (
            '%Y%m%d', '%Y%m%d%H', '%Y%m%d%H%M', '%Y%m%d%H%M%S',
            '%Y-%m-%d', '%Y/%m/%d',
            '%Y-%m-%d %H',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%dT%H:%M:%S',
            '%Y%j',
            '%Y%j%H'
        ):
            dt_str = raw_dt.strftime(fmt)
            parsed = T(dt_str)
            self.assertEqual(raw_dt.strftime(fmt), parsed.strftime(fmt), msg='Test Single String, fmt: {}, raw: {}, parsed: {}'.format(fmt, raw_dt, parsed))

    @given(st.lists(st.datetimes(min_value=datetime(1900, 1, 1))))
    def test_list(self, raw_dts):
        for fmt in ('%Y%m%d', '%Y%m%d%H', '%Y%m%d%H%M', '%Y%m%d%H%M%S'):
            raw_list = [dt.strftime(fmt) for dt in raw_dts]
            parsed = T(raw_list)
            self.assertEqual(type(parsed), list)
            parsed_strlist = [dt.strftime(fmt) for dt in parsed]
            self.assertListEqual(raw_list, parsed_strlist)

    @given(st.lists(st.datetimes(min_value=datetime(1900, 1, 1))))
    def test_array(self, raw_dts):
        for fmt in ('%Y%m%d', '%Y%m%d%H', '%Y%m%d%H%M', '%Y%m%d%H%M%S'):
            raw_list = [dt.strftime(fmt) for dt in raw_dts]
            raw_array = np.array(raw_list)
            parsed = T(raw_array)
            self.assertEqual(type(parsed), np.ndarray)
            parsed_strlist = [dt.strftime(fmt) for dt in parsed]
            self.assertListEqual(raw_list, parsed_strlist)


if __name__ == '__main__':
    unittest.main()