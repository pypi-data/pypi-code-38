#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: settings.py
# @time: 2018/9/8 0:53
# @Software: PyCharm

import os
from sqlalchemy.ext.declarative import declarative_base  # db 基类
from sqlalchemy import Column, Integer, String, DateTime  # 相应的列
from sqlalchemy.orm import sessionmaker, relationship, backref, scoped_session  # 执行的相关方法
from sqlalchemy.dialects.mysql import LONGTEXT

from tornado.options import parse_config_file, define

define("PASSWORD_HASHERS", default=[
    'apihelper.util.hashers.SM3PasswordHasher',
    'apihelper.util.hashers.UnsaltedSM3PasswordHasher',
], multiple=True)
