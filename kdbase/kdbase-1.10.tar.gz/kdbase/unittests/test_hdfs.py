#!/usr/bin/env python
#-*-coding: utf-8 -*-

import unittest
import sys

sys.path.append('..')
from hbase_kv_util import *


class TestHbaseKvUtil(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        hadoop_namenode1 = config.GET_CONF('hadoop', 'hadoop_namenode1')
        hadoop_namenode2 = config.GET_CONF('hadoop', 'hadoop_namenode2') 
        hadoop_home = config.GET_CONF('hadoop', 'hadoop_home')
        self.hdfs=Hdfs(hadoop_namenode1, hadoop_namenode2, hadoop_home)
    
    def test_upload_dir(self):
        res = self.hdfs.upload_dir('./base','/tmp')
        self.assertTrue(res)
    
    def test_upload(self):
        res = self.hdfs.upload('./log.py','/tmp')
        self.assertTrue(res)
    
    def test_delete(self):
        res = self.hdfs.delete('/tmp/t.txt')
        self.assertTrue(res)

    def test_download(self):
        res = self.hdfs.download('/user/hwl/par.jar','./')
        self.assertTrue(res)
    
    def test_download_dir(self):
        res = self.hdfs.download_dir('/tmp/output/protocol','./')
        self.assertTrue(res)

 
    def test_mkdirs(self):
        res = self.hdfs.mkdirs('/tmp/a/s/d')
        self.assertTrue(res)

    def test_upload_dir_v(self):
        res = self.hdfs.upload_dir_v2('./base','/tmp')
        self.assertTrue(res)

    def test_download_dir_v2(self):
        res = self.hdfs.download_dir_v2('/tmp/input','./')
        self.assertTrue(res)
    
    def test_create_file(self):
        res = self.hdfs.create_file('/tmp/6688.txt','tom', False)
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

    def test_upload_dir(self):
        res = self.hdfs.upload_dir('./base','/tmp')
        self.assertTrue(res)
    
    def test_upload(self):
        res = self.hdfs.upload('./log.py','/tmp')
        self.assertTrue(res)


if __name__ == '__main__':
    unittest.main()
