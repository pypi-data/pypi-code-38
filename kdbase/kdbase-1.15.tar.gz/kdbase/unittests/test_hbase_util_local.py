#!/usr/bin/env python
#-*-coding: utf-8 -*-

import unittest
import sys

sys.path.append('..')
from hbase_util_local import *


class TestHbaseUtilLocal(unittest.TestCase):

    def test_1_put_col(self):
        res = put_col('test', 'rowA', 'A', 'B', 'contentB')
        self.assertTrue(res)

    def test_get_col(self):
        res = get_col('test', 'rowA', 'A', 'B')
        self.assertTrue(res)

    def test_get_cols(self):
        res = get_cols('test', 'rowA', ['A:B'])
        self.assertTrue(res)
    

if __name__ == '__main__':
    unittest.main()
