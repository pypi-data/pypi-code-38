# -*- coding: utf-8 -*-

"""
notes:
    1. 使用decorator会影响到函数的文档，必须要运行一次函数，才可以通过`?`或者help查看函数文档
       在该文件内初始遍历调用这些函数，加载函数文档
       注意：`?`和help获得到的函数文档略有差异，推荐使用`?`
"""


from .coord_transform import *
from .dis_compute import *
from .rings import *

