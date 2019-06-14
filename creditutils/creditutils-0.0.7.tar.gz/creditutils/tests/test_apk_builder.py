'''
Created on 2014年5月5日

@author: work_cfh
'''
import unittest

import creditutils.base_util as base
import creditutils.file_util as myfile
import creditutils.apk_builder_util as apk_builder
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

    def testName(self):
        pass


def test_read_valid_string_list_from_file():
    test_name = r'AndroidManifest.xml'
    file_name = myfile.get_real_dir(__modpath__) + '\\' + test_name
    updater = apk_builder.VersionConfigUpdater(file_name, False)

    print('original version code: ' + updater.version_code)
    print('original version name: ' + updater.version_name)
    print()

    updater.update_version_config()

    print('new version code: ' + updater.version_code)
    print('new version name: ' + updater.version_name)


def test_ManifestVerInfoUpdater():
    test_name = r'AndroidManifest.xml'
    file_name = r'D:\temp' + os.sep + test_name
    updater = apk_builder.ManifestVerInfoUpdater(file_name)
    print('original version code: ' + updater.version_code)
    print('original version name: ' + updater.version_name)

    updater.update_version_config('14', 'what_are_you')

    print('new version code: ' + updater.version_code)
    print('new version name: ' + updater.version_name)


def test_ManifestConfigInfoUpdater():
    test_name = r'AndroidManifest.xml'
    file_name = r'E:\temp\test\meta_data' + os.sep + test_name
    updater = apk_builder.ManifestConfigInfoUpdater(file_name)
    mata_data_name = 'jpush_appkey'
    print('original jpush_appkey: ' + updater.get_single_meta_data(mata_data_name))

    ori_value = 'null'
    updater.update_single_meta_data(mata_data_name, ori_value)

    new_updater = apk_builder.ManifestConfigInfoUpdater(file_name)
    value = new_updater.get_single_meta_data(mata_data_name)
    if ori_value == value:
        print('update jpush_appkey success with {}.'.format(value))
    else:
        print('update jpush_appkey failed with {}!'.format(value))


def test_StringItemUpdater():
    test_name = r'strings.xml'
    file_name = r'E:\temp\test\android_res' + os.sep + test_name
    updater = apk_builder.StringItemUpdater(file_name)
    str_item_name = 'app_name'
    print('original app_name: ' + updater.get_single_item_value(str_item_name))

    ori_value = '天下信用-信用查询'
    updater.update_single_item(str_item_name, ori_value)

    new_updater = apk_builder.StringItemUpdater(file_name)
    value = new_updater.get_single_item_value(str_item_name)
    if ori_value == value:
        print('update app_name success with {}.'.format(value))
    else:
        print('update app_name failed with {}!'.format(value))


def test_main():
    #     test_read_valid_string_list_from_file()
    #     test_ManifestVerInfoUpdater()
    #     test_ManifestConfigInfoUpdater()
    test_StringItemUpdater()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    #     unittest.main()

    test_main()

    print()
    print('to the end')
