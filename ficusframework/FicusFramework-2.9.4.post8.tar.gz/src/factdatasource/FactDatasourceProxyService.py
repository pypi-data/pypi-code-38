#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/21
from abc import abstractmethod

import requests
from munch import Munch

from api.exceptions import ServiceInnerException, IllegalArgumentException, AuthException
from client import check_instance_avaliable, do_service
from config.annotation import Value
from factdatasource.FactDatasourceContext import FactDatasourceContext
from factdatasource.FactDatasourceContextHolder import FactDatasourceContextHolder
from factdatasource.dao.jdbc.MultipleJdbcDatasource import register_jdbc_default_datasource
from factdatasource.dao.kafka.MultipleKafkaDatasource import register_kafka_default_datasource
from factdatasource.message.FactDatasourceMessageHanlder import FactDatasourceChangeListener
from libs.utils import Singleton
from service.FactDatasourceService import FactDatasourceService


class FactDatasourceProxy(object):

    @abstractmethod
    def fd(self, fd_code: str):
        """
        返回fd对象
        :param fd_code:
        :return: FactDatasource
        """

    @abstractmethod
    def size(self, fd_code: str):
        """
        返回数据总长度
        :param fd_code:
        :return: 数据条数:long
        """

    @abstractmethod
    def is_empty(self, fd_code: str):
        """
        返回是否存在数据
        :param fd_code:
        :return: boolean
        """

    @abstractmethod
    def collect(self, fd_code: str, size: int):
        """
        返回指定条数的数据
        :param fd_code:
        :param size: 返回的条数
        :return: list
        """

    @abstractmethod
    def query(self, fd_code: str, query: str, parameters: dict):
        """
        使用查询语句查询数据
        :param fd_code:
        :param query: 查询语句
        :param parameters: 查询参数
        :return: Page
        """

    @abstractmethod
    def inserts(self, fd_code: str, result_list: list):
        """
        批量保存数据,要求list里面的字段和数据库里面的字段一一对应
        :param fd_code:
        :param result_list: 要保存的数据
        :return:
        """

    @abstractmethod
    def updates(self, fd_code: str, result_list: list):
        """
        批量更新数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param fd_code:
        :param result_list: 要修改的数据
        :return:
        """

    @abstractmethod
    def save_or_updates(self, fd_code: str, result_list: list):
        """
        批量saveOrUpdate数据,,数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param fd_code:
        :param result_list: 要添加或者需要修改的数据
        :return:
        """

    @abstractmethod
    def delete_all(self, fd_code: str):
        """
        清空数据
        :param fd_code:
        :return:
        """

    @abstractmethod
    def delete(self, fd_code: str, query: str):
        """
        根据删除语句删除数据,query是完整的删除语句
        :param fd_code:
        :param query:
        :return:
        """

    # @abstractmethod
    # def get_fact_datasource_fields(self, fd_code: str):
    #     """
    #     这个python版暂时用不到，先不实现
    #     获取fd的字段
    #     :param fd_code:
    #     :return: List<FactDatasourceField>
    #     """

    @abstractmethod
    def exists_fds(self, fd_codes: list) -> bool:
        """
        判断fd是否存在
        :param fd_codes:
        :return:
        """


