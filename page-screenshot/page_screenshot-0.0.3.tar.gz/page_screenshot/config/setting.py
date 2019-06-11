#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

"""配置"""

LOG_LEVEL = logging.INFO
DEFAULT_IMG_SUFFIX = '.png'

TIMESTAMP_WITH_FOLDER = False
URL = 'http://huaban.com/'
IMG_SAVE_PATH = 'C:/page_screenshot'
BASE_HEIGHT = 900
SCALE_HEIGHT = 1.25
TIME_MS_SCROLL_FAST = 600
TIME_MS_SCROLL_SLOW = 900
CHROME_DRIVER_PATH = 'C:/opt/exe/chromedriver.exe'
INIT_WINDOW_POSITION_X = 800
INIT_WINDOW_POSITION_Y = 0
JS_FILE_NAME = 'return nickname + "-" + msg_title'
INIT_HEIGHT = 500  # 响应式网页自行调整高度哦

# 微信公众号宽屏
OUTER_PC_WIDTH = 1273

# 手机屏
OUTER_PHONE_WIDTH = 643

"""配置 end"""

"""javascript"""
JS_MAX_HEIGHT = """
return
Math.max(document.body.scrollHeight, document.body.offsetHeight
, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);
""".replace("\n", " ")

JS_MAX_WIDTH = """
return
Math.min(document.body.scrollWidth, document.body.offsetWidth
, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth);
""".replace("\n", " ")

JS_WINDOW_HEIGHT = 'return document.documentElement.clientHeight'

JS_SCROLL = 'setTimeout(function(){ window.scrollTo(0, %s); }, %s);'

"""javascript end"""


def init():
    """
    初始化

    :return: void
    """
    logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='[%Y-%M-%d %H:%M:%S]')


"""run"""
init()
