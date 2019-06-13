#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

"""配置"""

LOG_LEVEL = logging.INFO
DO_MULTI = True
TIMESTAMP_WITH_FOLDER = True
URL = 'http://huaban.com/'
IMG_SAVE_PATH = 'D:/crawl/image'
DEFAULT_IMG_SUFFIX = 'jpg'
IMG_INCLUDE_SUFFIX = ['png', 'jpg']
IMG_EXCLUDE_SUFFIX = ['gif']

"""配置 end"""


# 初始化
def init():
    logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='[%Y-%M-%d %H:%M:%S]')


"""run"""
init()
