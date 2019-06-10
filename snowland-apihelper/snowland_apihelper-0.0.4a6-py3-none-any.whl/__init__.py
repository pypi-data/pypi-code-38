#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: __init__.py.py
# @time: 2018/9/8 1:02
# @Software: PyCharm

from astartool.setuptool import get_version
from apihelper.settings import *

version = (0, 0, 4, 'alpha', 6)
__version__ = get_version(version)
