#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/23
from elasticsearch import Elasticsearch

from api.model.FactDatasource import FactDatasourceTypeEnum
from factdatasource.dao.FactDatasource import Datasource
from factdatasource.dao.MultipleDatasourceHolder import get_multiple_datesource
from libs.utils import Singleton


class EsDatasourceDao(Singleton):

    @property
    def datasource(self) -> Datasource:
        data_source = get_multiple_datesource(FactDatasourceTypeEnum.ES)
        return data_source

    @property
    def client(self) -> Elasticsearch:
        return self.datasource.get_client()

    def count(self, index=None, doc_type=None, body=None, **params):
        """
        获取数据条数
        :param index:
        :param doc_type:
        :param body:
        :param params:
        :return:
        """
        count_result = self.client.count(index=index, doc_type=doc_type, body=body, params=params)
        if count_result:
            return count_result.get('count')

    def simple_query(self, index=None, doc_type=None, body=None, **params):
        """
        简单查询，直接返回数据结果
        :param index:
        :param doc_type:
        :param body:
        :param params:
        :return:
        """
        result = self.client.search(index=index, doc_type=doc_type, body=body, params=params)
        hits = result['hits']['hits']
        if hits:
            return [source['_source'] for source in hits]

    def query(self, index=None, doc_type=None, body=None, **params):
        """
        普通查询
        :param index:
        :param doc_type:
        :param body:
        :param params:
        :return:
        """
        return self.client.search(index=index, doc_type=doc_type, body=body, params=params)

    def delete_by_query(self, index, body, doc_type=None, **params):
        """
        根据查询结果进行删除，es版本需要5.0以上才支持
        :param index:
        :param body:
        :param doc_type:
        :param params:
        :return:
        """
        params['refresh'] = True
        return self.client.delete_by_query(index=index, doc_type=doc_type, body=body, params=params)

    def create(self, index, doc_type, id, body, **params):
        """
        添加数据
        :param index:
        :param doc_type:
        :param id:
        :param body:
        :param params:
        :return:
        """
        return self.client.create(index=index, doc_type=doc_type, id=id, body=body, params=params)

    def partial_update(self, index, doc_type, id, body=None, **params):
        """
        部分更新
        :param index:
        :param doc_type:
        :param id:
        :param body:
        :param params:
        :return:
        """
        upbody = {
            'doc': body
        }
        return self.client.update(index, doc_type, id, body=upbody, params=params)

    def upsert(self, index, doc_type, body, id=None, **params):
        """
        修改或添加
        :param index:
        :param doc_type:
        :param body:
        :param id:
        :param params:
        :return:
        """
        return self.client.index(index=index, doc_type=doc_type, body=body, id=id, params=params)
