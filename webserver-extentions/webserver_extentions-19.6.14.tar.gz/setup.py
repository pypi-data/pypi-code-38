#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
    reload(sys)
    sys.setdefaultencoding("utf8")
except:
    pass

cur_dir = os.path.split(os.path.realpath(__file__))[0]
sys.path.append("%s/" % cur_dir)

from setuptools import setup
from setuptools import find_packages

setup(
    name="webserver_extentions",
    version="19.06.14",
    keywords=("pip", "webserver", "extentions", ""),
    description="flask and webpy frame",
    long_description="flask and webpy frame",

    url="https://github.com/lijiacaigit/webserver_extentions",
    author="Lijiacai",
    author_email="1050518702@qq.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=["flask", "flask_restful", "flask_sqlalchemy", "werkzeug", "pymysql", "cx_Oracle", "pymongo",
                      "elasticsearch", "ConfigParser", "configparser", "tornado", "celery"]
)
