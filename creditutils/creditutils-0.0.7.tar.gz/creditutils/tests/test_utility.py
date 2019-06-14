# -*- coding:UTF-8 -*-
'''
Created on 2013-8-9

@author: caifenghua
'''
import unittest
import json
import datetime

import creditutils.trivial_util as myutility
import creditutils.file_util as myfile
import creditutils.base_util as base


def func_flag():
    pass  # do stuff


global __modpath__
__modpath__ = base.module_path(func_flag)


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_filter_unique_item(self):
        test_name = r'filter_unique_intput.txt'
        file_name = myfile.get_real_dir(__modpath__) + '\\' + test_name
        readed_lines = myfile.read_file_lines(file_name)
        src_list = []
        for item in readed_lines:
            src_list.append(item.strip())

        dst_list = myutility.filter_unique_item(src_list)

        expected = 5
        msg_format = 'expecte {0}, but {1}'
        self.assertEqual(expected, len(dst_list), msg_format.format(expected, len(dst_list)))


def testCJsonEncoder():
    data = {}
    data['date'] = datetime.datetime.now()
    str_ = json.dumps(data, ensure_ascii=False, cls=myutility.CJsonEncoder)
    print(str_)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    #     unittest.main()
    testCJsonEncoder()
