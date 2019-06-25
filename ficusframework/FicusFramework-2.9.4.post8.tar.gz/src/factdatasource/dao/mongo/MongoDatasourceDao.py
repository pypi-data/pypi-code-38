#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/31

from pymongo.collection import Collection
from pymongo.cursor import Cursor

from api.exceptions import IllegalArgumentException
from api.model.FactDatasource import FactDatasourceTypeEnum
from factdatasource.dao.FactDatasource import Datasource
from factdatasource.dao.MultipleDatasourceHolder import get_multiple_datesource
from libs.utils import Singleton


class MongoDatasourceDao(Singleton):

    @property
    def datasource(self) -> Datasource:
        data_source = get_multiple_datesource(FactDatasourceTypeEnum.MONGO)
        return data_source

    def client(self, target) -> Collection:
        if not target:
            raise IllegalArgumentException('获取MONGO操作客户端参数不合法，target不能为空。')
        return self.datasource.get_client()[target]

    def count_documents(self, target, filter={}, **kwargs):
        """
        统计一个Collection中的条数
        :param target:
        :param filter:
        :param kwargs:
        :return:
        """
        count = self.client(target).count_documents(filter, **kwargs)
        return count

    def find(self, target, *args, **kwargs) -> list:
        """
        简单查询
        :param target:
        :param args:
        :param kwargs:
        :return:
        """
        client: Collection = self.client(target)
        result: Cursor = client.find(*args, **kwargs)
        return list(result)

    def map_reduce(self, target, map, reduce, out, **kwargs):
        """
        map_reduce查询
        :param target:
        :param map:
        :param reduce:
        :param out:
        :param kwargs:
        :return:
        """
        client: Collection = self.client(target)
        result = client.map_reduce(map, reduce, out, **kwargs)
        return result

    def aggregate(self, target, pipeline, **kwargs):
        """
        聚合管道查询
        :param target:
        :param pipeline:
        :param kwargs:
        :return: 这里返回的是查询到的所有结果
        """
        client: Collection = self.client(target)
        result: Cursor = client.aggregate(pipeline, **kwargs)
        return list(result)

    def delete_many(self, target, filter):
        """
        根据条件删除数据
        :param target:
        :param filter: mongo查询条件
        :return:
        """
        client: Collection = self.client(target)
        client.delete_many(filter)

    def drop(self, target):
        """
        删除collection
        :param target:
        :return:
        """
        client: Collection = self.client(target)
        client.drop()

    def insert(self, target, documents: list):
        """
        添加数据
        :param target:
        :param documents:
        :return:
        """
        if not documents:
            return
        client: Collection = self.client(target)
        client.insert_many(documents)

    def update_one(self, target, filter, document: dict, upsert=False):
        """
        修改数据
        :param target:
        :param filter:
        :param document:
        :param upsert: 数据不存在是否进行插入操作
        :return:
        """
        if not filter or not document:
            raise IllegalArgumentException('修改MONGO数据时参数不合法，filter、document不能为空。')
        client: Collection = self.client(target)
        update_doc = {"$set": document}
        client.update_one(filter, update_doc, upsert=upsert)



