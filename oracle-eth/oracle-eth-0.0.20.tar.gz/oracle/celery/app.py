#! /usr/bin/env python
# -*- coding: utf8 -*-
"""
# Author: yuyongpeng@hotmail.com
# Description:
#  

"""



from oracle.celery.task import *

from celery import chain

res = taskA.apply_async((1,2), link=taskB.s(1,2))

# res = chain(taskA.s(1,2), taskB.s(1,1))
print(res.get())

# re1 = taskA.delay(100, 200)
# # print(re1.get())
# re2 = taskB.delay(1, 2, 3)
# # print(re2.result)
# re3 = add.delay(1, 2)
# # print(re3.status)