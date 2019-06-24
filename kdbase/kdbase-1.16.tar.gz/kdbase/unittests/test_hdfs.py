#!/usr/bin/env python
#-*-coding: utf-8 -*-

import unittest
import sys
import json
import math
import traceback
import urllib2
from pyhdfs import HdfsClient

sys.path.append('..')
from hdfs import *
from log import logger
import service_config as config

class TestHbaseKvUtil(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        hadoop_namenode1 = config.GET_CONF('hadoop', 'hadoop_namenode1')
        hadoop_namenode2 = config.GET_CONF('hadoop', 'hadoop_namenode2')
        hadoop_home = config.GET_CONF('hadoop', 'hadoop_home')
        self.hdfs = Hdfs(hadoop_namenode1, hadoop_namenode2, hadoop_home)

    def test_mkdirs(self):
        res = self.hdfs.mkdirs('/tmp/tmp2')
        self.assertTrue(res)

    def test_upload_dir(self):
        res = self.hdfs.upload_dir('/mk', '/tmp/tmp2')
        self.assertFalse(res)

    def test_upload(self):
        res = self.hdfs.upload('./t.py', '/tmp/tmp2')
        self.assertFalse(res)
    
    def test_download(self):
        res = self.hdfs.download('/user/hwl/par.jar', './')
        self.assertFalse(res)

    def test_get_content_sum(self):
        res = self.hdfs.get_content_sum('/production/service-storage/step2/streaming_output/400110713_1_kss-upload-mapreduce_null_test/part-00000/data')
        self.assertTrue(res)

    def test_download_dir(self):
        res = self.hdfs.download_dir('/tmp/logs', './tmp/tmp2')
        self.assertFalse(res)
    
    def test_create_file(self):
        res = self.hdfs.create_file('/tmp/6688.txt', 'tom', True)
        self.assertTrue(res)

    def test_append(self):
        res = self.hdfs.append('/tmp/6688.txt', 'tom\n')
        self.assertTrue(res)
    
    def test_delete(self):
        res = self.hdfs.delete('/tmp/6688.txt')
        self.assertTrue(res)
    
    def test_get_file_checksum(self):
        res = self.hdfs.get_file_checksum('/production/service-storage/step2/streaming_output/400110713_1_kss-upload-mapreduce_null_test/part-00000/data')
        self.assertTrue(res)

    def test_get_file_status(self):
        res = self.hdfs.get_file_status('/production/service-storage/step2/streaming_output/400110713_1_kss-upload-mapreduce_null_test/part-00000/data')
        self.assertTrue(res)

    def test_listdir(self):
        res = self.hdfs.listdir('/tmp')
        self.assertTrue(res)

    def test_exists(self):
        res = self.hdfs.exists('/tmp/timer.py')
        self.assertTrue(res)

    def test_set_xattr(self):
        res = self.hdfs.set_xattr('/production/service-storage/step2/streaming_output/400110713_1_kss-upload-mapreduce_null_test/part-00000/data', 'user.addr', 'bj', 'REPLACE')
        self.assertFalse(res)

    def test_get_xattr(self):
        res = self.hdfs.get_xattr('/production/service-storage/step2/streaming_output/400110713_1_kss-upload-mapreduce_null_test/part-00000/data', 'user.addr')
        self.assertFalse(res)
    
    def test_download_native(self):
        res = self.hdfs.download_native('/user/hwl/par.jar', './')
        self.assertTrue(res)
    
    def test_download_py(self):
        res = self.hdfs.download_py('/tmp/timer.py', './timer.py')
        self.assertTrue(res)

    def test_get_job_id(self):
        res = self.hdfs.get_job_id('element_400051160_1-class')
        self.assertTrue(res)

    def test_get_job_progress(self):
        res = self.hdfs.get_job_progress('element_400051160_1-class')
        self.assertTrue(res)

    def test_get_active_namenode(self):
        res = self.hdfs.get_active_namenode()
        self.assertTrue(res)

    def test_list_xattrs(self):
        res = self.hdfs.list_xattrs('/test/input/dq/test1')
        self.assertTrue(res)

  
if __name__ == '__main__':
    unittest.main()

