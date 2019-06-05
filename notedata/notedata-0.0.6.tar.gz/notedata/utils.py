#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/06/05 10:35
# @Author  : niuliangtao
# @Site    : 
# @File    : utils.py
# @Software: PyCharm
import logging
import os
import pycurl

__all__ = ['utils']

data_root = '/content/tmp/'


def download_file(url, path, overwrite=False):
    if exists(path, overwrite=overwrite):
        return

    logging.info("downloading from " + url + " to " + path)
    with open(path, 'wb') as f:
        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.WRITEDATA, f)
        c.perform()
        c.close()
        logging.info('download success')


def exists(path, overwrite=False):
    if os.path.exists(path):
        if overwrite:
            logging.info("file exists, overwrite it")
            os.remove(path)
            return False
        else:
            logging.info("file exists, return")
            return True
    return False
