# -*- coding: utf-8 -*-
# @Time    : 2018/8/3 10:13
# @Author  : Liu Gang
# @Site    : 
# @File    : __init__.py.py
# @Software: PyCharm
import sys

PY_VER = 0
if sys.version > '3':
    PY_VER = 3
    print("Python version type:3")
else:
    PY_VER = 2
    print("Python version type:2")

__VERSION__ = "V1.0.8"
