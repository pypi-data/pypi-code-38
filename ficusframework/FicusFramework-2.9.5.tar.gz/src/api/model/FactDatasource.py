#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/21
from enum import Enum

from api.model.MetaModel import MetaModel


class FactDatasource(object):
    """
    事实库的定义
    """

    def __init__(self, site, projectCode, code, name, type, connection, target,
                 id=None, description=None, credentials=None, model=None, ttl=None, tags=None,
                 privilege=None,
                 **kwargs):
        """
        描述数据源的对象
        :param site: 事实库所属的站点,必填
        :param projectCode: 事实库所属的工程,必填
        :param code: 事实库的唯一标示,必填,要求全局code唯一,允许大小写字母加数字下划线,最大128个字符
        :param name: 事实库显示名字,必填,允许中文/英文大小写字母加数字,最大256个字符
        :param type: 事实库的类型,必填 allowableValues = "FILE,JDBC,REDIS,KAFKA,MONGO,ES,SOBEY_HIVE,GRAPH,CUSTOM,AMQP"
        :param connection: 事实库的连接字符串,必填  FILE就是文件路径 JDBC/GRAPH就是jdbcUrl等等,KAFKA/AMQP/REDIS/MONGO/ES就是服务器的IP加端口 ,
            sobeyHive 就是hivecore的地址 带端口号  CUSTOM 是 微服务的名字也就是actor.name
            REIDS:单机：ip:port  集群（英文逗号分割）： ip:port,ip:port,ip:port  哨兵（第一个表示主节点名字，英文分号分割）：MASTERNAME;哨兵IP1:PORT1;哨兵IP2:PORT2;哨兵IP3:PORT3
        :param target: 事实库的数据目标,必填,FILE文件名/MYSQL,ORACLE表名/redis(key的前缀)?/kafka队列名/es索引名/mongo Collection名/
            sobeyHive 就是目标索引名 entity/ CUSTOM是 handler的名字/AMQP exchange:routingKey/ JMS 发送消息的目标位置 https://stomp.github.io/stomp-specification-1.2.html#SEND
        :param id: 事实库在数据库中的主键,添加的时候不填
        :param description: 事实库描述/备注,允许中文/英文大小写字母加数字,最大512个字符
        :param credentials: 数据的认证的字符串,JDBC/REDIS/ES/KAFKA/AMQP 就是 用户名:密码   MONGO就是 username:password@database  sobeyHive就是 站点名  CUSTOM 没意义
        :param model: 事实库关联的模型 可选
        :param ttl: 数据过期时间
        :param tags: FD的标签,用于给fd分类,可选的.其值允许英文大小写加字母下划线
        :param privilege: 权限
        """
        self.id = id
        self.site = site
        self.projectCode = projectCode
        self.code = code
        self.name = name
        self.description = description
        self.type: FactDatasourceTypeEnum = FactDatasourceTypeEnum(type)
        self.connection = connection
        self.credentials = credentials
        self.target = target
        self.model: MetaModel = MetaModel(id=model) if model is not None else None
        self.ttl = ttl
        self.tags = tags
        self.privilege = privilege
        self.other_param = kwargs

        self._source_name = f'fd_{self.site}_{self.projectCode}_{self.code}'

    def get_source_name(self):
        return self._source_name


class FactDatasourceTypeEnum(Enum):
    FILE = 'FILE'
    JDBC = 'JDBC'
    REDIS = 'REDIS'
    KAFKA = 'KAFKA'
    MONGO = 'MONGO'
    ES = 'ES'
    SOBEY_HIVE = 'SOBEY_HIVE'
    GRAPH = 'GRAPH'
    CUSTOM = 'CUSTOM'
    AMQP = 'AMQP'
    # python中JMS类型使用的是stomp协议，如果配置的JMS类型，需要开启对应消息组件的stomp支持
    JMS = 'JMS'


class JdbcTypeEnum(Enum):
    MYSQL = 'MYSQL'
    ORACLE = 'ORACLE'
    VERNOX = 'VERNOX'
    SQL_SERVER = 'SQL_SERVER'
    POSTGRESQL = 'POSTGRESQL'
    DB2 = 'DB2'
    JTDS = 'JTDS'
    MOCK = 'MOCK'
    HSQL = 'HSQL'
    SYBASE = 'SYBASE'
    ALI_ORACLE = 'ALI_ORACLE'
    MARIADB = 'MARIADB'
    DERBY = 'DERBY'
    HBASE = 'HBASE'
    HIVE = 'HIVE'
    H2 = 'H2'
    DM = 'DM'
    KINGBASE = 'KINGBASE'
    # 阿里云odps
    ODPS = 'ODPS'
    # Log4JDBC
    LOG4JDBC = 'LOG4JDBC'


class JdbcDriverEnum(Enum):
    MYSQL_DRIVER = 'mysql+mysqldb'
    ORACLE_DRIVER = 'oracle+cx_oracle'
    SQL_SERVER_DRIVER = 'mssql+pyodbc'
    POSTGRESQL_DRIVER = 'postgresql+psycopg2'
    VERNOX_DRIVER = 'mysql+mysqldb'