class DistributedFactDatasourceProxy(FactDatasourceProxy, Singleton):
    """
    本地直接使用FD操作数据库的方式
    """

    def fd(self, fd_code: str):
        """
        返回fd对象
        :param fd_code:
        :return: FactDatasource
        """
        return self._get_fd_context(fd_code).fd()

    def size(self, fd_code: str):
        """
        返回数据总长度
        :param fd_code:
        :return: 数据条数:long
        """
        fd_context = self._get_fd_context(fd_code)
        self._inner_check_permission(fd_context, 'read')
        return fd_context.size()

    def is_empty(self, fd_code: str):
        """
        返回是否存在数据
        :param fd_code:
        :return: boolean
        """
        fd_context = self._get_fd_context(fd_code)
        self._inner_check_permission(fd_context, 'read')
        return fd_context.is_empty()

    def collect(self, fd_code: str, size: int):
        """
        返回指定条数的数据
        :param fd_code:
        :param size: 返回的条数
        :return: list
        """
        fd_context = self._get_fd_context(fd_code)
        self._inner_check_permission(fd_context, 'read')
        return fd_context.collect(size)

    def query(self, fd_code: str, query: str, parameters: dict):
        """
        使用查询语句查询数据
        :param fd_code:
        :param query: 查询语句
        :param parameters: 查询参数
        :return: Page
        """
        fd_context = self._get_fd_context(fd_code)
        self._inner_check_permission(fd_context, 'read')
        return fd_context.query(query, parameters)

    def inserts(self, fd_code: str, result_list: list):
        """
        批量保存数据,要求list里面的字段和数据库里面的字段一一对应
        :param fd_code:
        :param result_list: 要保存的数据
        :return:
        """
        fd_context = self._get_fd_context(fd_code)
        self._inner_check_permission(fd_context, 'write')
        return fd_context.inserts(result_list)

    def updates(self, fd_code: str, result_list: list):
        """
        批量更新数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param fd_code:
        :param result_list: 要修改的数据
        :return:
        """
        fd_context = self._get_fd_context(fd_code)
        self._inner_check_permission(fd_context, 'write')
        return fd_context.updates(result_list)

    def save_or_updates(self, fd_code: str, result_list: list):
        """
        批量saveOrUpdate数据,,数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param fd_code:
        :param result_list: 要添加或者需要修改的数据
        :return:
        """
        fd_context = self._get_fd_context(fd_code)
        self._inner_check_permission(fd_context, 'write')
        return fd_context.inserts_or_updates(result_list)

    def delete_all(self, fd_code: str):
        """
        清空数据
        :param fd_code:
        :return:
        """
        fd_context = self._get_fd_context(fd_code)
        self._inner_check_permission(fd_context, 'delete')
        return fd_context.delete_all()

    def delete(self, fd_code: str, query: str):
        """
        根据删除语句删除数据,query是完整的删除语句
        :param fd_code:
        :param query:
        :return:
        """
        fd_context = self._get_fd_context(fd_code)
        self._inner_check_permission(fd_context, 'delete')
        return fd_context.delete(query)

    # def get_fact_datasource_fields(self, fd_code: str):
    #     """
    #     获取fd的字段
    #     :param fd_code:
    #     :return: List<FactDatasourceField>
    #     """
    #     fd_context = self._get_fd_context(fd_code)
    #     self._inner_check_permission(fd_context, 'execute')
    #     return fd_context.get_fact_datasource_fields()

    def exists_fds(self, fd_codes: list) -> bool:
        """
        判断fd是否存在
        :param fd_codes:
        :return:
        """
        if not fd_codes:
            return False

        if not isinstance(fd_codes, list):
            raise IllegalArgumentException("检测fd是否存在失败,输入参数不是一个list")

        fd_service = FactDatasourceService.instance()
        return fd_service.exists_fds(fd_codes)

    def _get_fd_context(self, fd_code: str):
        fd_context: FactDatasourceContext = FactDatasourceContextHolder.instance().get_fact_datasource(fd_code)
        return fd_context

    def _inner_check_permission(self, fd_context: FactDatasourceContext, operation: str):
        # TODO 暂未实现内容权限验证
        return True


