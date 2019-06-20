# coding=utf-8
from __future__ import absolute_import, print_function

import itertools

from suanpan.arguments import Int, String
from suanpan.dw.hive import HiveDataWarehouse
from suanpan.dw.mysql import MysqlDataWarehouse
from suanpan.dw.odps import OdpsDataWarehouse
from suanpan.dw.postgres import PostgresDataWarehouse
from suanpan.proxy import Proxy


class DataWarehouseProxy(Proxy):
    MAPPING = {
        "hive": HiveDataWarehouse,
        "odps": OdpsDataWarehouse,
        "postgres": PostgresDataWarehouse,
        "mysql": MysqlDataWarehouse,
    }
    DEFAULT_ARGUMENTS = [String("dw-type")]
    HIVE_ARGUMENTS = [
        String("dw-hive-host", default="localhost"),
        Int("dw-hive-port", default=10000),
        String("dw-hive-database", default="default"),
        String("dw-hive-username"),
        String("dw-hive-password"),
        String("dw-hive-auth"),
    ]

    ODPS_ARGUMENTS = [
        String("dw-odps-access-id"),
        String("dw-odps-access-key"),
        String(
            "dw-odps-endpoint", default="http://service.cn.maxcompute.aliyun.com/api"
        ),
        String("dw-odps-project"),
    ]

    POSTGRES_ARGUMENTS = [
        String("dw-postgres-host", default="localhost"),
        Int("dw-postgres-port", default=5432),
        String("dw-postgres-database"),
        String("dw-postgres-username"),
        String("dw-postgres-password"),
    ]

    MYSQL_ARGUMENTS = [
        String("dw-mysql-host", default="localhost"),
        Int("dw-mysql-port", default=3306),
        String("dw-mysql-database"),
        String("dw-mysql-username"),
        String("dw-mysql-password"),
    ]

    ARGUMENTS = list(
        itertools.chain(
            DEFAULT_ARGUMENTS,
            HIVE_ARGUMENTS,
            ODPS_ARGUMENTS,
            POSTGRES_ARGUMENTS,
            MYSQL_ARGUMENTS,
        )
    )


dw = DataWarehouseProxy()
