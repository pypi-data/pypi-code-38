#!/usr/bin/python
# coding:utf-8

"""
Author:Lijiacai
Email:1050518702@qq.com
===========================================
CopyRight@JackLee.com
===========================================
"""

import os
import sys
import json
try:
    import ConfigParser
except:
    import configparser as ConfigParser

try:
    reload(sys)
    sys.setdefaultencoding("utf8")
except:
    pass

def get_conf(conf_file):
    config = ConfigParser.ConfigParser()
    config.read(conf_file)
    return config._sections
