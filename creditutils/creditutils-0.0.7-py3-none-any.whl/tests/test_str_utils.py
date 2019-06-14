# -*- coding:UTF-8 -*-
'''
Created on 2014年12月5日

@author: caifh
'''
import unittest
import creditutils.str_util as utils
import chardet


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testName(self):
        pass


def test_escape():
    a = '123我们'
    b = utils.escape(a)
    print(b)
    c = ascii(a)
    print(c)


def test_decode_escape():
    src = 'abc我们'
    print(src)
    dst = utils.escape_entire(src)
    print(dst)
    dst = utils.escape(src)
    print(dst)
    thd = utils.decode_escape(dst)
    print(thd)


def test_detect_encoding():
    src_buf = 'abcdef'.encode(encoding='ascii')
    #     print(utils.detect_encoding(src_buf))
    print(utils.decode_to_unicode(src_buf))
    #     print(chardet.detect(src_buf))

    src_buf = 'abc我们'.encode(encoding='utf-8')
    #     print(utils.detect_encoding(src_buf))
    print(utils.decode_to_unicode(src_buf))

    src_buf = '我们在哪里啊afd'.encode(encoding='gb2312')
    #     print(utils.detect_encoding(src_buf))
    print(utils.decode_to_unicode(src_buf))


def test_maint():
    #     test_escape()
    #     test_decode_escape()
    test_detect_encoding()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    #     unittest.main()

    test_maint()
