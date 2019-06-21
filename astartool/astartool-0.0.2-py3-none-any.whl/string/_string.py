#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: _string.py
# @time: 2019/6/3 11:43
# @Software: PyCharm


__author__ = 'A.Star'

from astartool.number import ishex
from astartool.random import random_digit_string
import re
import datetime

is_hex = ishex


def is_email(email):
    """
    判断字符串是否为email
    :param email:
    :return:
    """
    regex = r'^[0-9a-zA-Z_\-\.]{0,19}@[0-9a-zA-Z_\-]{1,13}\.[a-zA-Z\.]{1,7}$'
    return True if re.match(regex, email) else False


def is_mobile(mobile):
    """
    判断是不是手机号
    :param mobile:
    :return:
    """
    regex = r'^1[0-9]{10}$'
    return True if re.match(regex, mobile) else False


def generate_number(k: int = 18):
    """
    k前14位是时间，后2位校验，中间是随机数。随机数应该不少于2位
    :param k:
    :return:
    """
    assert k >= 18
    assert not (k & 1)
    time_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # 14位
    rand_k = k - 16
    middle = random_digit_string(rand_k)  # 至少4位
    header = time_str + middle
    a1 = sum([int(i) for i in header[::2]]) % 10
    a2 = sum([int(i) for i in header[1::2]]) % 10
    c1 = str((-a1) % 10)
    c2 = str((-a2) % 10)
    return header + c1 + c2


def check_number(number):
    return not ((sum((int(i) for i in number[::2])) % 10) and (sum((int(i) for i in number[1::2])) % 10))


def force_bytes(s, encoding='utf-8', errors='strict'):
    """
    Similar to smart_bytes, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    # Handle the common case first for performance reasons.
    if isinstance(s, bytes):
        if encoding == 'utf-8':
            return s
        else:
            return s.decode('utf-8', errors).encode(encoding, errors)
    if isinstance(s, memoryview):
        return bytes(s)
    else:
        return s.encode(encoding, errors)
