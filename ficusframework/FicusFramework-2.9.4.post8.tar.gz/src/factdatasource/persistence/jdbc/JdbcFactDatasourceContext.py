#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/21
import json
import logging
from abc import abstractmethod

from api.exceptions import IllegalArgumentException
from api.model.Page import Page
from factdatasource.dao.FactDatasource import customer_dao_context_holder as costomer_context
from factdatasource.dao.jdbc.JdbcDatasourceDao import JdbcDatasourceDao
from factdatasource.execptions import FDExecuteException
from factdatasource.persistence.AbstractFactDatasourceContext import AbstractFactDatasourceContext
from factdatasource.persistence.jdbc import SqlWrap
from libs.utils import str_placeholder_replace

log = logging.getLogger('Ficus')


class JdbcFactDatasourceContext(AbstractFactDatasourceContext):

    @property
    def dao(self) -> JdbcDatasourceDao:
        return JdbcDatasourceDao.instance()

    def size(self):
        """
        返回数据总长度
        :return: 数据条数:long
        """
        source_name = self.fd().get_source_name()

        sql = self._size_sql()
        log.debug(f'事实库{source_name}执行size操作SQL：{sql}')
        try:
            costomer_context.set_source(source_name)
            result = self.dao.select_num(sql)
            size = 0 if result is None else result
            return size
        except Exception as e:
            error = f'事实库{source_name}执行size操作SQL：{sql} 发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()

    @abstractmethod
    def _size_sql(self):
        """
        构造查询数据总条数的sql
        :return:
        """

    def is_empty(self):
        """
        返回是否存在数据
        :return: boolean
        """
        source_name = self.fd().get_source_name()

        sql = self._is_empty_sql()
        log.debug(f'事实库{source_name}执行is_empty操作SQL：{sql}')
        try:
            costomer_context.set_source(source_name)
            result = self.dao.select_num(sql)
            size = 0 if result is None else result
            return size <= 0
        except Exception as e:
            error = f'事实库{source_name}执行is_empty操作SQL：{sql} 发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()

    def _is_empty_sql(self):
        """
        构造查询数据总条数的sql
        :return:
        """
        return self._size_sql()

    def collect(self, size: int):
        """
        返回指定条数的数据
        :param size: 返回的条数
        :return: list
        """
        source_name = self.fd().get_source_name()

        sql = self._collect_sql(size)
        log.debug(f'事实库{source_name}执行collect操作SQL：{sql}')
        try:
            costomer_context.set_source(source_name)
            result = self.dao.select_all(sql)
            return result
        except Exception as e:
            error = f'事实库{source_name}执行collect操作SQL：{sql} 发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()

    @abstractmethod
    def _collect_sql(self, size: int):
        """查询指定条数数据的SQL"""

    def query(self, query: str, parameters: dict = None):
        """
        使用查询语句查询数据
        :param query: 查询语句
        :param parameters: 查询参数
        :return: Page
        """
        source_name = self.fd().get_source_name()

        page = None
        if parameters and 'pageNum_' in parameters.keys() and 'pageSize_' in parameters.keys():
            # 需要分页的
            param = {
                'pageNum': parameters.get('pageNum_'),
                'pageSize': parameters.get('pageSize_'),
                'needCount': parameters.get('needCount_') if parameters.get('needCount_') else False
            }
            page = Page(**param)

        # 参数占位符处理
        query = self._fd_placeholder_replace(query, parameters)

        sql = self._query_page_sql(query, page)

        log.debug(f'事实库{source_name}执行query操作SQL：{sql}')
        try:
            costomer_context.set_source(source_name)

            result = self.dao.select_all(sql, parameters)
            if page:
                total = None
                if page.need_count():
                    total = self.dao.select_total(query, parameters)
                page.set_result(result, total)
                return page
            else:
                return Page.no_page(result)
        except Exception as e:
            error = f'事实库{source_name}执行query操作SQL：{sql} 发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()

    @abstractmethod
    def _query_page_sql(self, query: str, page: Page):
        """
        构造分页语句
        :param query:
        :param page:
        :return:
        """

    def _single_thread_inserts(self, table: str, result_list: list):
        """
        批量保存数据,要求list里面的字段和数据库里面的字段一一对应
        :param table: 表名
        :param result_list: 要保存的数据
        :return:
        """
        source_name = self.fd().get_source_name()
        try:
            costomer_context.set_source(source_name)
            for result in result_list:
                self._inner_insert(table, result, 0)
        finally:
            costomer_context.clear_source()

    def _inner_insert(self, table: str, result, dept: int):
        if dept > 5:
            # 重试5次都不行，直接报错
            raise FDExecuteException(f"插入数据{result}错误，重试5次依然失败。")

        if isinstance(result, dict):
            sql_wrap = self._generate_insert_sql(table, result)
        else:
            sql_wrap = self._generate_insert_sql(table, vars(result))

        if not sql_wrap:
            log.error(f'事实库{source_name}执行inserts操作时时无法对数据{result}进行有效的插入，放弃该数据的添加。')
            return

        source_name = self.fd().get_source_name()
        try:
            self.dao.execute(sql_wrap.sql, sql_wrap.param)
            # TODO  这里捕获的异常需要更精细的划分
        except Exception as e:
            error = f'事实库{source_name}执行inserts操作SQL：{sql_wrap.sql} 发生异常, {str(e)}'
            log.error(error)
            # 重试
            self._inner_insert(table, result, dept+1)

    @abstractmethod
    def _generate_insert_sql(self, table, result: dict) -> SqlWrap:
        """
        生成插入语句的SQL
        :param table:
        :param result:
        :return: SqlWrap
        """

    def _single_thread_updates(self, table: str, result_list: list):
        """
        批量更新数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param result_list: 要修改的数据
        :return:
        """
        source_name = self.fd().get_source_name()
        try:
            costomer_context.set_source(source_name)
            for result in result_list:
                self._inner_update(table, result)
        finally:
            costomer_context.clear_source()

    def _inner_update(self, table, result) -> bool:
        if isinstance(result, dict):
            sql_wrap = self._generate_update_sql(table, result)
        else:
            sql_wrap = self._generate_update_sql(table, vars(result))

        source_name = self.fd().get_source_name()

        if not sql_wrap:
            log.error(f'事实库{source_name}执行updates操作时时无法对数据{result}进行有效的更新，放弃该数据的更新。')
            return False

        try:
            return self.dao.execute(sql_wrap.sql, sql_wrap.param).rowcount > 0
        except Exception as e:
            error = f'事实库{source_name}执行updates操作SQL：{sql_wrap.sql} 发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        return False

    @abstractmethod
    def _generate_update_sql(self, table, result: dict) -> SqlWrap:
        """
        生成修改语句的SQL
        :param table:
        :param result:
        :return: SqlWrap
        """

    def _single_thread_inserts_or_updates(self, table: str, result_list: list):
        """
        批量saveOrUpdate数据,,数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param result_list: 要添加或者需要修改的数据
        :return:
        """
        source_name = self.fd().get_source_name()
        try:
            costomer_context.set_source(source_name)
            for result in result_list:
                if not self._inner_update(table, result):
                    # 没有更新成功
                    try:
                        self._inner_insert(table, result, 0)
                    except FDExecuteException as e:
                        # 这种异常直接抛出去
                        raise e
                    except Exception as e:
                        # 如果插入失败了,就可能是已经有其他的线程插入了,那么就重新执行更新.这里只尝试一次,而不是做递归
                        self._inner_update(table, result)
        finally:
            costomer_context.clear_source()

    def delete_all(self):
        """
        清空数据
        :return:
        """
        source_name = self.fd().get_source_name()

        sql = self._delete_all_sql()
        log.debug(f'事实库{source_name}执行delete_all操作SQL：{sql}')
        try:
            costomer_context.set_source(source_name)
            self.dao.execute(sql)
        except Exception as e:
            error = f'事实库{source_name}执行delete_all操作SQL：{sql} 发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()

    @abstractmethod
    def _delete_all_sql(self):
        """清空数据SQL"""

    def delete(self, query: str):
        """
        根据删除语句删除数据,query是完整的删除语句
        :param query: 完整的删除语句
        :return:
        """
        source_name = self.fd().get_source_name()

        sql = self._delete_sql(query)
        log.debug(f'事实库{source_name}执行delete操作SQL：{sql}')
        try:
            costomer_context.set_source(source_name)
            self.dao.execute(sql)
        except Exception as e:
            error = f'事实库{source_name}执行delete操作SQL：{sql} 发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()

    @abstractmethod
    def _delete_sql(self, query: str):
        """删除数据SQL"""

    def _fd_placeholder_replace(self, value: str, value_map: dict):
        """
        处理JDBC中的参数占位符
        将${key}这种直接进行替换， 将#{key}更换为:key这种，然后通过传参到数据库中去
        :param value:
        :param value_map:
        :return:
        """
        if not isinstance(value, str):
            raise IllegalArgumentException('占位符处理参数类型错误，value只能为str.')
        value = str_placeholder_replace('${', '}', value, value_map)

        tmp_map = {}
        for key in value_map.keys():
            tmp_map[key] = ':' + str(key)
        value = str_placeholder_replace('#{', '}', value, tmp_map)
        return value

    def _param_process(self, param: dict):
        """
        构造sql时处理下SQL的传入参数
        主要用于将对象字符串化，方便系统构造sql
        :param param:
        :return:
        """
        result = {}

        if not param:
            result

        for key, value in param.items():
            if isinstance(value, str):
                v = value
            elif isinstance(value, list) or isinstance(value, dict):
                v = json.dumps(value)
            elif isinstance(value, tuple) or isinstance(value, set):
                v = str(value)
            else:
                v = value
            result[key] = v
        return result

