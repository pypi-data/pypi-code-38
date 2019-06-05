#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/06/05 10:35
# @Author  : niuliangtao
# @Site    : 
# @File    : datautils.py
# @Software: PyCharm
import os
import pycurl

__all__ = ['utils']

data_root = '/content/tmp/'


def download_file(url, path):
    if not os.path.exists(path):
        print("downloading from " + url + " to " + path)
        with open(path, 'wb') as f:
            c = pycurl.Curl()
            c.setopt(pycurl.URL, url)
            c.setopt(pycurl.WRITEDATA, f)
            c.perform()
            c.close()
        print('download success')
