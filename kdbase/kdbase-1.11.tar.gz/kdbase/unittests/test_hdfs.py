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
from hbase_kv_util import *
from log import logger
import service_config as config

class TestHbaseKvUtil(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        hadoop_namenode1 = config.GET_CONF('hadoop', 'hadoop_namenode1')
        hadoop_namenode2 = config.GET_CONF('hadoop', 'hadoop_namenode2')
        hadoop_home = config.GET_CONF('hadoop', 'hadoop_home')
        self.hdfs = Hdfs(hadoop_namenode1, hadoop_namenode2, hadoop_home)

    def test_upload_dir(self):
        res = self.hdfs.upload_dir('./base', '/tmp')
        self.assertTrue(res)

    def test_upload(self):
        res = self.hdfs.upload('./log.py', '/tmp')
        self.assertTrue(res)

    def test_delete(self):
        res = self.hdfs.delete('/tmp/t.txt')
        self.assertTrue(res)

    def test_download(self):
        res = self.hdfs.download('/user/hwl/par.jar', './')
        self.assertTrue(res)

    def test_get_content_sum(self):
        res = self.hdfs.get_content_sum('/production/service-storage/step2/streaming_output/400106787_1_kss-upload-mapreduce_null_6758929')
        self.assertTrue(res)

    def test_download_dir(self):
        res = self.hdfs.download_dir('/tmp/output/protocol', './')
        self.assertTrue(res)
    
    def test_mkdirs(self):
        res = self.hdfs.mkdirs('/tmp/a/s/d')
        self.assertTrue(res)

    def test_create_file(self):
        res = self.hdfs.create_file('/tmp/6688.txt', 'tom', False)
        self.assertTrue(res)

    def test_append(self):
        res = self.hdfs.append('/tmp/6688.txti', 'tom\n')
        self.assertTrue(res)

    def test_get_file_checksum(self):
        res = self.hdfs.get_file_checksum('/user/hwl/input/test4')
        self.assertTrue(res)

    def test_get_file_status(self):
        res = self.hdfs.get_file_status('/user/hwl/input/test4')
        self.assertTrue(res)

    def test_listdir(self):
        res = self.hdfs.listdir('/production/version1/auto/input')
        self.assertTrue(res)

    def test_exists(self):
        res = self.hdfs.exists('/tmp/t.txt')
        self.assertTrue(res)

    def test_set_xattr(self):
        res = self.hdfs.set_xattr('/user/hwl/input/test4', 'user.addr', 'bj', 'REPLACE')
        self.assertTrue(res)

    def test_get_xattr(self):
        res = self.hdfs.get_xattr('/user/hwl/input/test4', 'user.atime')
        self.assertTrue(res)

    def test_download_native(self):
        res = self.hdfs.download_native('/user/hwl/par.jar', './')
        self.assertTrue(res)
    
    def test_download_py(self):
        res = self.hdfs.download_py('/user/hwl/par.jar', './')
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
        res = self.hdfs.list_xattrs('/user/hwl/input/test4')
        self.assertTrue(res)


if __name__ == '__main__':
    unittest.main()

