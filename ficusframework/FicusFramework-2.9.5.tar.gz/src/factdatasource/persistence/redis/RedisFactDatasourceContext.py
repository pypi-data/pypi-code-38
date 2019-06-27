#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/21
import logging
from enum import Enum

from api.exceptions import IllegalArgumentException
from api.model.FactDatasource import FactDatasource
from api.model.Page import Page
from factdatasource.dao.redis.RedisDatasourceDao import RedisDatasourceDao
from factdatasource.execptions import NotSupportedFDException, FDExecuteException
from factdatasource.dao.FactDatasource import customer_dao_context_holder as costomer_context
from factdatasource.persistence.AbstractFactDatasourceContext import AbstractFactDatasourceContext

log = logging.getLogger('Ficus')


class OptionTypeEnum(Enum):
    LIST = 'LIST'
    SET = 'SET'
    VALUE = 'VALUE'
    HASH = 'HASH'


class RedisFactDatasourceContext(AbstractFactDatasourceContext):
    """
    redis的target格式是 value:XXXXX:30 list:XXXX:30 set:XXXXX:30 hash:XXXXX:30
    要指明类型和过期时间(秒),如果没有指明类型默认是 value，没有指明过期时间默认不过期
    """

    def __init__(self, fact_datasource: FactDatasource):
        self.fact_datasource = fact_datasource
        self.target_type = None

    @property
    def dao(self) -> RedisDatasourceDao:
        return RedisDatasourceDao.instance()

    def size(self):
        """
        返回数据总长度
        :return: 数据条数:long
        """
        source_name = self.fd().get_source_name()
        target_tuple = self.__analysis_target()
        option = target_tuple[0]
        name = target_tuple[1]
        try:
            costomer_context.set_source(source_name)
            if option == OptionTypeEnum.VALUE:
                result = self.dao.client.strlen(name)
            elif option == OptionTypeEnum.SET:
                result = self.dao.client.scard(name)
            elif option == OptionTypeEnum.HASH:
                result = self.dao.client.hlen(name)
            elif option == OptionTypeEnum.LIST:
                result = self.dao.client.llen(name)

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
        return self.size() <= 0

    def collect(self, size: int):
        """
        返回指定条数的数据
        :param size: 返回的条数
        :return: list
        """
        source_name = self.fd().get_source_name()
        target_tuple = self.__analysis_target()
        option = target_tuple[0]
        name = target_tuple[1]
        try:
            costomer_context.set_source(source_name)
            if option == OptionTypeEnum.VALUE:
                result = [self.dao.client.get(name)]
            elif option == OptionTypeEnum.SET:
                result = self.dao.client.srandmember(name, size)
            elif option == OptionTypeEnum.HASH:
                result = [self.dao.client.hgetall(name)]
            elif option == OptionTypeEnum.LIST:
                result = self.dao.client.lrange(name, 0, size)

            if result and size and len(result) > size:
                return result[0:size]
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
        target_tuple = self.__analysis_target()
        option = target_tuple[0]
        name = target_tuple[1]

        page = None
        if parameters and 'pageNum_' in parameters.keys() and 'pageSize_' in parameters.keys():
            # 需要分页的
            param = {
                'pageNum': parameters.get('pageNum_'),
                'pageSize': parameters.get('pageSize_'),
                'needCount': parameters.get('needCount_') if parameters.get('needCount_') else False
            }
            page = Page(**param)

        try:
            costomer_context.set_source(source_name)
            if option == OptionTypeEnum.VALUE:
                # value不会进行分页
                result = [self.dao.client.get(name)]
                page = Page.no_page(result)
            elif option == OptionTypeEnum.SET:
                result = list(self.dao.client.smembers(name))
                if page:
                    tmp = result[page.start_row:page.end_row]
                    page.set_result(tmp, len(result))
                else:
                    # TODO 这里如果没有分页，数据量过大可能会有问题
                    page = Page.no_page(result)
            elif option == OptionTypeEnum.HASH:
                if not query or '*' == query:
                    # 不能分页，顺序不好保证
                    result = [self.dao.client.hgetall(name)]
                else:
                    result = [self.dao.client.hget(name, query)]
                page = Page.no_page(result)
            elif option == OptionTypeEnum.LIST:
                if page:
                    result = self.dao.client.lrange(name, page.start_row, page.end_row)
                    total = None
                    if page.need_count():
                        total = self.dao.client.llen(name)
                    page.set_result(result, total)
                else:
                    result = self.dao.client.lrange(name, 0, -1)
                    page = Page.no_page(result)
            return page
        except Exception as e:
            error = f'事实库{source_name}执行size操作发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()

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
        target_tuple = self.__analysis_target()
        option = target_tuple[0]
        name = target_tuple[1]
        expire = target_tuple[2]

        try:
            costomer_context.set_source(source_name)
            if option == OptionTypeEnum.VALUE:
                for result in result_list:
                    self.dao.client.set(name, result)
            elif option == OptionTypeEnum.SET:
                self.dao.client.sadd(name, *result_list)
            elif option == OptionTypeEnum.HASH:
                for result in result_list:
                    self.dao.client.hmset(name, result)
            elif option == OptionTypeEnum.LIST:
                self.dao.client.rpush(name, *result_list)

            # 设置超时时间
            if expire:
                self.dao.client.expire(name, expire)
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
        self.inserts(result_list)

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
        # redis已经很快了,暂时不使用并发的方式执行
        raise NotSupportedFDException('redis不支持该操作')

    def _single_thread_updates(self, table: str, result_list: list):
        """
        批量更新数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param result_list: 要修改的数据
        :return:
        """
        # redis已经很快了,暂时不使用并发的方式执行
        raise NotSupportedFDException('redis不支持该操作')

    def _single_thread_inserts_or_updates(self, table: str, result_list: list):
        """
        批量saveOrUpdate数据,,数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param result_list: 要添加或者需要修改的数据
        :return:
        """
        # redis已经很快了,暂时不使用并发的方式执行
        raise NotSupportedFDException('redis不支持该操作')

    def delete_all(self):
        """
        清空数据
        :return:
        """
        source_name = self.fd().get_source_name()
        target_tuple = self.__analysis_target()
        name = target_tuple[1]
        try:
            costomer_context.set_source(source_name)
            self.dao.client.delete(name)
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
        raise NotSupportedFDException('redis不支持该操作')

    def __analysis_target(self) -> tuple:
        """
        分析redis的target，获取配置的类型和过期时间
        redis的 目标格式是  value:XXXXX:30  list:XXXX:30 set:XXXXX:30 hash:XXXXX:30
        需要指明类型.和过期时间 如果没有指明类型默认是 value 默认不过期
        :return: (OptionTypeEnum, target, int)
        """
        if self.target_type:
            return self.target_type

        target = self.fd().target
        if not target:
            raise IllegalArgumentException(f'redis的target配置错误，target不能为空。')

        split = target.split(":", 2)

        def get_type(option: str):
            if not option:
                return OptionTypeEnum.VALUE
            tmp = option.upper()
            if tmp == 'LIST':
                return OptionTypeEnum.LIST
            elif tmp == 'SET':
                return OptionTypeEnum.SET
            elif tmp == 'VALUE':
                return OptionTypeEnum.VALUE
            elif tmp == 'HASH':
                return OptionTypeEnum.HASH
            else:
                return OptionTypeEnum.VALUE

        if len(split) == 3:
            # 有超时时间
            self.target_type = (get_type(split[0]), split[1], int(split[2]), )
        elif len(split) == 2:
            # 没有超时时间
            self.target_type = (get_type(split[0]), split[1], None, )
        else:
            # 只有队列名
            self.target_type = (OptionTypeEnum.VALUE, split[0], None, )
        return self.target_type






