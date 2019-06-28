# -*- coding: utf-8 -*-

# @Date    : 2019-06-27
# @Author  : Peng Shiyu
from __future__ import unicode_literals, print_function
from puremysql.sql_builder_util import SQLBuilderUtil


class PureTable(object):
    def __init__(self, pure_mysql, table_name):
        self.pure_mysql = pure_mysql
        self.table_name = table_name

    def execute(self, sql, data=(), commit=False):
        return self.pure_mysql.execute(sql, data, commit)

    def select(self, fields, where, limit=None):

        if limit:
            where = "{} LIMIT {}".format(where, limit)

        sql = SQLBuilderUtil.get_select_sql(self.table_name, fields, where)
        cursor = self.execute(sql)
        return cursor.fetchall()

    def select_one(self, fields, where):
        result = self.select(fields, where, 1)
        if len(result) == 1:
            row = result[0]
        else:
            row = {}
        return row

    def insert(self, data):
        if isinstance(data, list):
            keys = SQLBuilderUtil.get_list_keys(data)
            sql = SQLBuilderUtil.get_insert_sql(self.table_name, keys)

        else:
            sql = SQLBuilderUtil.get_insert_sql(self.table_name, data.keys())

        cursor = self.execute(sql, data, True)
        return cursor.rowcount

    def delete(self, where):
        sql = SQLBuilderUtil.get_delete_sql(self.table_name, where)
        cursor = self.execute(sql, commit=False)
        return cursor.rowcount

    def update(self, data, where):
        """
        :param data: dict
        :param where: str
        :return: int
        """
        sql = SQLBuilderUtil.get_update_sql(self.table_name, data.keys(), where)
        cursor = self.execute(sql, data, True)
        return cursor.rowcount

    def update_by_id(self, data, row_id):
        return self.update(data, "`id`={}".format(row_id))

    def delete_by_id(self, row_id):
        return self.delete("`id`={}".format(row_id))

    def select_by_id(self, fields, row_id):
        where = "`id`={}".format(row_id)
        return self.select_one(fields, where)
