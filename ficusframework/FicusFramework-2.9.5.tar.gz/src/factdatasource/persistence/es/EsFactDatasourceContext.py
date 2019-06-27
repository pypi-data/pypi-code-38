#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/21
import logging

from api.model.Page import Page
from factdatasource.dao.FactDatasource import customer_dao_context_holder as costomer_context
from factdatasource.dao.es.EsDatasourceDao import EsDatasourceDao
from factdatasource.execptions import FDExecuteException
from factdatasource.persistence.AbstractFactDatasourceContext import AbstractFactDatasourceContext

log = logging.getLogger('Ficus')


class EsFactDatasourceContext(AbstractFactDatasourceContext):

    DEFAULT_INDEX_TYPE = 'SobeyCube'

    @property
    def dao(self) -> EsDatasourceDao:
        return EsDatasourceDao.instance()

    def size(self):
        """
        返回数据总长度
        :return: 数据条数:long
        """
        source_name = self.fd().get_source_name()
        target = self.fd().target
        try:
            costomer_context.set_source(source_name)
            result = self.dao.count(index=target, doc_type=self.DEFAULT_INDEX_TYPE)
            size = 0 if result is None else result
            return size
        except Exception as e:
            error = f'事实库{source_name}执行size操作发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()

    def is_empty(self):
        """
        返回是否存在数据
        :return: boolean
        """
        source_name = self.fd().get_source_name()
        target = self.fd().target
        try:
            costomer_context.set_source(source_name)
            result = self.dao.count(index=target, doc_type=self.DEFAULT_INDEX_TYPE)
            size = 0 if result is None else result
            return size <= 0
        except Exception as e:
            error = f'事实库{source_name}执行is_empty操作发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()

    def collect(self, size: int):
        """
        返回指定条数的数据
        :param size: 返回的条数
        :return: list
        """
        source_name = self.fd().get_source_name()
        target = self.fd().target
        try:
            costomer_context.set_source(source_name)
            size = size if size else 0
            result = self.dao.simple_query(index=target, doc_type=self.DEFAULT_INDEX_TYPE, size=size, analyze_wildcard=True)
            return result
        except Exception as e:
            error = f'事实库{source_name}执行collect操作发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()

    def query(self, query: str, parameters: dict = None):
        """
        使用查询语句查询数据
        :param query: 查询语句
        :param parameters: 查询参数
        :return: Page
        """
        source_name = self.fd().get_source_name()
        target = self.fd().target

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

        # 处理SQL空格
        query = query.strip()

        if query.startswith('{') and query.endswith('}'):
            # 说明是json方式
            # 处理下分页
            if page:
                if 'from' not in query:
                    query['from'] = page.start_row
                if 'size' not in query:
                    query['size'] = page.pageSize
        else:
            # TODO 暂时先不支持  这里如果找不到开源的SQL转换工具，就只能自己写一个了
            raise FDExecuteException(f'事实库{source_name}执行query操作查询语句错误，SQL：{query}')

        # 进行查询
        try:
            log.debug(f'事实库{source_name}执行query操作SQL：{query}')
            costomer_context.set_source(source_name)
            query_result = self.dao.query(index=target, doc_type=self.DEFAULT_INDEX_TYPE, body=query, analyze_wildcard=True)
        except Exception as e:
            error = f'事实库{source_name}执行query操作SQL：{query} 发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()

        # 处理查询结果
        result = []
        if query_result and query_result['hits']:
            hits = query_result['hits']
            # 取结果
            if hits['hits']:
                result = [source['_source'] for source in hits['hits']]
            # 取总数
            total = None
            if page:
                if page.need_count():
                    total = hits['total']
                page.set_result(result, total)
                return page
        return Page.no_page(result)

    def _single_thread_inserts(self, table: str, result_list: list):
        """
        批量保存数据,要求list里面的字段和数据库里面的字段一一对应
        :param result_list: 要保存的数据
        :return:
        """
        source_name = self.fd().get_source_name()
        try:
            last_index = len(result_list) - 1
            costomer_context.set_source(source_name)
            for index, result in enumerate(result_list):
                # 寻找id字段
                if not isinstance(result, dict):
                    result = vars(result)
                id_tuple = self._get_id_from(result)
                if not id_tuple:
                    # 没设置id,只能用upsert,create要求id必填
                    self.dao.upsert(index=table, doc_type=self.DEFAULT_INDEX_TYPE, body=result, refresh=True)
                    continue
                else:
                    id = id_tuple[1]

                # 最后一个再刷新
                if index < last_index:
                    self.dao.create(index=table, doc_type=self.DEFAULT_INDEX_TYPE, id=id, body=result, refresh='wait_for')
                else:
                    self.dao.create(index=table, doc_type=self.DEFAULT_INDEX_TYPE, id=id, body=result, refresh=True)
        except Exception as e:
            error = f'事实库{source_name}执行inserts操作发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()

    def _single_thread_updates(self, table: str, result_list: list):
        """
        批量更新数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param result_list: 要修改的数据
        :return:
        """
        source_name = self.fd().get_source_name()
        try:
            last_index = len(result_list) - 1
            costomer_context.set_source(source_name)
            # TODO 暂时没有考虑事务
            for index, result in enumerate(result_list):
                # 寻找id字段
                if not isinstance(result, dict):
                    result = vars(result)
                id_tuple = self._get_id_from(result)
                if not id_tuple:
                    # 没有id字段，放弃该数据
                    log.warning(f'事实库{source_name}执行updates操作时未配置id字段,放弃该数据的更新：{result}')
                    continue
                else:
                    id = id_tuple[1]

                # 最后一个再刷新
                if index < last_index:
                    self.dao.partial_update(index=table, doc_type=self.DEFAULT_INDEX_TYPE, id=id, body=result, refresh='wait_for')
                else:
                    self.dao.partial_update(index=table, doc_type=self.DEFAULT_INDEX_TYPE, id=id, body=result, refresh=True)
        except Exception as e:
            error = f'事实库{source_name}执行updates操作发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()

    def _single_thread_inserts_or_updates(self, table: str, result_list: list):
        """
        批量saveOrUpdate数据,,数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param result_list: 要添加或者需要修改的数据
        :return:
        """
        source_name = self.fd().get_source_name()
        try:
            last_index = len(result_list) - 1
            costomer_context.set_source(source_name)
            for index, result in enumerate(result_list):
                # 寻找id字段
                if not isinstance(result, dict):
                    result = vars(result)
                id_tuple = self._get_id_from(result)
                if not id_tuple:
                    id = None
                    log.warning(f'事实库{source_name}执行upserts操作时未配置id字段：{result}')
                else:
                    id = id_tuple[1]

                # 最后一个再刷新
                if index < last_index:
                    self.dao.upsert(index=table, doc_type=self.DEFAULT_INDEX_TYPE, id=id, body=result, refresh='wait_for')
                else:
                    self.dao.upsert(index=table, doc_type=self.DEFAULT_INDEX_TYPE, id=id, body=result, refresh=True)
        except Exception as e:
            error = f'事实库{source_name}执行upserts操作发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()

    def delete_all(self):
        """
        清空数据
        :return:
        """
        source_name = self.fd().get_source_name()
        target = self.fd().target
        try:
            costomer_context.set_source(source_name)

            body = {
                "query": {
                    "match_all": {}
                }
            }
            self.dao.delete_by_query(index=target, body=body, doc_type=self.DEFAULT_INDEX_TYPE, analyze_wildcard=True)
        except Exception as e:
            error = f'事实库{source_name}执行delete_all操作发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()

    def delete(self, query: str):
        """
        根据删除语句删除数据,query是es的查询语句
        :return:
        """
        source_name = self.fd().get_source_name()
        target = self.fd().target
        log.debug(f'事实库{source_name}执行delete操作SQL：{query}')
        try:
            costomer_context.set_source(source_name)
            self.dao.delete_by_query(index=target, body=query, doc_type=self.DEFAULT_INDEX_TYPE, analyze_wildcard=True)
        except Exception as e:
            error = f'事实库{source_name}执行delete操作发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()
