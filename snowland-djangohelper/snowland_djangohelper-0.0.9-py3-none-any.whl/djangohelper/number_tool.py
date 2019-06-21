#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: number_tool.py
# @time: 2019/3/11 16:58
# @Software: PyCharm


__author__ = 'A.Star'

from djangohelper.common import (
    hex_string_upper, hex_string, digit_string, alnum_string
)
from astartool.random import random_string as tool_random_string
from astartool.random import random_hex_string as tool_random_hex_string
from astartool.random import random_digit_string as tool_random_digit_string


def random_string(n: int = 32, allow_string=alnum_string):
    return tool_random_string(n, allow_string)


def random_hex_string(n: int = 32, upper=False):
    return tool_random_hex_string(n, upper)


def random_digit_string(n: int = 8):
    return tool_random_digit_string(n)
