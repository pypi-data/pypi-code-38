'''
Created on 2016年5月30日

@author: caifh
'''
import unittest
import creditutils.zip_util as myzip
import pprint


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testName(self):
        pass


def test_zip_dir():
    src_path = r'E:\temp\crash\to_process'
    #     src_root = 'E:\temp'
    src_root = None
    dst_path = r'E:\temp\test_zip_02.zip'
    myzip.zip_dir(src_path, dst_path, src_root, to_print=True)

    src_path = r'E:\temp\crash\crash_info_201512011634.txt'
    dst_path = r'E:\temp\test_zip_01.zip'
    myzip.zip_dir(src_path, dst_path, to_print=True)


def test_zip_file():
    src_path = r'E:\temp\file_list.txt'
    dst_path = r'E:\temp\test_zip_02.zip'
    myzip.zip_file(src_path, dst_path, to_print=True)

    src_path = 'E:\\temp\\pack_config\\'
    dst_path = r'E:\temp\test_zip_02.zip'
    myzip.zip_file(src_path, dst_path, to_print=True)


def test_zip_item():
    src_path = 'E:\\temp\\pack_config\\'
    dst_path = r'E:\temp\test_zip_03.zip'
    myzip.zip_item(src_path, dst_path, to_print=True)

    src_path = r'E:\temp\file_list.txt'
    dst_path = r'E:\temp\test_zip_04.zip'
    myzip.zip_item(src_path, dst_path, to_print=True)


def test_unzip_specified_file():
    filepath = r'E:\temp\config\24695\android\config_file.zip'
    relative_path = r'config_file\version.txt'
    dst_dir = r'E:\temp\config\temp'
    dst_path = myzip.unzip_specified_file(filepath, relative_path, dst_dir)
    print(dst_path)


def test_append_file():
    filepath = r'E:\temp\test\src\config_file.zip'
    relative_path = 'config_file/file_list/list.txt'
    src_path = r'E:\temp\test\src\company_banner.png'
    myzip.append_file(filepath, relative_path, src_path)


def test_append_file_with_data():
    filepath = r'E:\temp\test\src\config_file.zip'
    relative_path = 'config_file/file_list/list.txt'
    data = 'nothing'
    myzip.append_file_with_data(filepath, relative_path, data)


def test_get_file_list():
    filepath = r'E:\temp\test\src\config_file.zip'
    result = myzip.get_file_list(filepath)
    pprint.pprint(result)


def test_append_file_with_original_file_list_data():
    filepath = r'E:\temp\test\src\config_file.zip'
    relative_path = 'config_file/file_list/list.txt'
    myzip.append_file_with_original_file_list_data(filepath, relative_path)


def test_main():
    #     test_unzip_specified_file()
    #     test_append_file()
    #     test_append_file_with_data()
    #     test_get_file_list()
    #     test_append_file_with_original_file_list_data()
    test_zip_dir()


#     test_zip_file()
#     test_zip_item()

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    #     unittest.main()

    test_main()

    print('to the end')
