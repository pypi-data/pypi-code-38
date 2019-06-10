#!/usr/bin/env python

# -*-coding:utf-8-*-

"""
@author: vcancy
@software: PyCharm
@file: db_helper.py
@time: 2019/5/9 9:29 PM
@description:
"""
import pymysql
from logging import getLogger

logger = getLogger(__name__)


class MysqlHelper:
    def __init__(self, host='127.0.0.1', user='root', pwd='123456', db='testdb'):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db
        self.conn = None
        self.cur = None

    def connect(self):
        try:
            self.conn = pymysql.connect(self.host, self.user, self.pwd, self.db, charset='utf8')
        except Exception as e:
            logger.error("connect db exception {}".format(str(e)))
            return False
        self.cur = self.conn.cursor()
        return True

    def close(self):
        if self.conn and self.cur:
            self.cur.close()
            self.conn.close()
        return True

    def execute(self, sql, params=None):
        self.connect()
        try:
            if self.conn and self.cur:
                self.cur.execute(sql, params)
                self.conn.commit()
        except Exception as e:
            logger.error("execute exception: {}:{} ".format(sql, str(e)))
            self.close()
            return False
        return True

    def executemany(self, sql, items):
        self.connect()
        try:
            if self.conn and self.cur:
                self.cur.execute(sql, items)
                self.conn.commit()
        except Exception as e:
            logger.error("executemany exception: {}:{} ".format(sql, str(e)))
            self.close()
            return False
        return True

    # 用来查询表数据
    def fetchall(self, sql, params=None):
        self.execute(sql, params)
        return self.cur.fetchall()
