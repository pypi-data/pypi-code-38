# -*- coding:UTF-8 -*-


'''
Created on 2013年10月28日

@author: work_cfh
'''
import unittest
import creditutils.apk_util as apk
import pprint


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testName(self):
        pass


def test_extract_apk_info():
    apk_path = r'D:\temp\83860_544781eb-1c79-4b3b-a49d-89ff124c220d.apk'
    #     apk_path = r'D:\temp\qing.apk'

    exePath = r'D:\workspace\ApkInstalling\build\exe.win32-2.7'
    apkInfoPath = r'D:\temp\apkInfo'
    extractor = apk.Extractor(exePath, apkInfoPath)
    apkInfo = extractor.extract_apk_info(apk_path)
    pprint.pprint(apkInfo)


def test_sign_apk():
    keystore = r'D:\auto_build\pytxxy\projects\pytxxy\pytxxy\pycreditKeystore'
    storepass = 'pycreditapkkey'
    store_alias = 'pycreditKeystoreAlias'
    signer = apk.ApkSigner(keystore, storepass, store_alias)

    src_path = r'D:\programs\shieldpy_v4\upload\3.0.0beta_p_12-294-20170401_sec.apk'
    dst_path = r'D:\programs\shieldpy_v4\upload\3.0.0beta_p_12-294-20170401_sec_signed.apk'
    signer.sign(src_path, dst_path)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    #     unittest.main()
    #     test_extract_apk_info()
    test_sign_apk()

    print('to the end!')
