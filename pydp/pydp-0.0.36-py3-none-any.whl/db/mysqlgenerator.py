#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File: mysqlgenerator.py
Desc: mysql sql语句生成
"""
import sys
import json
from dp import utils
if utils.get_python_version() >= 3:  # python3 use html
    import html
else:  # python2 use cgi
    import cgi as html


class MySqlGenerator(object):
    """
        sqlgenerator
    """

    @staticmethod
    def query(table, select=None, where={}, groupby=None, orderby=None, limit=None):
        """
            query
        """
        if select:
            sql = "SELECT {} FROM ".format(select) + table
        else:
            sql = "SELECT * FROM " + table
        where_st = ""
        for (k, v) in where.items():
            where_st += MySqlGenerator.format_where(k, v) + " AND "
        if where is not None and len(where):
            sql += " WHERE " + where_st[0:-4]
        if groupby:
            sql += " GROUP BY " + groupby
        if orderby:
            sql += " ORDER BY " + orderby
        if limit:
            sql += " LIMIT " + str(limit)
        return sql

    @staticmethod
    def delete(table, where={}):
        """
            delete
        """
        sql = "DELETE FROM " + table
        where_st = ""
        for (k, v) in where.items():
            where_st += MySqlGenerator.format_where(k, v) + " AND "
        if where is None or len(where):
            sql += " WHERE " + where_st[0:-4]
        return sql

    @staticmethod
    def update(table, where, values={}):
        """
            update
        """
        sql = "UPDATE " + table
        sett = "SET "
        for (k, v) in values.items():
            sett += MySqlGenerator.format_set(k, v) + ","
        sett = sett.strip(',')
        where_st = "WHERE "
        for (k, v) in where.items():
            where_st += MySqlGenerator.format_where(k, v) + " AND "
        if where is None or len(where):
            where_st = where_st[0:-4]
        sql = "%s %s %s" % (sql, sett, where_st)
        return sql

    @staticmethod
    def insert(table, values={}):
        """
            insert
        """
        sql = "INSERT INTO " + table + " "
        sett = "SET "
        for (k, v) in values.items():
            sett += MySqlGenerator.format_set(k, v) + ","
        sett = sett.strip(',')
        sql += sett
        return sql

    @staticmethod
    def format_where(k, v):
        """返回k/v对应的where语句"""
        where_st = ''
        if type(v) is str:
            if v.find('!= ') > -1 or v.find('<> ') > -1 or v.find('like ') > -1 or \
                    v.find('> ') > -1 or v.find('< ') > -1 or v.find('>= ') > -1 or \
                    v.find('<= ') > -1 or v.find('between ') > -1 or v.find('in ') > -1:
                where_st += "`" + k + "` " + v
            else:
                v = json.dumps(html.escape(v), ensure_ascii=False)
                where_st += "`" + k + "`" + "=" + v
        elif v is None:
            where_st += "`" + k + "`" + " is null"
        else:
            where_st += "`" + k + "`" + "=" + str(v)
        return where_st

    @staticmethod
    def format_set(k, v):
        """返回k/v对应的set语句"""
        set_st = ''
        if type(v) is str:
            v = json.dumps(html.escape(v), ensure_ascii=False)
            set_st += "`" + k + "`" + "=" + v
        elif v is None:
            set_st += "`" + k + "`" + "=" + "NULL"
        else:
            set_st += "`" + k + "`" + "=" + str(v)
        return set_st
