#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/3/11
import json

from sqlalchemy.engine import ResultProxy
from sqlalchemy.orm import Session

from api.exceptions import IllegalArgumentException
from api.model.FactDatasource import FactDatasourceTypeEnum
from api.model.GraphNode import GraphNode
from api.model.GraphRelation import GraphRelation
from factdatasource.dao.FactDatasource import Datasource
from factdatasource.dao.MultipleDatasourceHolder import get_multiple_datesource
from libs.utils import Singleton, uuid4


class GraphDatasourceDao(Singleton):

    @property
    def datasource(self) -> Datasource:
        data_source = get_multiple_datesource(FactDatasourceTypeEnum.JDBC)
        return data_source

    @property
    def client(self) -> Session:
        return self.datasource.get_client()

    # region 创建
    def create_node(self, table: str, graph_node: GraphNode) -> str:
        """
        创建一个节点
        :param table:
        :param graph_node:
        :return: 节点id
        """
        if not table or not graph_node:
            raise IllegalArgumentException('graph创建节点table或graph_node不能为空')

        if not graph_node.guid:
            guid = uuid4()
            graph_node.guid(guid)
        node_param = self.__convert_node(graph_node)

        sql = f'INSERT NODE(ID, TYPE, RESOURCEID,GROUP,TAGS) INTO {table} VALUES(:id,:type, :resourceId, :group, :tags)'
        result: ResultProxy = self.client.execute(sql, node_param)
        if result.rowcount > 0:
            return graph_node.guid
        return None

    def create_nodes(self, table: str, graph_nodes: list):
        """
        创建多个节点
        :param table:
        :param graph_nodes:
        :return:
        """
        if not table or not graph_nodes:
            raise IllegalArgumentException('graph创建节点table或graph_nodes不能为空')
        result = []
        for graph_node in graph_nodes:
            node_id = self.create_node(table, graph_node)
            result.append(node_id)
        return result

    def create_relation(self, table: str, graph_relation: GraphRelation) -> str:
        """
        创建一个节点
        :param table:
        :param graph_relation:
        :return: 节点id
        """
        if not table or not graph_relation or not graph_relation.from_ or not graph_relation.to:
            raise IllegalArgumentException('graph创建关系参数错误')

        if not graph_relation.guid:
            guid = uuid4()
            graph_relation.guid(guid)
        relation_param = self.__convert_relation(graph_relation)

        sql = f'INSERT RELATION(ID, TYPE ,GROUP, TAGS) INTO {table} VIA NODE1(ID = :id1) TO NODE2(ID = :id2) ' \
              f'VALUES(:id,:type,:group,:tags)'
        result: ResultProxy = self.client.execute(sql, relation_param)
        if result.rowcount > 0:
            return graph_relation.guid
        return None

    def create_relations(self, table: str, graph_relations: list):
        """
        创建多个关系
        :param table:
        :param graph_relations:
        :return:
        """
        if not table or not graph_relations:
            raise IllegalArgumentException('graph创建关系参数错误')

        result = []
        for graph_relation in graph_relations:
            relation_id = self.create_relation(table, graph_relation)
            result.append(relation_id)
        return result

    # endregion

    # region Exists
    def node_exists(self, table: str, id: str) -> bool:
        """
        节点是否存在
        :param id:
        :return:
        """
        return self.get_one_node(table, id) != None

    # endregion

    # region get
    def get_one_node(self, table: str, id: str):
        """
        根据id获取一个节点
        :param table:
        :param id:
        :return:
        """
        param = {'ID': id}
        sql = f'SELECT * FROM NODE {table} WHERE ID = :ID'
        result: ResultProxy = self.client.execute(sql, param)
        row = result.fetchone()
        if not row:
            return None
        return dict(zip(row.keys(), row))

    def get_one_relation(self, table: str, id: str):
        """
        根据id获取一个关系
        :param table:
        :param id:
        :return:
        """
        param = {'ID': id}
        sql = f'SELECT * FROM RELATION {table} WHERE ID = :ID'
        result: ResultProxy = self.client.execute(sql, param)
        row = result.fetchone()
        if not row:
            return None
        return dict(zip(row.keys(), row))

    # endregion

    # region delete
    def delte_node_by_id(self, table: str, id: str):
        """
        根据id删除一个节点
        :param table:
        :param id:
        :return:
        """
        param = {'ID': id}
        sql = f'DELETE NODE FROM {table} WHERE ID = :ID'
        result: ResultProxy = self.client.execute(sql, param)
        return result.rowcount > 0

    def delte_relation_by_id(self, table: str, id: str):
        """
        删除关系
        :param table:
        :param id:
        :return:
        """
        param = {'ID': id}
        sql = f'DELETE RELATION FROM {table} WHERE ID = :ID'
        result: ResultProxy = self.client.execute(sql, param)
        return result.rowcount > 0

    def delete_by_query(self, query: str, param: dict = None):
        """
        根据查询来删除
        :param query:
        :param param:
        :return:
        """
        result: ResultProxy = self.client.execute(query, param)
        return result.rowcount > 0
    # endregion

    # region update
    def update_relation_tags(self, table: str, group_guid: str, graph_relation: GraphRelation):
        """
        修改关系标签
        :param table:
        :param group_guid:
        :param graph_relation:
        :return:
        """
        param = {
            'group': group_guid,
            'id': graph_relation.guid,
            'tags': json.dumps(graph_relation.tags) if graph_relation.tags else None,
        }
        sql = f'UPDATE RELATION FROM {table}  SET TAGS= :tags WHERE ID = :id AND GROUP = :group '
        result: ResultProxy = self.client.execute(sql, param)
        return result.rowcount > 0

    def update_node_tags(self, table: str, group_guid: str, graph_node: GraphNode):
        """
        修改关系标签
        :param table:
        :param group_guid:
        :param graph_node:
        :return:
        """
        param = {
            'group': group_guid,
            'id': graph_node.guid,
            'tags': json.dumps(graph_node.tags) if graph_node.tags else None,
        }
        sql = f'UPDATE NODE FROM {table}  SET TAGS= :tags WHERE ID = :id AND GROUP = :group '
        result: ResultProxy = self.client.execute(sql, param)
        return result.rowcount > 0
    # endregion

    # region query
    def query(self, sql: str, params: dict = None) -> list:
        """
        查询所有结果
        :param sql:
        :param params:
        :return:
        """
        result = self.client.execute(sql, params)
        rows = result.fetchall()
        if not rows:
            return []
        return [dict(zip(row.keys(), row)) for row in rows]

    def query_total(self, sql: str, params: dict = None):
        """
        查询sql的返回结果有多少条
        :param sql:
        :param params:
        :return:
        """
        count_result = self.client.execute(sql, params)
        count_result.close()
        return count_result.rowcount
    # endregion

    def __convert_node(self, graph_node: GraphNode):
        node = {
            'id': graph_node.guid,
            'group': graph_node.get('GROUP'),
            'type': graph_node.type,
            'resourceId': graph_node.guid,
            'tags': json.dumps(graph_node.tags) if graph_node.tags else None,
        }
        return node

    def __convert_relation(self, graph_relation: GraphRelation):
        relation = {
            'id': graph_relation.guid,
            'id1': graph_relation.from_.guid,
            'id2': graph_relation.to.guid,
            'group': graph_relation.get('GROUP'),
            'type': graph_relation.type,
            'tags': json.dumps(graph_relation.tags) if graph_relation.tags else None,
        }
        return relation
