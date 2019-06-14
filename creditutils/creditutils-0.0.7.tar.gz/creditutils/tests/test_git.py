# -*- coding:UTF-8 -*-
'''
Created on 2017年6月17日

@author: caifh
'''
import unittest
import creditutils.git_util as git
import creditutils.file_util as myfile
import shutil
import os
from build_txxy import checkout_or_update


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testName(self):
        pass


def test_clone():
    url = 'git@gitlab.app.com:iOS/pytxxy.git'
    dst_path = '/Users/caifh/Documents/git_test/test'
    if os.path.isdir(dst_path):
        shutil.rmtree(dst_path)
        os.makedirs(dst_path)

    git.clone(url, dst_path)


def test_clone_with_revision():
    url = 'git@gitlab.app.com:iOS/pytxxy.git'
    dst_path = '/Users/caifh/Documents/git_test/test'
    revision = '9f6854dc1a505b11e55616d93b0e98ac91905ec9'

    if os.path.isdir(dst_path):
        shutil.rmtree(dst_path)
        os.makedirs(dst_path)

    git.clone(url, dst_path, revision)


def test_revert():
    dst_path = '/Users/caifh/Documents/git_test/test'
    git_root = git.get_git_root(dst_path)
    git.revert(git_root)


def test_get_revision():
    src_path = '/Users/caifh/Documents/git_test/temp/pytxxy'
    print(git.get_revision(src_path))


def test_update():
    src_path = '/Users/caifh/Documents/git_test/test/pytxxy'
    git.update(src_path)


def test_update_with_revision():
    src_path = '/Users/caifh/Documents/git_test/test/pytxxy'
    revision = '698dce20320e25465a40a37040bf6a72ae64075b'
    git.update(src_path, revision)
    got_revision = git.get_revision(src_path)
    if revision == got_revision:
        print('Success.')
    else:
        print('Failed, expecting {} but got {}!'.format(revision, got_revision))


def test_add():
    src_path = '/Users/caifh/Documents/git_test/test/pytxxy/Projects/pytxxy_ios/pytxxy_ios'
    items = []
    items.append('../init.rb')
    items.append('PYMonitor.h')
    git.add(items, src_path)


def test_checkout_or_update():
    url = 'git@gitlab.app.com:iOS/pytxxy.git'
    dst_path = '/Users/caifh/Documents/git_test/test'
    revision = '9f6854dc1a505b11e55616d93b0e98ac91905ec9'

    if os.path.isdir(dst_path):
        shutil.rmtree(dst_path)

    git.checkout_or_update(dst_path, url, revision)

    git.checkout_or_update(dst_path, url, revision)


def test_main():
    #     test_get_revision()
    #     test_clone()
    #     test_clone_with_revision()
    #     test_revert()
    #     test_update()
    #     test_update_with_revision()
    #     test_add()
    test_checkout_or_update()
    pass


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    #     unittest.main()

    test_main()
    print('to the end!')
