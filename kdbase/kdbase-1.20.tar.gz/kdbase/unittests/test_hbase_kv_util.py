#!/usr/bin/env python
#-*-coding: utf-8 -*-

import unittest
import sys

sys.path.append('..')
from hbase_kv_util import *


class TestHbaseKvUtil(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.kv_url = 'http://192.168.8.16:9527/prd/kv/get/v2'
        self.key = '400110713_20190325160823858'
        self.namespace = 'recognition_quality'

    def test_hbase_kv_get(self):
        res = hbase_kv_get(self.kv_url, self.key, self.namespace)
        self.assertTrue(res)



if __name__ == '__main__':
    unittest.main()
