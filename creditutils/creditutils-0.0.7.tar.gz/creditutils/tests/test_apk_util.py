# -*- coding:UTF-8 -*-

'''
Created on 2014年12月8日

@author: caifh
'''
import unittest
import creditutils.apk_util as apk_util
import creditutils.file_util as file_util


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testName(self):
        pass


def test_sign_apk():
    src_file = r'E:\temp\apk\3.5.4\3.5.4beta_p_01-487-20181206_sec_2.apk'
    dst_file = r'E:\temp\apk\3.5.4\3.5.4beta_p_01-487-20181206_sec_3.apk'
    keystore = r'D:\auto_build\pytxxy\project\develop\Android\pytxxy\pycreditKeystore'
    storepass = 'pycreditapkkey'
    storealias = 'pycreditKeystoreAlias'
    apk_util.sign_apk(keystore, storepass, storealias, src_file, dst_file)


def test_align_apk():
    src_file = r'E:\temp\apk\3.5.4\3.5.4beta_p_01-487-20181206_sec_1.apk'
    dst_file = r'E:\temp\apk\3.5.4\3.5.4beta_p_01-487-20181206_sec_2.apk'
    apk_util.zipalign(src_file, dst_file)


def test_align_check_apk():
    # src_file = r'E:\temp\apk\3.5.4\3.5.4beta_p_01-487-20181206_sec_1.apk'
    # src_file = r'E:\temp\apk\3.5.4\3.5.4beta_p_01-487-20181206_sec_2.apk'
    # src_file = r'E:\temp\apk\3.5.4\3.5.4beta_p_01-487-20181206_sec_3.apk'
    src_file = r'E:\temp\apk\3.5.4\3.5.4beta_p_01-487-20181206_sec_3.apk'
    result = apk_util.zipalign_check(src_file)
    info = "The file's align status: {}.".format(result)
    print(info)


def test_main():
    # test_sign_apk()
    # test_align_apk()
    test_align_check_apk()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    #     unittest.main()

    test_main()

    print('to the end')