class CentralizedFactDatasourceProxy(FactDatasourceProxy, Singleton):
    """
    集中式的FD获取,也就是传统的 调用ficus-web的方式来获取fd
    """

    def fd(self, fd_code: str):
        """
        获取某一个FD对象
        :param fd_code: fd的唯一code
        :return: FD对象
        """
        check_instance_avaliable()

        try:
            r = do_service(f"/remote/fd-service/{fd_code}")

            if r is not None:
                return Munch(r)
            else:
                return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 500:
                # 说明服务器端报错了
                raise ServiceInnerException(e.response._content.decode('utf-8'))
            elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
                # 说明是认证相关的错误
                raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
            raise e

    def size(self, fd_code: str):
        """
        获取数据的条数
        :param fd_code:  fd的唯一code
        :return: 数据的条数 没得就返回0
        """
        check_instance_avaliable()

        try:
            r = do_service(f"/remote/fd-service/{fd_code}/size")

            if  r is not None:
                return r
            else:
                return 0
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 500:
                # 说明服务器端报错了
                raise ServiceInnerException(e.response._content.decode('utf-8'))
            elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
                # 说明是认证相关的错误
                raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
            raise e

    def is_empty(self, fd_code: str):
        """
        判断数据集是否为空
        :param fd_code: fd的唯一code
        :return: 如果为空返回True,否则返回False
        """
        check_instance_avaliable()

        try:
            r = do_service(f"/remote/fd-service/{fd_code}/empty")

            if r is not None:
                return r
            else:
                return True
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 500:
                # 说明服务器端报错了
                raise ServiceInnerException(e.response._content.decode('utf-8'))
            elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
                # 说明是认证相关的错误
                raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
            raise e

    def collect(self, fd_code: str, size: int):
        """
        返回整个数据集
        :param fd_code: fd的唯一code
        :return:
        """
        check_instance_avaliable()

        try:
            r = do_service(f"/remote/fd-service/{fd_code}/all")
            if r is not None:
                if isinstance(r, list):
                    return [Munch(x) for x in r]
                else:
                    return Munch(r)
            else:
                return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 500:
                # 说明服务器端报错了
                raise ServiceInnerException(e.response._content.decode('utf-8'))
            elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
                # 说明是认证相关的错误
                raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
            raise e

    def query(self, fd_code: str, query: str, parameters: dict):
        """
        对数据集进行查询
        :param fd_code: fd的唯一code
        :param query_str: 查询语句
        :param parameters: 查询可能涉及的参数 K/V形式
        :return:
        """
        check_instance_avaliable()

        try:
            r = do_service(f"/remote/fd-service/{fd_code}/query",method="post",data=parameters,params={'query': query})

            if r is not None:
                if isinstance(r, list):
                    return [Munch(x) for x in r]
                else:
                    return Munch(r)
            else:
                return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 500:
                # 说明服务器端报错了
                raise ServiceInnerException(e.response._content.decode('utf-8'))
            elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
                # 说明是认证相关的错误
                raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
            raise e

    def inserts(self, fd_code: str, result_list: list):
        """
        增加数据
        :param fd_code: fd的唯一code
        :param result_list: 要被写入的数据 是一个List
        :return:
        """
        if result_list is None:
            return

        if not isinstance(result_list, list):
            raise IllegalArgumentException("输入的参数:result_list 不是数组")

        check_instance_avaliable()

        request = []
        for result in result_list:
            if not isinstance(result, Munch):
                # 说明不是 Munch类型的 判断是否是Dict的
                if isinstance(result, dict):
                    # 如果是dict类型的,直接发
                    request.append(result)
            else:
                # 说明是munch的,那么就转成Dict的
                request.append(result.toDict())

        try:
            r = do_service(f"/remote/fd-service/{fd_code}", method="post", data=request,return_type="None")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 500:
                # 说明服务器端报错了
                raise ServiceInnerException(e.response._content.decode('utf-8'))
            elif e.response.status_code >= 400 and e.response.status_code < 500:
                # 说明是认证相关的错误
                raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
            raise e

    def updates(self, fd_code: str, result_list: list):
        """
        更新数据
        :param fd_code: fd的唯一code
        :param result_list: 要被更新的数据 是一个List
        :return:
        """
        if result_list is None:
            return

        if not isinstance(result_list, list):
            raise IllegalArgumentException("输入的参数:result_list 不是数组")

        check_instance_avaliable()

        request = []
        for result in result_list:
            if not isinstance(result, Munch):
                # 说明不是 Munch类型的 判断是否是Dict的
                if isinstance(result, dict):
                    # 如果是dict类型的,直接发
                    request.append(result)
            else:
                # 说明是munch的,那么就转成Dict的
                request.append(result.toDict())

        try:
            r = do_service(f"/remote/fd-service/{fd_code}", method="put", data=request, return_type="None")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 500:
                # 说明服务器端报错了
                raise ServiceInnerException(e.response._content.decode('utf-8'))
            elif e.response.status_code >= 400 and e.response.status_code < 500:
                # 说明是认证相关的错误
                raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
            raise e


    def save_or_updates(self, fd_code: str, result_list: list):
        """
        新增或更新数据
        :param fd_code:  fd的唯一code
        :param result_list: upsertCache
        :return:
        """
        if result_list is None:
            return

        if not isinstance(result_list, list):
            raise IllegalArgumentException("输入的参数:result_list 不是数组")

        check_instance_avaliable()

        request = []
        for result in result_list:
            if not isinstance(result, Munch):
                # 说明不是 Munch类型的 判断是否是Dict的
                if isinstance(result, dict):
                    # 如果是dict类型的,直接发
                    request.append(result)
            else:
                # 说明是munch的,那么就转成Dict的
                request.append(result.toDict())

        try:
            r = do_service(f"/remote/fd-service/{fd_code}/upsert", method="post", data=request, return_type="None")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 500:
                # 说明服务器端报错了
                raise ServiceInnerException(e.response._content.decode('utf-8'))
            elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
                # 说明是认证相关的错误
                raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
            raise e


    def delete_all(self, fd_code: str):
        """
        删除数据集中所有数据
        :param fd_code: fd的唯一code
        :return:
        """
        check_instance_avaliable()

        try:
            r = do_service(f"/remote/fd-service/{fd_code}", method="delete", return_type="None")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 500:
                # 说明服务器端报错了
                raise ServiceInnerException(e.response._content.decode('utf-8'))
            elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
                # 说明是认证相关的错误
                raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
            raise e

    def delete(self, fd_code: str, query: str):
        """
        删除数据集中查询语句命中的数据
        :param fd_code: fd的唯一code
        :param query_str: 查询语句
        :return:
        """
        check_instance_avaliable()

        try:
            r = do_service(f"/remote/fd-service/{fd_code}", method="delete",params={'query': query}, return_type="None")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 500:
                # 说明服务器端报错了
                raise ServiceInnerException(e.response._content.decode('utf-8'))
            elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
                # 说明是认证相关的错误
                raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
            raise e

    def get_fact_datasource_fields(self, fd_code: str):
        """
        获取fd的字段
        :param fd_code:
        :return: List<FactDatasourceField>
        """
        fd_context = self._get_fd_context(fd_code)
        self._inner_check_permission(fd_context, 'execute')
        return fd_context.get_fact_datasource_fields()

    def exists_fds(self, fds):
        """
        判断fd是否存在
        :param fds:
        :return:
        """
        if fds is None:
            return False

        if not isinstance(fds, list):
            raise IllegalArgumentException("检测fd是否存在失败,输入参数不是一个list")

        check_instance_avaliable()

        try:
            r = do_service(f"/remote/fd-service/exists", method="post", data=fds)
            if r is not None:
                return r
            else:
                return False
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 500:
                # 说明服务器端报错了
                raise ServiceInnerException(e.response._content.decode('utf-8'))
            elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
                # 说明是认证相关的错误
                raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
            raise e



@Value("${sobeycube.factdatasource.distributed-mode:False}")
def distributed_mode():
    pass


class FactDatasourceProxyFactory(Singleton):

    __instance = None

    def get_fd_client_proxy(self, mode: bool = None) -> FactDatasourceProxy:
        if self.__instance:
            return self.__instance

        if mode is None:
            mode = distributed_mode()

        if mode:
            # 注册本地数据源
            register_jdbc_default_datasource()
            # 注册kafka默认的数据源
            register_kafka_default_datasource()
            # 启动FD改变事件消息监听
            FactDatasourceChangeListener.instance().start()
            # 获取本地操作实例
            self.__instance = DistributedFactDatasourceProxy.instance()
        else:
            self.__instance = CentralizedFactDatasourceProxy.instance()
        return self.__instance


def fd_client_proxy() -> FactDatasourceProxy:
    return FactDatasourceProxyFactory.instance().get_fd_client_proxy()
