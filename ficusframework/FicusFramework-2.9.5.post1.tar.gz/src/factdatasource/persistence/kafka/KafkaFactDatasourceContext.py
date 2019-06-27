#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/21
import logging

from factdatasource.dao.FactDatasource import customer_dao_context_holder as costomer_context
from factdatasource.dao.kafka.KafkaDatasourceDao import KafkaDatasourceDao
from factdatasource.execptions import NotSupportedFDException, FDExecuteException
from factdatasource.persistence.AbstractFactDatasourceContext import AbstractFactDatasourceContext

log = logging.getLogger('Ficus')


class KafkaFactDatasourceContext(AbstractFactDatasourceContext):

    @property
    def dao(self) -> KafkaDatasourceDao:
        return KafkaDatasourceDao.instance()

    def size(self):
        """
        返回数据总长度
        :return: 数据条数:long
        """
        raise NotSupportedFDException('kafka不支持该操作')

    def is_empty(self):
        """
        返回是否存在数据
        :return: boolean
        """
        raise NotSupportedFDException('kafka不支持该操作')

    def collect(self, size: int):
        """
        返回指定条数的数据
        :param size: 返回的条数
        :return: list
        """
        raise NotSupportedFDException('kafka不支持该操作')

    def query(self, query: str, parameters: dict = None):
        """
        使用查询语句查询数据
        :param query: 查询语句
        :param parameters: 查询参数
        :return: Page
        """
        raise NotSupportedFDException('kafka不支持该操作')

    def inserts(self, result_list: list):
        """
        批量保存数据,要求list里面的字段和数据库里面的字段一一对应
        :param result_list: 要保存的数据
        :return:
        """
        if not result_list:
            return
        if not isinstance(result_list, list):
            result_list = [result_list]

        source_name = self.fd().get_source_name()
        topic = self.fd().target
        try:
            costomer_context.set_source(source_name)
            for result in result_list:
                self.dao.producer.produce(topic, result)
            self.dao.producer.flush(30)
        except Exception as e:
            error = f'事实库{source_name}执行size操作发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()

    def updates(self, result_list: list):
        """
        批量更新数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param result_list: 要修改的数据
        :return:
        """
        raise NotSupportedFDException('kafka不支持该操作')

    def inserts_or_updates(self, result_list: list):
        """
        批量saveOrUpdate数据,,数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param result_list: 要添加或者需要修改的数据
        :return:
        """
        self.inserts(result_list)

    def _single_thread_inserts(self, table: str, result_list: list):
        """
        批量保存数据,要求list里面的字段和数据库里面的字段一一对应
        :param result_list: 要保存的数据
        :return:
        """
        # 消息可能是有顺序的,因此先不并发
        raise NotSupportedFDException('kafka不支持该操作')

    def _single_thread_updates(self, table: str, result_list: list):
        """
        批量更新数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param result_list: 要修改的数据
        :return:
        """
        # 消息可能是有顺序的,因此先不并发
        raise NotSupportedFDException('kafka不支持该操作')

    def _single_thread_inserts_or_updates(self, table: str, result_list: list):
        """
        批量saveOrUpdate数据,,数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param result_list: 要添加或者需要修改的数据
        :return:
        """
        # 消息可能是有顺序的,因此先不并发
        raise NotSupportedFDException('kafka不支持该操作')

    def delete_all(self):
        """
        清空数据
        :return:
        """
        raise NotSupportedFDException('kafka不支持该操作')

    def delete(self, query: str):
        """
        根据删除语句删除数据,query是完整的删除语句
        :return:
        """
        raise NotSupportedFDException('kafka不支持该操作')
