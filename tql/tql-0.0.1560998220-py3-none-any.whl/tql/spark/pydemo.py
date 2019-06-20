#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : iWork.
# @File         : pydemo
# @Time         : 2019-06-14 21:52
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 


from iwork.spark import SparkInit

sc, spark = SparkInit()()
df = spark.range(1, 20, 2)
df.show()
