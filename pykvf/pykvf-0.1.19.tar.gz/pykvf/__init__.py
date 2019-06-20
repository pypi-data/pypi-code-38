#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

@author: banixcyan

@license: (C) Copyright 2013-2017, Tencent Corporation Limited.

@contact: banixcyan@gmail.com

@time: 2017/12/11 16:25

@desc: Py工具集封装 集成config, db, log

"""
from pykvf.log import console_logger as clog
from pykvf.config import init_conf, get_conf
from pykvf.db import init_db, get_db
from pykvf.log import init_log, get_log, get_console_logger


def init(config_filename, name='__default'):
    c = init_conf(config_filename, name)

    for l in c['log']:
        init_log(l['filename'], name=l.get('name', '__default'), level=l.get('level', 10))

    for d in c['mysql']:
        init_db(d['host'], d['user'], d['password'], d['port'], d['database'], charset=d.get('charset', 'utf8'), alias=d.get('name', None), max_conn=d.get('max_conn', 10))
