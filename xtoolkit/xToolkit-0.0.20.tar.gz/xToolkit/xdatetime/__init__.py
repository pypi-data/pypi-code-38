#!/usr/bin/env python
# encoding: utf-8
"""
@author: 熊利宏
@email:xionglihong@163.com
@phone：15172383635
@project: X工具集->时间库
@file: __init__.py.py
@time: 2019-05-15 下午9:27
"""
from arrow.arrow import Arrow
from arrow.factory import ArrowFactory
from arrow.api import get, now, utcnow

# 判断时间格式是否正确
from .expansions import shape
# 时间起止区间
from .expansions import start_and_end
# 星期列表的字典
from .expansions import get_week_dict
