# -*- coding: utf-8 -*-

"""
#=============================================================================
#  ProjectName: plum-tools
#     FileName: printer
#         Desc: 按指定颜色打印信息
#       Author: seekplum
#        Email: 1131909224m@sina.cn
#     HomePage: seekplum.github.io
#       Create: 2019-04-03 22:50
#=============================================================================
"""

from __future__ import print_function

from ..compat import implements_to_unicode


def get_color(c, s):
    """获取带背景色的字符串

    :param c 前背景色
    :type c int
    :example c 1

    :param s 需要获取背景色的字符串
    :type s basestring
    :example s ok

    :rtype str
    :return: 带颜色的字符串
    """
    return "\033[3%sm%s\033[0m" % (c, implements_to_unicode(s))


def get_red(s):
    """获取红颜色字符串

    :param s 需要获取背景色的字符串
    :type s basestring
    :example s ok

    :rtype str
    :return: 红色的字符串
    """
    return get_color(1, s)


def get_green(s):
    """获取绿颜色字符串

    :param s 需要获取背景色的字符串
    :type s basestring
    :example s ok

    :rtype str
    :return: 绿色的字符串
    """
    return get_color(2, s)


def get_yellow(s):
    """获取黄颜色字符串

    :param s 需要获取背景色的字符串
    :type s basestring
    :example s ok

    :rtype str
    :return: 黄色的字符串
    """
    return get_color(3, s)


def print_text(text):
    """打印普通信息

    :param text 要打印的信息
    :type text basestring
    :example text "ok"
    """
    print(text)


def print_ok(text):
    """打印正确信息,绿色

    :param text 要打印的信息
    :type text basestring
    :example text "ok"
    """
    fmt = get_green(text)
    print_text(fmt)


def print_warn(text):
    """打印警告信息,黄色

    :param text 要打印的信息
    :type text basestring
    :example text "warn"
    """
    fmt = get_yellow(text)
    print_text(fmt)


def print_error(text):
    """打印错误信息,红色

    :param text 要打印的信息
    :type text basestring
    :example text "error"
    """
    fmt = get_red(text)
    print_text(fmt)
