# -*- coding:UTF-8 -*-

'''
Created on 2013-7-12

@author: caifenghua
'''
import unittest

import pprint

import creditutils.file_util as myfile
import creditutils.base_util as base
import os


def func_flag():
    pass  # do stuff


global __modpath__
__modpath__ = base.module_path(func_flag)


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_read_file_content(self):
        # GB2312 编码格式文件验证
        ori_content = '这只是一个测试文件。'
        test_name = r'for_test.txt'
        file_name = myfile.get_real_dir(__modpath__) + os.sep + test_name
        readed_content = myfile.read_file_content(file_name)

        msg_format = 'expecte {0}, but {1}'
        self.assertEqual(ori_content, readed_content, msg_format.format(ori_content, readed_content))

        # UTF8 with BOM 编码格式文件验证
        ori_content = 'utf-8-sig及中文验证;'
        test_name = r'utf_8_sig.txt'
        file_name = myfile.get_real_dir(__modpath__) + os.sep + test_name
        readed_content = myfile.read_file_content(file_name)

        msg_format = 'expecte {0}, but {1}'
        self.assertEqual(ori_content, readed_content, msg_format.format(ori_content, readed_content))

    def test_write_to_file(self):
        content = "info to write"

        dst_name = r'file_output.txt'
        dst_file = myfile.get_real_dir(__modpath__) + os.sep + dst_name
        myfile.write_to_file(dst_file, content)

        readed_content = myfile.read_file_content(dst_file)

        msg_format = 'expecte {0}, but {1}'
        self.assertEqual(content, readed_content, msg_format.format(content, readed_content))

    def test_detect_file_enc(self):
        test_name = r'for_test.txt'
        file_name = myfile.get_real_dir(__modpath__) + os.sep + test_name
        enc_result = myfile.detect_file_enc(file_name)

        expecte = 'GB2312'
        msg_format = 'expecte {0}, but {1}'
        self.assertEqual(expecte, enc_result['encoding'], msg_format.format(expecte, enc_result['encoding']))

        test_name = r'alias_example.txt'
        file_name = myfile.get_real_dir(__modpath__) + os.sep + test_name
        enc_result = myfile.detect_file_enc(file_name)

        expecte = 'utf-8'
        msg_format = 'expecte {0}, but {1}'
        self.assertEqual(expecte, enc_result['encoding'], msg_format.format(expecte, enc_result['encoding']))

        test_name = r'utf_8_sig.txt'
        file_name = myfile.get_real_dir(__modpath__) + os.sep + test_name
        enc_result = myfile.detect_file_enc(file_name)

        expecte = 'utf-8-sig'
        msg_format = 'expecte {0}, but {1}'
        self.assertEqual(expecte, enc_result['encoding'], msg_format.format(expecte, enc_result['encoding']))

    def test_get_dict_from_file(self):
        alias_file = 'alias_example.txt'
        file_name = myfile.get_real_dir(__modpath__) + os.sep + alias_file
        dict_ = myfile.get_dict_from_file(file_name)
        key = 'BTV文艺'
        value = '北京文艺'
        msg_format = 'expecte {0}, but {1}'
        self.assertEqual(dict_[key], value, msg_format.format(value, dict_[key]))

        key = 'BTV科教'
        value = '北京科教'
        msg_format = 'expecte {0}, but {1}'
        self.assertEqual(dict_[key], value, msg_format.format(value, dict_[key]))

        key = 'what'
        msg_format = 'expecte {0}, but {1}'
        self.assertFalse(key in dict_, msg_format.format(False, True))

        key = 'BTV科教'
        msg_format = 'expecte {0}, but {1}'
        self.assertTrue(key in dict_, msg_format.format(False, True))

    def test_replace_string_in_file(self):
        test_name = 'gbk.txt'
        ori_data = '这是一个文件，用于进行测试。what are you doing.'
        file_name = myfile.get_real_dir(__modpath__) + os.sep + test_name

        expect_data = ori_data
        file_data = myfile.read_file_content(file_name)
        msg_format = 'expecte {0}, but {1}'
        self.assertEqual(expect_data, file_data, msg_format.format(expect_data, file_data))

        enc_result = myfile.detect_file_enc(file_name)
        expect_data = 'gb2312'
        encoding = enc_result['encoding'].lower()
        self.assertEqual(expect_data, encoding, msg_format.format(expect_data, encoding))

        src_dst_list = list(zip(['what'], ['Fuck']))
        enc_result = myfile.replace_string_in_file(file_name, src_dst_list)
        expect_data = '这是一个文件，用于进行测试。Fuck are you doing.'
        file_data = myfile.read_file_content(file_name)
        self.assertEqual(expect_data, file_data, msg_format.format(expect_data, file_data))

        enc_result = myfile.detect_file_enc(file_name)
        expect_data = 'gb2312'
        encoding = enc_result['encoding'].lower()
        self.assertEqual(expect_data, encoding, msg_format.format(expect_data, encoding))

        myfile.write_to_file(file_name, ori_data, encoding)

    def test_import_code(self):
        code = """paras_table = [0,1]"""
        module = myfile.import_code(code, "just_for_test")
        msg_format = 'expecte {0}, but {1}'
        self.assertEqual(module.paras_table[0], 0, msg_format.format(0, module.paras_table[0]))

    def test_read_file_first_line(self):
        test_name = r'upgrade.xml'
        file_name = myfile.get_real_dir(__modpath__) + os.sep + test_name
        first_line = myfile.read_file_first_line(file_name)

        expect_data = '<?xml version="1.0" encoding="utf-8"?>\r\n'
        msg_format = 'expecte {0}, but {1}'
        self.assertEqual(expect_data, first_line, msg_format.format(expect_data, first_line))


def test_read_valid_string_list_from_file():
    test_name = r'test_valid_string_list.txt'
    file_name = myfile.get_real_dir(__modpath__) + os.sep + test_name
    valid_list = myfile.read_valid_string_list_from_file(file_name)
    pprint.pprint(valid_list)


def test_get_children():
    src_dir = r'D:\temp'
    pprint.pprint(myfile.get_child_dirs(src_dir))
    pprint.pprint(myfile.get_child_files(src_dir))

    pprint.pprint(myfile.get_child_dirs())
    pprint.pprint(myfile.get_child_files())


def test_get_file_list():
    src_dir = r'D:\temp'
    pprint.pprint(myfile.get_file_list(src_dir, '/'))


def test_main():
    #     test_read_valid_string_list_from_file()
    #     test_get_children()
    test_get_file_list()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    #     unittest.main()

    #     import creditutils.myunittest as myunittest
    #     unittest.main(testRunner=myunittest.TestRunner())

    test_main()

    print('to the end')
