#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

@author: banixc

@contact: banixc@gmail.com

@time: 2017/9/30 14:57

@desc: DB

    连接池 sql拼装 sql预格式化 参数检查

"""
import sys

import pymysql
from pymysql import InternalError, OperationalError

try:
    import queue
except Exception:
    import Queue as queue

db_dict = {}


class DB:
    def __init__(self, host, user, password, port, database, charset, max_conn):
        self.db_config = {
            'host': host,
            'user': user,
            'password': password,
            'port': port,
            'database': database,
            'charset': charset
        }
        self.init_error_message = None
        self.conn_pool = queue.Queue(maxsize=max_conn)
        for _ in range(max_conn):
            self.conn_pool.put(self.init_conn())
        self.callback_function = {}

    def init_conn(self):
        return pymysql.connect(**self.db_config)

    def ping(self, conn):
        try:
            cursor = conn.cursor()
            cursor.execute('select 1;')
            cursor.fetchall()
            conn.commit()
            cursor.close()
            return conn
        except (OperationalError, InternalError):
            return self.init_conn()

    def get_conn(self):
        return self.ping(self.conn_pool.get())

    def put_conn(self, conn):
        try:
            conn.rollback()
            self.conn_pool.put(conn)
        except pymysql.err.InterfaceError:
            self.conn_pool.put(init_db())

    def session(self):
        return Session(self)

    def exe(self, sql, args=None):
        session = self.session()
        affect_rows = session.exe(sql, args)
        session.commit()
        del session
        return affect_rows

    def query(self, sql, args=None):
        return self.session().query(sql, args)

    def select(self, field, table, where=None, other=None, args=None):
        return self.query(select(field, table, where, other), args)

    def update(self, table, field, where=None, other=None, args=None):
        return self.exe(update(table, field, where, other), args)

    def insert(self, table, field, args):
        return self.exe(insert(table, field), args)

    def delete(self, table, where=None, other=None, args=None):
        return self.exe(delete(table, where, other), args)

    def replace(self, table, field, args):
        return self.exe(replace(table, field), args)

    def insert_on_duplicate_key(self, table, field, args):
        return self.exe(insert_on_duplicate_key(table, field), args)

    def callback(self, operation_type, func):
        self.callback_function[operation_type] = func


class Session:
    def __init__(self, db_instance):
        self.db = db_instance
        self.conn = db_instance.get_conn()
        self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    def __del__(self):
        self.db.put_conn(self.conn)

    def __exe(self, sql, args=None):
        callback = self.db.callback_function.get(sys._getframe().f_code.co_name, None)
        if callback is not None:
            callback(sql, args)
        return self.cursor.execute(sql, args)

    def __fetchall(self):
        return self.cursor.fetchall()

    def query(self, sql, args=None):
        callback = self.db.callback_function.get(sys._getframe().f_code.co_name, None)
        if callback is not None:
            callback(sql, args)
        self.__exe(sql, args)
        return self.__fetchall()

    def exe(self, sql, args=None):
        callback = self.db.callback_function.get(sys._getframe().f_code.co_name, None)
        if callback is not None:
            callback(sql, args)
        return self.__exe(sql, args)

    def select(self, field, table, where=None, other=None, args=None):
        return self.query(select(field, table, where, other), args)

    def insert(self, table, field, args):
        return self.exe(insert(table, field), args)

    def update(self, table, field, where=None, other=None, args=None):
        return self.exe(update(table, field, where, other), args)

    def delete(self, table, where=None, other=None, args=None):
        return self.exe(delete(table, where, other), args)

    def replace(self, table, field, args):
        return self.exe(replace(table, field), args)

    def insert_on_duplicate_key(self, table, field, args):
        return self.exe(insert_on_duplicate_key(table, field), args)

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def get_insert_id(self):
        return self.conn.insert_id()


def select(field, table, where, other):
    return 'SELECT ' + ', '.join(field) + ' FROM ' + table + where_and_other(where, other)


def insert(table, field):
    return 'INSERT INTO ' + table + ' ( ' + ', '.join(field) + ') VALUES (' + ('%s, ' * len(field))[:-2] + ')'


def update(table, field, where, other):
    return 'UPDATE ' + table + ' SET ' + ', '.join(field) + where_and_other(where, other)


def delete(table, where, other):
    return 'DELETE FROM ' + table + where_and_other(where, other)


def replace(table, field):
    return 'REPLACE INTO ' + table + ' ( ' + ', '.join(field) + ') VALUES (' + ('%s, ' * len(field))[:-2] + ')'


def insert_on_duplicate_key(table, field):
    return insert(table, field) + " ON DUPLICATE KEY UPDATE " + ", ".join(
        ["`{0}`=VALUES(`{0}`)".format(f) for f in field])


def where_and_other(where, other):
    sql = ''
    if where is not None and len(where) > 0:
        sql += ' WHERE (' + ') AND ('.join(where) + ')'
    if other is not None and other != '':
        sql += ' ' + other
    return sql


def init_db(host='localhost', user='root', password='root', port=3306, database='test', charset='utf8', alias=None,
            max_conn=10):
    if alias is None:
        alias = database
    db_dict[alias] = DB(host, user, password, port, database, charset, max_conn)
    return db_dict[alias]


def get_db(name=None):
    if name is None:
        name = list(db_dict.keys())[0]
    return db_dict[name]
