#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/22
from sqlalchemy.engine import ResultProxy, RowProxy
from sqlalchemy.orm import Session

from api.model.FactDatasource import FactDatasourceTypeEnum
from factdatasource.dao.FactDatasource import Datasource
from factdatasource.dao.MultipleDatasourceHolder import get_multiple_datesource
from libs.utils import Singleton


class JdbcDatasourceDao(Singleton):

    @property
    def datasource(self) -> Datasource:
        data_source = get_multiple_datesource(FactDatasourceTypeEnum.JDBC)
        return data_source

    @property
    def client(self) -> Session:
        return self.datasource.get_client()

    def select_one(self, sql: str, params: dict = None) -> dict:
        """
        查询一行结果
        :param sql:
        :param params:
        :return:
        """
        result = self.__execute(sql, params)
        row = result.fetchone()
        return self.__result_to_dict(row)

    def select_all(self, sql: str, params: dict = None) -> list:
        """
        查询所有结果
        :param sql:
        :param params:
        :return:
        """
        result = self.__execute(sql, params)
        rows = result.fetchall()
        return self.__result_to_list(rows)

    def select_total(self, sql: str, params: dict = None):
        """
        查询sql的返回结果有多少条
        :param sql:
        :param params:
        :return:
        """
        count_result = self.__execute(sql, params)
        count_result.close()
        # TODO 这个方式在sqlserver中没有作用,需要新的方法，暂时先这样
        # 详见 https://usyiyi.github.io/sqlalchemy-docs-zh/dialects/mssql.html#rowcount-support-orm-versioning
        return count_result.rowcount

    def select_num(self, sql: str, params: dict = None):
        """
        查询一行一个结果，比如 select count(*) from table  这种
        :param sql:
        :param params:
        :return: str or num or obj
        """
        result = self.__execute(sql, params)
        row = result.fetchone()
        return row.values()[0] if len(row.values()) > 0 else None

    def execute(self, sql: str, params: dict = None) -> ResultProxy:
        """
        外部直接执行sql
        :param sql:
        :param params:
        :return:
        """
        return self.__execute(sql, params)

    def __execute(self, sql: str, params: dict = None) -> ResultProxy:
        """
        统一执行sql
        :param sql:
        :param params:
        :return:
        """
        return self.client.execute(sql, params)

    def __result_to_list(self, rows: list):
        """
        将多行查询结果转换为 list<dict>
        :param result: list<dict>
        :return:
        """
        if not rows:
            return []
        return [dict(zip(row.keys(), row)) for row in rows]

    def __result_to_dict(self, row: RowProxy):
        """
        将单行查询结果转换为dict
        :param row:
        :return:
        """
        if not row:
            return dict()
        return dict(zip(row.keys(), row))

