# coding=utf-8
from __future__ import unicode_literals, print_function, absolute_import

import pandas as pd

from nf.csdk.c_sdk import py_nfi_get_trades
from datetime import date, datetime
from nf.constant import CSDK_OPERATE_SUCCESS
from nf.pb.data.api.data_pb2 import Trades
from nf.pb_to_dict import protobuf_to_dict, dict_to_protobuf

from nf import utils
from nf.constant import DATA_TYPE_TICK

from nf.utils import load_to_datetime_str, protomessage2dict


pd.set_option('precision', 4)


def get_trades(symbol, end_time=None, count=50, df=False):
    if not symbol or len(symbol) <= 0:
        return []

    if count > 1000:
        count = 1000

    if not end_time:
        end_time = datetime.now()

    if isinstance(end_time, (date, datetime)):
        end_time = load_to_datetime_str(end_time)

    status, result = py_nfi_get_trades(symbol, end_time, count)

    if not status == CSDK_OPERATE_SUCCESS:
        print('unable to get trade data. error code: ', status)
        return []

    trades = Trades()
    trades.ParseFromString(result)

    tlist = [protobuf_to_dict(trade) for trade in trades.data]

    trade_list = []

    for trade in tlist:
        nt = {}

        nt['symbol'] = symbol
        nt['amount'] = trade['volume']
        nt['price'] = trade['price']
        nt['side'] = trade['side']
        nt['time'] = trade['created_at']

        trade_list.append(nt)
    if not df:
        return trade_list
    else:
        data = pd.DataFrame(trade_list)

        return data
