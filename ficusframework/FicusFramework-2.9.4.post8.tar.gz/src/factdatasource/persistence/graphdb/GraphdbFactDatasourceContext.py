#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/21
import logging

from api.model.GraphNode import GraphNode
from api.model.GraphRelation import GraphRelation
from api.model.Page import Page
from factdatasource.dao.FactDatasource import customer_dao_context_holder as costomer_context
from factdatasource.dao.graph.GraphDatasourceDao import GraphDatasourceDao
from factdatasource.execptions import FDExecuteException
from factdatasource.persistence.AbstractFactDatasourceContext import AbstractFactDatasourceContext

log = logging.getLogger('Ficus')


class GraphdbFactDatasourceContext(AbstractFactDatasourceContext):

    DEFAULT_GROUP = 'ficus'

    @property
    def dao(self) -> GraphDatasourceDao:
        return GraphDatasourceDao.instance()

    def size(self):
        """
        返回数据总长度
        :return: 数据条数:long
        """
        return 0

    def is_empty(self):
        """
        返回是否存在数据
        :return: boolean
        """
        return False

    def collect(self, size: int):
        """
        返回指定条数的数据
        :param size: 返回的条数
        :return: list
        """
        return None

    def query(self, query: str, parameters: dict):
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

            result = self.dao.query(sql, parameters)
            if page:
                total = None
                if page.need_count():
                    total = self.dao.query_total(query, parameters)
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

    def _query_page_sql(self, query: str, page: Page = None):
        """
        构造分页语句
        :param query: 原始SQL
        :param page:
        :return:
        """
        if page:
            sql = f'{query} LIMIT {page.start_row},{page.end_row}'
        else:
            sql = query
        return sql

    def _single_thread_inserts(self, table: str, result_list: list):
        """
        批量保存数据,要求list里面的字段和数据库里面的字段一一对应
        :param result_list: 要保存的数据
        :return:
        """
        source_name = self.fd().get_source_name()
        try:
            costomer_context.set_source(source_name)
            for result in result_list:
                if not isinstance(result, GraphNode) and not isinstance(result, GraphRelation):
                    # 不是图结构就无法保存
                    log.warning(f'保存图结构数据类型错误，放弃保存数据:{result}')
                    continue
                self._inner_insert(table, result)
        finally:
            costomer_context.clear_source()

    def _inner_insert(self, table: str, result):
        try:
            if isinstance(result, GraphNode):
                # 插入节点
                self._inner_insert_node(table, result)
            elif isinstance(result, GraphRelation):
                # 插入关系
                self._inner_insert_relation(table, result)
        except Exception as e:
            source_name = self.fd().get_source_name()
            error = f'事实库{source_name}执行inserts操作发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)

    def _inner_insert_node(self, table: str, graph_node: GraphNode):
        graph_node['GROUP'] = self.DEFAULT_GROUP
        self.dao.create_node(table, graph_node)

    def _inner_insert_relation(self, table: str, graph_relation: GraphRelation):
        graph_relation['GROUP'] = self.DEFAULT_GROUP
        self.dao.create_relation(table, graph_relation)

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
                if not isinstance(result, GraphNode) and not isinstance(result, GraphRelation):
                    # 不是图结构就无法修改
                    continue
                self._inner_update(table, result)
        finally:
            costomer_context.clear_source()

    def _inner_update(self, table: str, result) -> bool:
        try:
            if isinstance(result, GraphNode):
                # 修改节点
                return self._inner_update_node(table, result)
            elif isinstance(result, GraphRelation):
                # 修改关系
                return self._inner_update_relation(table, result)
        except Exception as e:
            source_name = self.fd().get_source_name()
            error = f'事实库{source_name}执行inserts操作发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)

    def _inner_update_node(self, table, graph_node: GraphNode) -> bool:
        if graph_node.guid and graph_node.tags:
            return self.dao.update_node_tags(table, self.DEFAULT_GROUP, graph_node)
        else:
            # 信息不全无法进行修改
            log.warning(f'修改图节点时信息不全无法修改{graph_node}')
            return False

    def _inner_update_relation(self, table, graph_relation: GraphRelation) -> bool:
        if graph_relation.guid and graph_relation.tags:
            return self.dao.update_relation_tags(table, self.DEFAULT_GROUP, graph_relation)
        else:
            # 信息不全无法进行修改
            log.warning(f'修改图节点关系时信息不全无法修改{graph_relation}')
            return False

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
                if not isinstance(result, GraphNode) and not isinstance(result, GraphRelation):
                    # 不是图结构就无法保存
                    continue
                if not self._inner_update(table, result):
                    # 没有修改成功，尝试插入操作
                    try:
                        self._inner_insert(table, result)
                    except Exception as e:
                        # 重新尝试一次修改
                        self._inner_update(table, result)
        finally:
            costomer_context.clear_source()

    def delete_all(self):
        """
        清空数据
        :return:
        """
        table = self.fd().target
        source_name = self.fd().get_source_name()
        try:
            costomer_context.set_source(source_name)
            delete_relation_sql = f'DELETE RELATION FROM {table}'
            self.dao.delete_by_query(delete_relation_sql)
            delete_node_sql = f'DELETE NODE FROM {table}'
            self.dao.delete_by_query(delete_node_sql)
        except Exception as e:
            error = f'事实库{source_name}执行delete_all操作发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()

    def delete(self, query: str):
        """
        根据删除语句删除数据,query是完整的删除语句
        :return:
        """
        source_name = self.fd().get_source_name()
        try:
            costomer_context.set_source(source_name)
            self.dao.delete_by_query(query)
        except Exception as e:
            error = f'事实库{source_name}执行delete操作发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()

