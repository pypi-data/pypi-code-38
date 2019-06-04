#! /usr/bin/env python
# -*- coding: utf8 -*-
"""
Author:       yuyongpeng@hotmail.com
Github:       https://github.com/yuyongpeng/
Date:         2019-04-12 13:40:03
LastEditors:
LastEditTime: 2019-04-12 13:40:03
Description:
"""

import ctypes
from ctypes import CDLL

Hello = CDLL('./crypto.so').DESEncrypt  #调用ｇｏ模块
# 显式声明参数和返回的期望类型
Hello.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
Hello.restype = ctypes.c_char_p
print(Hello(b'hello world', b'12345678'))


# add = CDLL('./libexptest.so').addstr  #调用ｇｏ模块
# 显式声明参数和返回的期望类型
# add.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
# add.restype = ctypes.c_char_p
# print(add('haha','hehe'))

# 无参数，则可直接调用
# t = CDLL('./libexptest.so').test #调用ｇｏ模块
# print(t())