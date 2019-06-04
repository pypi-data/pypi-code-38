# coding=utf-8
from __future__ import absolute_import, print_function

import itertools

from suanpan.arguments import Int, String
from suanpan.dw.hive import HiveDataWarehouse
from suanpan.dw.odps import OdpsDataWarehouse
from suanpan.proxy import Proxy


class DataWarehouseProxy(Proxy):
    MAPPING = {"hive": HiveDataWarehouse, "odps": OdpsDataWarehouse}
    DEFAULT_ARGUMENTS = [String("dw-type")]
    HIVE_ARGUMENTS = [
        String("dw-hive-host", default="localhost"),
        Int("dw-hive-port"),
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
    ARGUMENTS = list(itertools.chain(DEFAULT_ARGUMENTS, HIVE_ARGUMENTS, ODPS_ARGUMENTS))


dw = DataWarehouseProxy()
