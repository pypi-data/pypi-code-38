#!/usr/bin/env python
#-*-coding: utf-8 -*-

import unittest
import sys

sys.path.append('..')
from hbase_util_thrift import *


class TestHbaseUtilLocal(unittest.TestCase):
    
    def test_1_put_col(self):
        res = put_col('kv_store_prd', 'row', 'data', 'key', 'val')
        self.assertTrue(res)

    def test_2_put_cols(self):
        res = put_cols(
                'kv_store_prd', 'wang', [('data', 'sex', 'female'), ('data', 'tag', '1')])
        self.assertTrue(res)

    def test_3_get_col(self):
        res = get_col('kv_store_prd', 'wang', 'data', 'sex')
        self.assertTrue(res)

    def test_4_get_cols(self):
        res = get_cols('kv_store_prd', 'wang', ['data:tag', 'data:sex', 'data:b'])
        self.assertTrue(res)

    def test_5_delete(self):
        res = delete('kv_store_prd', 'wang')
        self.assertTrue(res)

    def test_6_get_cols(self):
        res = get_cols('kv_store_prd', 'wang', ['data:tag', 'data:sex', 'data:b'])
        self.assertFalse(res)

if __name__ == '__main__':
    unittest.main()
