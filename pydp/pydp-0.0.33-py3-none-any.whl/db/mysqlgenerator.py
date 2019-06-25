#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File: mysqlgenerator.py
Desc: mysql sql语句生成
"""
import sys
import json


class MySqlGenerator(object):
    """
        sqlgenerator
    """

    @staticmethod
    def query(table, select_key=None, where={}):
        """
            query
        """
        if select_key:
            sql = "SELECT {} FROM ".format(select_key) + table
        else:
            sql = "SELECT * FROM " + table
        where_st = ""
        for (k, v) in where.items():
            if type(v) is str:
                if v.find('!=') > -1 or v.find('like ') > -1:
                    where_st += "`" + k + "`" + v
                else:
                    v = json.dumps(v, ensure_ascii=False)
                    where_st += "`" + k + "`" + "=" + v
            elif v is None:
                where_st += "`" + k + "`" + " is null"
            else:
                where_st += "`" + k + "`" + "=" + str(v)
            where_st += " AND "
        if where is not None and len(where):
            sql += " WHERE " + where_st[0:-4]
        return sql

    @staticmethod
    def like_query(table, where={}):
        """
             like query
        """
        sql = "SELECT * FROM " + table
        where_st = ""
        for (k, v) in where.items():
            if type(v) is str:
                where_st += "`" + k + "`" + " like " + "\"%{}%\"".format(v)
            elif v is None:
                where_st += "`" + k + "`" + " is null"
            else:
                where_st += "`" + k + "`" + " like " + "\"%{}%\"".format(str(v))
            where_st += " AND "
        if where is not None and len(where):
            sql += " WHERE " + where_st[0:-4]
        return sql

    @staticmethod
    def delete(table, where={}):
        """
            delete
        """
        sql = "DELETE FROM " + table
        where_st = ""
        for (k, v) in where.items():
            if type(v) is str:
                if v.find('>') > -1 or v.find('<') > -1:
                    where_st += "`" + k + "`" + v
                else:
                    v = json.dumps(v, ensure_ascii=False)
                    where_st += "`" + k + "`" + "=" + v
            elif v is None:
                where_st += "`" + k + "`" + " is null"
            else:
                where_st += "`" + k + "`" + "=" + str(v)
            where_st += " AND "
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
            if type(v) is str:
                v = json.dumps(v, ensure_ascii=False)
                sett += "`" + k + "`" + "=" + v
            elif v is None:
                sett += "`" + k + "`" + "=" + "NULL"
            else:
                sett += "`" + k + "`" + "=" + str(v)
            sett += ","
        sett = sett.strip(',')
        where_st = "WHERE "
        for (k, v) in where.items():
            if type(v) is str:
                v = json.dumps(v, ensure_ascii=False)
                where_st += "`" + k + "`" + "=" + v
            elif v is None:
                where_st += "`" + k + "`" + " is null"
            else:
                where_st += "`" + k + "`" + "=" + str(v)
            where_st += " AND "
        if where is None or len(where):
            where_st = where_st[0:-4]
        sql = "%s %s %s" % (sql, sett, where_st)
        return sql

    @staticmethod
    def like_update(table, where, values={}):
        """
            like update
        """
        sql = "UPDATE " + table
        sett = "SET "
        for (k, v) in values.items():
            if type(v) is str:
                v = json.dumps(v, ensure_ascii=False)
                sett += "`" + k + "`" + "=" + v
            elif v is None:
                sett += "`" + k + "`" + "=" + "NULL"
            else:
                sett += "`" + k + "`" + "=" + str(v)
            sett += ","
        sett = sett.strip(',')
        where_st = ""
        for (k, v) in where.items():
            if type(v) is str:
                where_st += "`" + k + "`" + " like " + "\"%{}%\"".format(v)
            elif v is None:
                where_st += "`" + k + "`" + " is null"
            else:
                where_st += "`" + k + "`" + " like " + "\"%{}%\"".format(str(v))
            where_st += " AND "
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
            if type(v) is str:
                v = json.dumps(v, ensure_ascii=False)
                sett += "`" + k + "`" + "=" + v
            elif v is None:
                sett += "`" + k + "`" + "=" + "NULL"
            else:
                sett += "`" + k + "`" + "=" + str(v)
            sett += ","
        sett = sett.strip(',')
        sql += sett
        return sql
