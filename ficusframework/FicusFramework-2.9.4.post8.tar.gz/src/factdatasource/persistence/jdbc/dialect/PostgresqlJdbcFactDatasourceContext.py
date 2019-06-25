#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/22
from api.model.Page import Page
from factdatasource.execptions import FDExecuteException
from factdatasource.persistence.jdbc import SqlWrap
from factdatasource.persistence.jdbc.JdbcFactDatasourceContext import JdbcFactDatasourceContext


class PostgresqlJdbcFactDatasourceContext(JdbcFactDatasourceContext):
    """
    Postgresql 数据库中字段名是区分大小写的，建议都统一使用小写
    """

    def _size_sql(self):
        return f'SELECT COUNT(*) FROM "{self.fd().target}"'

    def _collect_sql(self, size: int):
        limit = f' LIMIT {size}' if size and size > 0 else ''
        return f'SELECT * FROM "{self.fd().target}" {limit}'

    def _delete_all_sql(self):
        return f'TRUNCATE TABLE "{self.fd().target}"'

    def _delete_sql(self, query: str):
        """删除数据SQL, 这里验证下这个query是否是删除语句"""
        if not query.lstrip().upper().startswith('DELETE'):
            err = f'{query}不是合法的删除操作.'
            raise FDExecuteException(err)
        return query

    def _query_page_sql(self, query: str, page: Page = None):
        """
        构造分页语句
        :param query: 原始SQL
        :param page:
        :return:
        """
        if page:
            page_sql = f'{query} LIMIT {page.pageSize} OFFSET {page.start_row}'
        else:
            page_sql = query
        return page_sql

    def _generate_insert_sql(self, table, result: dict) -> SqlWrap:
        """
        构造插入语句
        :param table:
        :param result:
        :return: SqlWrap
        """
        if not result:
            return None

        keys = '('
        values = '('
        for key, value in result.items():
            # if 'id' == str(key).lower() and not value:
            #     # 如果id字段的值是空的,就忽略
            #     # 这边如果只有一个id字段这里又跳过会有问题
            #     continue

            keys = '{0}"{1}",'.format(keys, key)
            values = '{0}:{1},'.format(values, key)

        if len(keys) > 1:
            keys = keys.rstrip(',') + ')'
            values = values.rstrip(',') + ')'
        else:
            return None

        sql = f'INSERT  INTO "{table}" {keys} VALUES {values}'

        param = self._param_process(result)
        return SqlWrap(sql, param)

    def _generate_update_sql(self, table, result: dict) -> SqlWrap:
        """
        生成修改语句的SQL
        :param table:
        :param result:
        :return: SqlWrap
        """
        if not result:
            return None

        updates = ''
        id_key = None
        for key, value in result.items():
            if 'id' == str(key).lower():
                id_key = key
                continue
            updates = '{0}"{1}"=:{2},'.format(updates, key, key)

        if not id_key or not updates:
            return None

        updates = updates.rstrip(',')

        sql = f'UPDATE "{table}" SET {updates} WHERE "{id_key}"=:{id_key}'

        param = self._param_process(result)
        return SqlWrap(sql, param)

