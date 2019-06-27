#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/23
import datetime
import json
import re
import threading
import uuid


from api.model.FactDatasource import JdbcTypeEnum


def get_jdbc_type(url: str) -> JdbcTypeEnum:
    """
    根据url获取JDBC的类型
    :param url:
    :return:
    """
    if not url:
        return None

    if url.startswith('jdbc:derby:') or url.startswith('jdbc:log4jdbc:derby:'):
        return JdbcTypeEnum.DERBY
    elif url.startswith('jdbc:mysql:') or url.startswith('jdbc:cobar:') or url.startswith('jdbc:log4jdbc:mysql:'):
        return JdbcTypeEnum.MYSQL
    elif url.startswith('jdbc:mariadb:'):
        return JdbcTypeEnum.MARIADB
    elif url.startswith('jdbc:oracle:') or url.startswith('jdbc:log4jdbc:oracle:'):
        return JdbcTypeEnum.ORACLE
    elif url.startswith('jdbc:alibaba:oracle:'):
        return JdbcTypeEnum.ALI_ORACLE
    elif url.startswith('jdbc:microsoft:') or url.startswith('jdbc:log4jdbc:microsoft:'):
        return JdbcTypeEnum.SQL_SERVER
    elif url.startswith('jdbc:sqlserver:') or url.startswith('jdbc:log4jdbc:sqlserver:'):
        return JdbcTypeEnum.SQL_SERVER
    elif url.startswith('jdbc:sybase:Tds:') or url.startswith('jdbc:log4jdbc:sybase:'):
        return JdbcTypeEnum.SYBASE
    elif url.startswith('jdbc:jtds:') or url.startswith('jdbc:log4jdbc:jtds:'):
        return JdbcTypeEnum.JTDS
    elif url.startswith('jdbc:fake:') or url.startswith('jdbc:mock:'):
        return JdbcTypeEnum.MOCK
    elif url.startswith('jdbc:postgresql:') or url.startswith('jdbc:log4jdbc:postgresql:'):
        return JdbcTypeEnum.POSTGRESQL
    elif url.startswith('jdbc:hsqldb:') or url.startswith('jdbc:log4jdbc:hsqldb:'):
        return JdbcTypeEnum.HSQL
    elif url.startswith('jdbc:db2:'):
        return JdbcTypeEnum.DB2
    elif url.startswith('jdbc:h2:') or url.startswith('jdbc:log4jdbc:h2:'):
        return JdbcTypeEnum.H2
    elif url.startswith('jdbc:dm:'):
        return JdbcTypeEnum.DM
    elif url.startswith('jdbc:kingbase:'):
        return JdbcTypeEnum.KINGBASE
    elif url.startswith('jdbc:log4jdbc:'):
        return JdbcTypeEnum.LOG4JDBC
    elif url.startswith('jdbc:vernox:'):
        return JdbcTypeEnum.VERNOX
    else:
        return None


class Singleton(object):
    """
    简单实现一个单例基类, 保证通过instance方法取到的对象都是同一个对象
    这里使用这个类不使用模块直接加载的原因是想延迟初始化，使用集中式的FD时，很多本地的FD配置启动时都不需要加载
    """
    _lock = threading.Lock()
    _instance = None

    @classmethod
    def instance(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = cls()
        return cls._instance


def str_placeholder_replace(prefix: str, suffix: str, value: str, value_map: dict):
    """
    字符串占位符替换工具,将前缀和后缀之间的字符串作为key，在value_map中如果存在该key值，就用该key值替换
    如： str_placeholder_replace('${', '}', 'select * from ${table}', {'table':'test'}) 返回select * from test

    :param prefix:
    :param suffix:
    :param value:
    :param value_map:
    :return:
    """
    if not prefix or not suffix or not value or not value_map:
        return value

    value_list = []
    start = 0
    regex = re.escape(prefix) + '|' + re.escape(suffix)
    for r in re.finditer(regex, value):
        fix_key = value[start:r.start()]
        fix = value[r.start():r.end()]
        if fix == prefix:
            # 入栈
            value_list.append(fix_key)
            value_list.append(fix)
        elif fix == suffix:
            k = None
            key = fix_key

            # 出栈
            if value_list:
                k = value_list.pop()
                while value_list and prefix != k:
                    key = k + key
                    k = value_list.pop()

            # 替换值
            if k and k == prefix:
                if key in value_map:
                    v = value_map.get(key)
                    value_list.append(str(v))
                else:
                    value_list.append(prefix + key + suffix)
            else:
                k = k if k else ''
                key = key if key else ''
                value_list.append(k + key + suffix)
        start = r.end()
    # 加上最后剩下的
    if start < len(value):
        value_list.append(value[start:])
    return ''.join(value_list)


class JSONEncoder(json.JSONEncoder):
    """
    dict转换为JSON时处理下
    """
    def default(self, o):
        if isinstance(o, datetime.date):
            return str(o)
        if isinstance(o, uuid.UUID):
            return str(o)

        try:
            from bson import ObjectId
            if isinstance(o, ObjectId):
                return str(o)
        except ImportError:
            pass

        return json.JSONEncoder.default(self, o)


def uuid4():
    return str(uuid.uuid4()).replace('-', '')

