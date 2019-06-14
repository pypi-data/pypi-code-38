# -*- coding:UTF-8 -*-

'''
Created on 2014年12月8日

@author: caifh
'''
import unittest
import creditutils.svn_util as svn
import os
import creditutils.file_util as myfile
import pprint


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testName(self):
        pass


def test_revert_with_default_arg():
    src_dir = r'D:\version_build\pytxxy\pytxxy'
    dir_ = os.getcwd()
    os.chdir(src_dir)
    svn.revert()
    os.chdir(dir_)


def test_revert():
    src_dir = r'D:\version_build\pytxxy\pytxxy'
    svn.revert(src_dir)


def test_update():
    src_dir = r'D:\version_build\pytxxy\pytxxy'
    svn.update(src_dir)


def test_update_with_specified_revision():
    src_dir = r'D:\version_build\pytxxy\pytxxy'
    svn.update(src_dir, 3885)


def test_status():
    src_dir_01 = r'D:\version_build\pytxxy\pytxxy'
    print(svn.status(src_dir_01))

    src_dir_02 = r'D:\temp'
    print(svn.status(src_dir_02))


def test_get_statuses():
    src_dir_01 = r'D:\version_build\pytxxy'
    statuses_01 = svn.get_statuses(myfile.get_child_dirs(src_dir_01))
    pprint.pprint(statuses_01)

    src_dir_02 = r'D:\temp'
    statuses_02 = svn.get_statuses(myfile.get_child_dirs(src_dir_02))
    print(statuses_02)


def test_checkout():
    dst_dir = r'E:\temp\pytxxy\pytxxy'
    url = ''
    svn.checkout(url, dst_dir)
    print('to the end')


def test_checkout_with_specified_revision():
    dst_dir = r'E:\temp\pytxxy\PYCreditAF'
    url = ''
    svn.checkout(url, dst_dir, 3900)
    print('to the end')


def test_checkout_with_default_dir():
    dst_dir = r'E:\temp\svn_test'
    dir_ = os.getcwd()
    os.chdir(dst_dir)

    url = ''
    try:
        svn.checkout(url)
    finally:
        os.chdir(dir_)

    print('to the end')


def test_get_revision():
    #     dst_dir = r'D:\repository\config_file'
    #     dst_dir = r'D:\repository\build_script'
    #     dst_dir = r'D:\repository\upgrade_demo'
    dst_dir = r'/Users/caifh/Documents/AutoBuild/projects/pycredit'
    ver_code = svn.get_revision(dst_dir)
    print(str(ver_code))


def test_add():
    paths = []
    paths.append(r'D:\repository\upgrade_demo\are')
    paths.append(r'D:\repository\upgrade_demo\what')
    svn.add(paths)


def test_commit():
    paths = []
    paths.append(r'D:\repository\upgrade_demo\are')
    paths.append(r'D:\repository\upgrade_demo\what')
    msg = 'It is just for test.'
    svn.commit(msg, paths)


def test_main():
    #     test_revert_with_default_arg()
    #     test_revert()
    #     test_update()
    #     test_update_with_specified_revision()
    #     test_status()
    #     test_get_statuses()
    #     test_checkout()
    #     test_checkout_with_specified_revision()
    #     test_checkout_with_default_dir()
    test_get_revision()


#     test_add()
#     test_commit()

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    #     unittest.main()

    test_main()

    print('to the end')
