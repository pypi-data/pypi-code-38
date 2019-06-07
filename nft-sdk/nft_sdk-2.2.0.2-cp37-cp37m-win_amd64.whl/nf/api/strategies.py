# coding=utf-8
# Stubs for six (Python 3.5)
from __future__ import print_function, absolute_import, unicode_literals

from nf.csdk.c_sdk import py_nfi_strategy_duidao, py_nfi_strategy_budan, py_nfi_update_strategy_datas, \
    py_nfi_add_strategy_rds, py_nfi_strategy_kongpan
from nf.pb.strategy.strategy_params.strategy.params_pb2 import StrategyDuidaoParams, StrategyBudanParams, \
    StrategyLapanParams
from nf.pb.trade.api.trade.service_pb2 import UpdateStrategyDatasReq, AddStrategyRdsReq


def run_strategy_duidao(**kwargs):
    params = StrategyDuidaoParams()
    for key in kwargs:
        if hasattr(params, key):
            setattr(params, key, kwargs[key])

    req = params.SerializeToString()

    return py_nfi_strategy_duidao(req)


def run_strategy_budan(**kwargs):
    params = StrategyBudanParams()
    for key in kwargs:
        if hasattr(params, key):
            setattr(params, key, kwargs[key])

    req = params.SerializeToString()

    return py_nfi_strategy_budan(req)


def update_strategy_datas(vol_sum=0.0, runtime_sum=0):
    if isinstance(vol_sum, float):
        vol_sum = '%.2f' % vol_sum

    if not isinstance(vol_sum, str):
        vol_sum = str(vol_sum)

    if not isinstance(runtime_sum, str):
        runtime_sum = str(runtime_sum)

    req = UpdateStrategyDatasReq()
    req.vol_sum = vol_sum
    req.runtime_sum = runtime_sum

    sreq = req.SerializeToString()

    return py_nfi_update_strategy_datas(sreq)


def add_strategy_rds(type_name, rds_value=0.0, rds_info=''):

    if type_name is None or not isinstance(type_name, str):
        raise TypeError('add_strategy_rds() : argument missing or incorrect argument type.')

    if not isinstance(rds_value, float) and not isinstance(rds_value, int):
        raise TypeError('add_strategy_rds() : argument missing or incorrect argument type.')
        return

    if not isinstance(rds_info, str):
        raise TypeError('add_strategy_rds() : argument missing or incorrect argument type.')

    req = AddStrategyRdsReq()
    req.type_name = type_name
    req.rds_value = rds_value
    req.rds_info = rds_info

    sreq = req.SerializeToString()

    return py_nfi_add_strategy_rds(sreq)


def run_strategy_kongpan(**kwargs):
    params = StrategyLapanParams()
    for key in kwargs:
        if hasattr(params, key):
            setattr(params, key, kwargs[key])

    req = params.SerializeToString()

    return py_nfi_strategy_kongpan(req)
