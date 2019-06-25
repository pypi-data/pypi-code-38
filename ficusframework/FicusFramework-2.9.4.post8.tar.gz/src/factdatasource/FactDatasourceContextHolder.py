#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/21
from api.model.FactDatasource import FactDatasource, FactDatasourceTypeEnum, JdbcTypeEnum
from factdatasource.FactDatasourceContext import FactDatasourceContext
from factdatasource.dao.FactDatasource import customer_dao_context_holder
from factdatasource.dao.MultipleDatasourceHolder import get_multiple_datesource
from factdatasource.execptions import NotSupportedFDException, FDNotExistsException, FDOperationException

from libs.utils import get_jdbc_type, Singleton
from service.FactDatasourceService import FactDatasourceService


class FactDatasourceContextHolder(Singleton):

    # fd_code ---> FactDatasourceContext
    __fact_datasource_context_cache = dict()

    # fd_code ---> FactDatasource
    __fact_datasource_cache = dict()

    @property
    def _fd_service(self):
        return FactDatasourceService.instance()

    def get_fact_datasource(self, fd_code: str) -> FactDatasourceContext:
        """
        获取一个fd_context的实现
        这里逻辑应该是这样，先通过rest接口取到fd的定义信息，然后根据这个定义信息构造fd_context
        :param fd_code:
        :return:
        """
        if fd_code in self.__fact_datasource_context_cache.keys():
            return self.__fact_datasource_context_cache.get(fd_code)

        if fd_code not in self.__fact_datasource_cache.keys():
            fact_datasource: FactDatasource = self._fd_service.get_fd_by_code(fd_code)
            if not fact_datasource:
                raise FDNotExistsException(f'数据源{fd_code}不存在')
        else:
            fact_datasource = self.__fact_datasource_cache.get(fd_code)

        if self.add_fact_datasource(fact_datasource):
            return self.__fact_datasource_context_cache.get(fd_code)

    def remove_fact_datasource(self, fact_datasource: FactDatasource):
        """
        删除一个fd实现
        这里只有消息监听处会调用，其他地方暂时没有调用这里的
        :param fact_datasource:
        :return:
        """
        fd_code = fact_datasource.code
        if self.is_using_fact_datasource(fd_code):
            raise FDOperationException(f'数据源{fd_code}正在使用，无法删除。')

        if fd_code in self.__fact_datasource_context_cache.keys():
            del self.__fact_datasource_context_cache[fd_code]
        if fd_code in self.__fact_datasource_cache.keys():
            del self.__fact_datasource_cache[fd_code]

        # 删除数据源中的配置
        if self._need_datasource(fact_datasource.type):
            get_multiple_datesource(fact_datasource.type).delete_datasource_type(fact_datasource.get_source_name())
        return True

    def add_fact_datasource(self, fact_datasource: FactDatasource):
        """
        增加一个fd实现
        :param fact_datasource:
        :return:
        """
        if fact_datasource is None or fact_datasource.code is None:
            return False

        fd_code = fact_datasource.code
        # 放到缓存中
        if fd_code not in self.__fact_datasource_cache.keys():
            self.__fact_datasource_cache[fd_code] = fact_datasource

        fact_datasource_context = self.__get_fact_datasource_context(fact_datasource)
        if fact_datasource_context:
            self.__fact_datasource_context_cache[fd_code] = fact_datasource_context
            # 添加到数据源中
            if self._need_datasource(fact_datasource.type):
                get_multiple_datesource(fact_datasource.type).add_datasource_type(fact_datasource.get_source_name(),
                                                                                  fact_datasource.connection,
                                                                                  fact_datasource.credentials)
            return True
        return False

    def update_fact_datasource(self, fact_datasource: FactDatasource):
        """
        FD修改
        :param fact_datasource:
        :return:
        """
        fd_code = fact_datasource.code
        if self.is_using_fact_datasource(fd_code):
            raise FDOperationException(f'数据源{fd_code}正在使用，无法修改。')
        self.remove_fact_datasource(fact_datasource)
        self.add_fact_datasource(fact_datasource)

    def is_loaded_fact_datasource(self, fd_code: str) -> bool:
        """
        判断fd_code是否已经加载
        :param fd_code:
        :return:
        """
        return fd_code in self.__fact_datasource_cache.keys()

    def is_using_fact_datasource(self, fd_code: str) -> bool:
        """
        判断fd_code是否正在使用，正在使用表示正在读写数据或者查询数据
        :param fd_code:
        :return:
        """
        # 没在内存中肯定就没有被使用
        if not self.is_loaded_fact_datasource(fd_code):
            return False

        fd: FactDatasource = self.__fact_datasource_cache.get(fd_code)
        return customer_dao_context_holder.is_using(fd.get_source_name())

    def _need_datasource(self, fd_type: FactDatasourceTypeEnum):
        """
        判断某一个fd是否需要使用数据源，比如sobeyhvie这种直接调用rest接口的，就不需要使用数据源
        默认都应该使用的
        :param fd_type:
        :return:
        """
        if not fd_type:
            True
        if fd_type == FactDatasourceTypeEnum.SOBEY_HIVE:
            return False
        return True

    def __get_fact_datasource_context(self, fact_datasource: FactDatasource) -> FactDatasourceContext:
        fd_type = fact_datasource.type
        fd_context = None

        if fd_type == FactDatasourceTypeEnum.JDBC:
            # 根据url区分需要选择的方言类型
            connection = fact_datasource.connection
            jdbc_type = get_jdbc_type(connection)
            if not jdbc_type:
                raise NotSupportedFDException(f'不支持该连接{connection}')

            if jdbc_type == JdbcTypeEnum.MYSQL:
                from factdatasource.persistence.jdbc.dialect.MysqlJdbcFactDatasourceContext import \
                    MysqlJdbcFactDatasourceContext
                fd_context = MysqlJdbcFactDatasourceContext(fact_datasource)
            elif jdbc_type == JdbcTypeEnum.DB2:
                from factdatasource.persistence.jdbc.dialect.Db2JdbcFactDatasourceContext import \
                    Db2JdbcFactDatasourceContext
                fd_context = Db2JdbcFactDatasourceContext(fact_datasource)
            elif jdbc_type == JdbcTypeEnum.ORACLE:
                from factdatasource.persistence.jdbc.dialect.OracleJdbcFactDatasourceContext import \
                    OracleJdbcFactDatasourceContext
                fd_context = OracleJdbcFactDatasourceContext(fact_datasource)
            elif jdbc_type == JdbcTypeEnum.POSTGRESQL:
                from factdatasource.persistence.jdbc.dialect.PostgresqlJdbcFactDatasourceContext import \
                    PostgresqlJdbcFactDatasourceContext
                fd_context = PostgresqlJdbcFactDatasourceContext(fact_datasource)
            elif jdbc_type == JdbcTypeEnum.SQL_SERVER:
                from factdatasource.persistence.jdbc.dialect.SqlserverJdbcFactDatasourceContext import \
                    SqlserverJdbcFactDatasourceContext
                fd_context = SqlserverJdbcFactDatasourceContext(fact_datasource)
            elif jdbc_type == JdbcTypeEnum.VERNOX:
                from factdatasource.persistence.jdbc.dialect.VernoxJdbcFactDatasourceContext import \
                    VernoxJdbcFactDatasourceContext
                fd_context = VernoxJdbcFactDatasourceContext(fact_datasource)
            else:
                raise NotSupportedFDException(f'暂不支持该数据库{jdbc_type}')
        elif fd_type == FactDatasourceTypeEnum.AMQP:
            from factdatasource.persistence.amqp.AmqpFactDatasourceContext import AmqpFactDatasourceContext
            fd_context = AmqpFactDatasourceContext(fact_datasource)
        elif fd_type == FactDatasourceTypeEnum.CUSTOM:
            from factdatasource.persistence.custom.CustomFactDatasourceContext import CustomFactDatasourceContext
            fd_context = CustomFactDatasourceContext(fact_datasource)
        elif fd_type == FactDatasourceTypeEnum.ES:
            from factdatasource.persistence.es.EsFactDatasourceContext import EsFactDatasourceContext
            fd_context = EsFactDatasourceContext(fact_datasource)
        elif fd_type == FactDatasourceTypeEnum.FILE:
            from factdatasource.persistence.file.FileFactDatasourceContext import FileFactDatasourceContext
            fd_context = FileFactDatasourceContext(fact_datasource)
        elif fd_type == FactDatasourceTypeEnum.GRAPH:
            from factdatasource.persistence.graphdb.GraphdbFactDatasourceContext import GraphdbFactDatasourceContext
            fd_context = GraphdbFactDatasourceContext(fact_datasource)
        elif fd_type == FactDatasourceTypeEnum.JMS:
            from factdatasource.persistence.stomp.StompFactDatasourceContext import StompFactDatasourceContext
            fd_context = StompFactDatasourceContext(fact_datasource)
        elif fd_type == FactDatasourceTypeEnum.KAFKA:
            from factdatasource.persistence.kafka.KafkaFactDatasourceContext import KafkaFactDatasourceContext
            fd_context = KafkaFactDatasourceContext(fact_datasource)
        elif fd_type == FactDatasourceTypeEnum.MONGO:
            from factdatasource.persistence.mongo.MongoFactDatasourceContext import MongoFactDatasourceContext
            fd_context = MongoFactDatasourceContext(fact_datasource)
        elif fd_type == FactDatasourceTypeEnum.REDIS:
            from factdatasource.persistence.redis.RedisFactDatasourceContext import RedisFactDatasourceContext
            fd_context = RedisFactDatasourceContext(fact_datasource)
        elif fd_type == FactDatasourceTypeEnum.SOBEY_HIVE:
            from factdatasource.persistence.sobeyhive.SobeyHiveFactDatasourceContext import SobeyHiveFactDatasourceContext
            fd_context = SobeyHiveFactDatasourceContext(fact_datasource)
        else:
            raise NotSupportedFDException(f'暂不支持该FD类型{fd_type}')

        return fd_context

