#!/usr/bin/env python
"""
File: mysql.py
Desc: mysql操作类(python3+)
"""

import os
import sys
import time
import logging
import pymysql
import pymysql.cursors
from dp import utils
from dp.db.mysqlgenerator import MySqlGenerator

CUR_PATH = os.path.dirname(os.path.abspath(__file__))


class Mysql(object):
    """
        Mysql操作类
    """

    def __init__(self, host, port, user, password, db,
                 charset="utf8", debug=0):
        """
        初始化配置

        :param host: hostname
        :param port: 端口
        :param user: 用户名
        :param password: 密码
        :param db: 库名
        :param charset: 字符集（默认utf8）
        :param debug: 是否打印sql
        :returns: 
        """
        self.host = host
        self.port = int(port)
        self.user = user
        self.password = password
        self.db = db
        self.debug_level = debug
        self.conn = None
        self.charset = charset
        self.sqlGen = MySqlGenerator()

    def debug(self, sql):
        """debug"""
        logging.info('SQL: {};'.format(sql))
        if self.debug_level:
            print('SQL: {};'.format(sql))

    def connect(self):
        """connect"""
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user,
                                    password=self.password, db=self.db, charset=self.charset,
                                    cursorclass=pymysql.cursors.DictCursor)

    def disconnect(self):
        """disconnect"""
        if self.conn:
            self.conn.close()

    def insert(self, table, values={}):
        """
        插入数据

        :param table: 表名
        :param values: dict键值对
        :returns: 数据id
        """
        try:
            self.connect()
            cursor = self.conn.cursor()
            sql = self.sqlGen.insert(table=table, values=values)
            self.debug(sql)
            cursor.execute(sql)
            lastrowid = cursor.lastrowid
            self.conn.commit()
            cursor.close()
            self.conn.close()
            return lastrowid
        except:
            logging.error(utils.get_trace())

    def update(self, table, where, values={}):
        """
        更新数据

        :param table: 表名
        :param where: where条件键值对
        :param values: 要更新的键值对
        :returns: 
        """
        if not isinstance(where, dict):
            logging.error("where must be dict")
        self.connect()
        cursor = self.conn.cursor()
        sql = self.sqlGen.update(table=table, where=where, values=values)
        self.debug(sql)
        cursor.execute(sql)
        self.conn.commit()
        cursor.close()
        self.conn.close()

    def query(self, table, where={}):
        """
        查询数据

        :param table: 表名
        :param where: where条件键值对
        :returns: 结果集list
        """
        res_arry = []
        self.connect()
        cursor = self.conn.cursor()
        sql = self.sqlGen.query(table=table, where=where)
        self.debug(sql)
        cursor.execute(sql)
        for data in cursor.fetchall():
            res_arry.append(data)
        cursor.close()
        self.conn.close()
        return res_arry

    def delete(self, table, where={}):
        """
        删除数据

        :param table: 表名
        :param where: where条件键值对
        :returns: 
        """
        self.connect()
        cursor = self.conn.cursor()
        sql = self.sqlGen.delete(table=table, where=where)
        self.debug(sql)
        cursor.execute(sql)
        self.conn.commit()
        cursor.close()
        self.conn.close()


if __name__ == '__main__':
    """测试"""
    # log
    utils.init_logging(log_file='mysql', log_path=CUR_PATH)

    # mysql
    #from dp.db.mysql import Mysql
    db = Mysql(host='127.0.0.1', port='3306', user='root', password='Qazwsx!2#4%6&8(0', db='test', debug=1)
    table = 'test'
    # insert
    ret = db.insert(table, {'val': str(time.time())+'"; delete * from test'})
    print(ret)
    # delete
    db.delete(table, {'id': '< 2'})
    # update
    db.update(table, {'id': 2}, {'val': '6663'})
    # query
    res = db.query(table, {'id': 'between 2 and 100', 'val': "like '66%'"})
    print(res)
    res = db.query(table)  # , {'val': '6663 or 1=2'})
    print(res)
