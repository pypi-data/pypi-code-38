# -*- coding: utf-8 -*-

# @Date    : 2019-06-27
# @Author  : Peng Shiyu

from __future__ import unicode_literals, print_function
import mysql.connector

from puremysql.logger import pure_mysql_logger
from puremysql.pure_table import PureTable
from puremysql.util import parse_db_url


class PureMysql(object):
    def __init__(self, db_url=None, **db_config):
        # 返回字典对象
        if db_url:
            parse_config = parse_db_url(db_url)
            if parse_config.pop("scheme") != "mysql":
                raise Exception("scheme not mysql")
            else:
                db_config.update(parse_config)
        self.connect = mysql.connector.connect(**db_config)
        self.cursor = self.connect.cursor(dictionary=True)

    def close(self):
        self.cursor.close()
        self.connect.close()

    def execute(self, sql, data=(), commit=False):
        pure_mysql_logger.info(self.cursor.statement)

        if isinstance(data, list):
            self.cursor.executemany(sql, data)
        else:
            self.cursor.execute(sql, data)

        if commit:
            self.connect.commit()

        # pure_mysql_logger.info(self.cursor.statement)

        return self.cursor

    def table(self, table_name):
        return PureTable(self, table_name)


if __name__ == '__main__':
    url = "mysql://root:123456@127.0.0.1:3306/demo?charset=utf8"
    PureMysql(db_url=url)
