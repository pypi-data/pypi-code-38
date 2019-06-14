# -*- coding:UTF-8 -*-

'''
Created on 2014年11月12日

@author: caifh
'''
import unittest

import creditutils.base_util as base
import creditutils.file_util as myfile
import creditutils.hash_util as myhash


def func_flag():
    pass  # do stuff


global __modpath__
__modpath__ = base.module_path(func_flag)


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_file_md5(self):
        test_name = r'gbk.txt'
        file_name = myfile.get_real_dir(__modpath__) + '\\' + test_name
        file_md5 = myhash.get_file_md5(file_name)

        ori_md5 = '71BC7781C1AF31B3F50FFF631FA80852'
        expected = ori_md5.lower()
        msg_format = 'expecte {0}, but {1}'
        self.assertEqual(expected, file_md5.lower(), msg_format.format(expected, file_md5.lower()))

    def test_get_data_md5(self):
        ori_data = 'what are you doing here!'
        data_md5 = myhash.get_data_md5(ori_data)

        ori_md5 = '5d61eef139897ae53715e77d6b7cf8e7'
        expected = ori_md5.lower()
        msg_format = 'expecte {0}, but {1}'
        self.assertEqual(expected, data_md5.lower(), msg_format.format(expected, data_md5.lower()))

    def test_get_file_sha1(self):
        test_name = r'gbk.txt'
        file_name = myfile.get_real_dir(__modpath__) + '\\' + test_name
        file_sha1 = myhash.get_file_sha1(file_name)

        ori_sha1 = '6B497D040B40DDA36C53E7F96BE12390602523B1'
        expected = ori_sha1.lower()
        msg_format = 'expecte {0}, but {1}'
        self.assertEqual(expected, file_sha1.lower(), msg_format.format(expected, file_sha1.lower()))

    def test_get_data_sha1(self):
        ori_data = 'what are you doing here!'
        data_sha1 = myhash.get_data_sha1(ori_data)

        ori_sha1 = '6EDF594AADEBC525232809A54CE0EB4486F0DA5A'
        expected = ori_sha1.lower()
        msg_format = 'expecte {0}, but {1}'
        self.assertEqual(expected, data_sha1.lower(), msg_format.format(expected, data_sha1.lower()))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
