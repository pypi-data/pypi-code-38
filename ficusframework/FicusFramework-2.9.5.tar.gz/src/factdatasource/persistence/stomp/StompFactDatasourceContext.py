#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/21
import json
import logging

from factdatasource.dao.FactDatasource import customer_dao_context_holder as costomer_context
from factdatasource.dao.stomp.StompDatasourceDao import StompDatasourceDao
from factdatasource.execptions import NotSupportedFDException, FDExecuteException
from factdatasource.persistence.AbstractFactDatasourceContext import AbstractFactDatasourceContext
from libs.utils import JSONEncoder

log = logging.getLogger('Ficus')


class StompFactDatasourceContext(AbstractFactDatasourceContext):

    @property
    def dao(self) -> StompDatasourceDao:
        return StompDatasourceDao.instance()

    def size(self):
        """
        返回数据总长度
        :return: 数据条数:long
        """
        raise NotSupportedFDException('stomp不支持该操作')

    def is_empty(self):
        """
        返回是否存在数据
        :return: boolean
        """
        raise NotSupportedFDException('stomp不支持该操作')

    def collect(self, size: int):
        """
        返回指定条数的数据
        :param size: 返回的条数
        :return: list
        """
        raise NotSupportedFDException('stomp不支持该操作')

    def query(self, query: str, parameters: dict):
        """
        使用查询语句查询数据
        :param query: 查询语句
        :param parameters: 查询参数
        :return: Page
        """
        raise NotSupportedFDException('stomp不支持该操作')

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
        destination = self.fd().target

        try:
            costomer_context.set_source(source_name)
            for result in result_list:
                if not isinstance(result, str):
                    result = json.dumps(result, cls=JSONEncoder)
                self.dao.send(destination, result)
        except Exception as e:
            error = f'事实库{source_name}执行inserts操作发生异常, {str(e)}'
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
        raise NotSupportedFDException('stomp不支持该操作')

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
        raise NotSupportedFDException('stomp不支持该操作')

    def _single_thread_updates(self, table: str, result_list: list):
        """
        批量更新数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param result_list: 要修改的数据
        :return:
        """
        raise NotSupportedFDException('stomp不支持该操作')

    def _single_thread_inserts_or_updates(self, table: str, result_list: list):
        """
        批量saveOrUpdate数据,,数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param result_list: 要添加或者需要修改的数据
        :return:
        """
        raise NotSupportedFDException('stomp不支持该操作')

    def delete_all(self):
        """
        清空数据
        :return:
        """
        raise NotSupportedFDException('stomp不支持该操作')

    def delete(self, query: str):
        """
        根据删除语句删除数据,query是完整的删除语句
        :return:
        """
        raise NotSupportedFDException('stomp不支持该操作')

