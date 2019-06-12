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

logger = logging.getLogger(__name__)

__all__ = ['utils']

data_root = '/content/tmp/'
raw_root = 'https://raw.githubusercontent.com/1007530194/data/master/'


def download_file(url, path, overwrite=False):
    if exists(path, overwrite=overwrite):
        return

    logger.info("downloading from " + url + " to " + path)
    with open(path, 'wb') as f:
        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.WRITEDATA, f)
        c.perform()
        c.close()
        logger.info('download success')


def exists(path, overwrite=False):
    filename = os.path.basename(path)
    if os.path.exists(path):
        if overwrite:
            logger.info("file:{} exists, overwrite it".format(filename))
            os.remove(path)
            return False
        else:
            logger.info("file:{} exists, return".format(filename))
            return True
    return False
