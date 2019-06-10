#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: crypto.py
# @time: 2018/12/20 9:54
# @Software: PyCharm
from apihelper.util.hashers import make_password, check_password

if __name__ == '__main__':
    password = 'xxxxxx'
    encoded = make_password(password, salt=None, hasher='default')
    print(encoded)

    print(check_password(password, encoded))
    # import hashlib
    # md5 = hashlib.md5()
    # md5.update(b'123')
    # print(md5.digest())
