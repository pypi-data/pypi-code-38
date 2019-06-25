#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/22
from api.model.FactDatasource import FactDatasourceTypeEnum
from factdatasource.execptions import NotSupportedFDException


def get_multiple_datesource(fd_type: FactDatasourceTypeEnum):
    if fd_type == FactDatasourceTypeEnum.JDBC:
        from factdatasource.dao.jdbc.MultipleJdbcDatasource import MultipleJdbcDatasource
        return MultipleJdbcDatasource.instance()
    elif fd_type == FactDatasourceTypeEnum.ES:
        from factdatasource.dao.es.MultipleEsDatasource import MultipleEsDatasource
        return MultipleEsDatasource.instance()
    elif fd_type == FactDatasourceTypeEnum.MONGO:
        from factdatasource.dao.mongo.MultipleMongoDatasource import MultipleMongoDatasource
        return MultipleMongoDatasource.instance()
    elif fd_type == FactDatasourceTypeEnum.REDIS:
        from factdatasource.dao.redis.MultipleRedisDatasource import MultipleRedisDatasource
        return MultipleRedisDatasource.instance()
    elif fd_type == FactDatasourceTypeEnum.KAFKA:
        from factdatasource.dao.kafka.MultipleKafkaDatasource import MultipleKafkaDatasource
        return MultipleKafkaDatasource.instance()
    elif fd_type == FactDatasourceTypeEnum.GRAPH:
        from factdatasource.dao.jdbc.MultipleJdbcDatasource import MultipleJdbcDatasource
        return MultipleJdbcDatasource.instance()
    elif fd_type == FactDatasourceTypeEnum.AMQP:
        from factdatasource.dao.amqp.MultipleAmqpDatasource import MultipleAmqpDatasource
        return MultipleAmqpDatasource.instance()
    elif fd_type == FactDatasourceTypeEnum.JMS:
        from factdatasource.dao.stomp.MultipleStompDatasource import MultipleStompDatasource
        return MultipleStompDatasource.instance()
    else:
        raise NotSupportedFDException(f'暂未支持{fd_type}类型的数据源')
