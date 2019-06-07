    # coding=utf-8
# Stubs for six (Python 3.5)
from __future__ import print_function, absolute_import, unicode_literals

import sys
import os
import base64
import json
from importlib import import_module
from optparse import OptionParser
import datetime
import six
import time

from nf.__version__ import __version__
from nf.callback import callback_controller
from nf.constant import (CSDK_OPERATE_SUCCESS, DATA_TYPE_TICK,
                         SUB_TAG, SCHEDULE_INFO, CALLBACK_TYPE_ERROR,
                         ERR_PARSE_MASSAGE, ERR_INVALID_PARAMETER)

from nf.csdk.c_sdk import (py_nfi_current, py_nfi_schedule,
                           py_nfi_set_data_callback, py_nfi_set_strategy_id, nfi_set_mode,
                           py_nfi_subscribe, py_nfi_subscribe_tx, py_nfi_set_token, py_nfi_current_bar,
                           py_nfi_unsubscribe, py_nfi_set_backtest_config_by_pb, py_nfi_get_inst_trade,py_nfi_get_inst_depth,
                           py_nfi_log, py_nfi_strerror, py_nfi_run, py_nfi_set_timer,
                           py_nfi_set_serv_addr, nfi_live_init, nfi_poll, nfi_now, py_nfi_get_on_error,
                           py_nfi_set_bar_timeout, py_nfi_get_future_symbol)


from nf.enum import MODE_UNKNOWN, ADJUST_NONE, MODE_BACKTEST, MODE_LIVE
from nf.model.storage import context
from nf.model.sub import SubDetail
from nf.pb.core.api.common_pb2 import Logs
from nf.pb.data.api.data_pb2 import Ticks, Bars, Trades, DethpRateLists
from nf.pb.core.api.account_pb2 import BacktestMode_Stream, BacktestReq, Position, Commission, Asset
from nf.pb.trade.api.trade.service_pb2 import GetTargetSymbolForBTResp
import pandas as pd
from nf.pb_to_dict import protobuf_to_dict
from nf.utils import load_to_list, load_to_second, timestamp2datetime, dict_fields_filter, takePriceFromDepth, load_to_datetime_str

running = True


def _unsubscribe_bar(symbol, frequency):

    [context.inside_remove_bar_sub(sub) for sub in context.inside_bar_subs
     if SUB_TAG.format(symbol, frequency) == sub.sub_tag]


def _unsubscribe_all():
    context.inside_unsubscribe_all()


def set_token(token):
    """
    设置用户的token，用于身份认证
    """
    if not token:
        raise TypeError('set_token() : argument missing or incorrect argument type.')
    py_nfi_set_token(token)
    context.token = str('bearer {}'.format(token))


def get_version():
    return __version__


def subscribe(symbols, frequency='1d', count=1, wait_group=False, wait_group_timeout='26s', unsubscribe_previous=False):
    """
    订阅行情，可以指定symbol， 数据滑窗大小，以及是否需要等待全部代码的数据到齐再触发事件。
    wait_group: 是否等待全部相同频度订阅的symbol到齐再触发on_bar事件。
    """
    frequency = _check_frequency(frequency)

    if not frequency:
        _error_call_back(ERR_INVALID_PARAMETER)
        return
    if not symbols:
        _error_call_back(ERR_INVALID_PARAMETER)
        return

    symbols = load_to_list(symbols)
    symbols_str = ','.join(symbols)

    status = py_nfi_subscribe(symbols_str, frequency, unsubscribe_previous)
    if not status == CSDK_OPERATE_SUCCESS:
        _error_call_back_by_check(status)
        print(status)
        return
    '''
    symbols=[]
    for symbol_in in symbols_str.split(","):
        symbol_list=get_histury_future_symbol(symbol_in)
        if (symbol_list == None):
            continue
        symbols=symbols+symbol_list
    '''
    if unsubscribe_previous:
        _unsubscribe_all()

    # 设置超时触发时间，期货要设置超时时间长点，因为bitmex 16秒才显示上一分钟的bar
    tm = 26
    if wait_group_timeout.endswith('s'):
        tm = int(wait_group_timeout[0:-1])

    py_nfi_set_bar_timeout(tm - 6)  # bar超时时间比wait_group默认短6秒

    if frequency == DATA_TYPE_TICK:
        [context.inside_append_tick_sub(
        SubDetail(symbol, frequency, count, False, wait_group_timeout,
                  unsubscribe_previous)) for symbol in symbols]

        return

    # bar缓存初始化
    wait_group_timeout = load_to_second(wait_group_timeout)
    # count 必须大于2, 不然没法进行wait_group, 被冲掉了
    if count < 2:
        count = 2

    [context.inside_append_bar_sub(
        SubDetail(symbol, frequency, count, wait_group, wait_group_timeout,
                  unsubscribe_previous)) for symbol in symbols]


def subscribe_tx(symbols, frequency, count=1, unsubscribe_previous=False):
    status = py_nfi_subscribe_tx(symbols, frequency, unsubscribe_previous, count)
    if not status == CSDK_OPERATE_SUCCESS:
        _error_call_back(status)
        print(status)
        return


def get_inst_trade(symbol, count=1, df=False):

    status, result = py_nfi_get_inst_trade(symbol, count)
    if not status == CSDK_OPERATE_SUCCESS:
        _error_call_back(status)
        print(status)
        return
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


def get_inst_depth(symbol, points=50):
    if not symbol or len(symbol) <= 0:
        return {}

    if points > 50:
        points = 50
    status, result =py_nfi_get_inst_depth(symbol, 1)
    if not status == CSDK_OPERATE_SUCCESS:
        _error_call_back(status)
        print(status)
        return {}
    if len(result) <= 0:
        return {}

    depth = DethpRateLists()
    depth.ParseFromString(result)
    depth = protobuf_to_dict(depth)
    bids = depth.data[0].bids
    asks = depth.data[0].asks
    created_at = depth.data[0].created_at
    if points < len(bids):
        bids = bids[0: points]
        asks = asks[0: points]

    bids = [dict_fields_filter(bid, ['price', 'volume']) for bid in bids]
    asks = [dict_fields_filter(ask, ['price', 'volume']) for ask in asks]

    bids.sort(key=takePriceFromDepth, reverse=True)  # 买盘，降序
    asks.sort(key=takePriceFromDepth, reverse=False)  # 卖盘，升序

    acc_vol = 0
    for dpt in asks:
        acc_vol += dpt['volume']
        dpt['accumulate'] = acc_vol

    acc_vol = 0
    for dpt in bids:
        acc_vol += dpt['volume']
        dpt['accumulate'] = acc_vol

    depth = {'points': len(bids),'created_at':timestamp2datetime(created_at), 'bids': bids, 'asks': asks}

    return depth


def unsubscribe_tx(symbols, frequency):
    symbols = load_to_list(symbols)
    symbols_str = ','.join(symbols)
    if frequency != "trade" and frequency != "depth":
        _error_call_back_by_check(ERR_INVALID_PARAMETER)
        return
    status = py_nfi_unsubscribe(symbols_str, frequency)
    if not status == CSDK_OPERATE_SUCCESS:
        _error_call_back_by_check(status)
        return

    if symbols_str == '*':
        return _unsubscribe_all()

    if frequency == DATA_TYPE_TICK:
        for symbol in symbols:
            [context.inside_remove_tick_sub(sub) for sub in context.inside_tick_subs
             if SUB_TAG.format(symbol, frequency) == sub.sub_tag]

        return

    [_unsubscribe_bar(symbol, frequency) for symbol in symbols]


def unsubscribe(symbols, frequency='1d'):
    """
    unsubscribe - 取消行情订阅

    取消行情订阅，默认取消所有已订阅行情
    """
    symbols = load_to_list(symbols)
    symbols_str = ','.join(symbols)
    frequency = _check_frequency(frequency)
    if not frequency:
        _error_call_back_by_check(ERR_INVALID_PARAMETER)
        return

    status = py_nfi_unsubscribe(symbols_str, frequency)
    if not status == CSDK_OPERATE_SUCCESS:
        _error_call_back(status)
        return

    if symbols_str == '*':
        return _unsubscribe_all()

    if frequency == DATA_TYPE_TICK:
        for symbol in symbols:
            [context.inside_remove_tick_sub(sub) for sub in context.inside_tick_subs
            if SUB_TAG.format(symbol, frequency) == sub.sub_tag]

        return

    [_unsubscribe_bar(symbol, frequency) for symbol in symbols]


def current_bar(symbol, frequency):
    if not symbol:
        raise TypeError('current_bar() : argument missing or incorrect argument type.')
    if not frequency:
        raise TypeError('current_bar() : argument missing or incorrect argument type.')
    frequency = _check_frequency(frequency)
    if not frequency:
        _error_call_back_by_check(ERR_INVALID_PARAMETER)
        return []
    bars = Bars()
    status, data = py_nfi_current_bar(symbol, frequency)
    if not status == CSDK_OPERATE_SUCCESS:
        _error_call_back(status)
        return []

    bars.ParseFromString(data)
    bars = [protobuf_to_dict(bar) for bar in bars.data]
    bars = [_reform_tick_data(bar) for bar in bars]
    return bars


def current(symbols, fields=''):
    """
    查询当前行情快照，返回tick数据
    """
    if not symbols:
        raise TypeError('current() : argument missing or incorrect argument type.')

    symbols = load_to_list(symbols)
    fields = load_to_list(fields)

    symbols_str = ','.join(symbols)
    fields_str = ','.join(fields)

    ticks = Ticks()
    status, data = py_nfi_current(symbols_str, fields_str)
    if not status == CSDK_OPERATE_SUCCESS:
        _error_call_back(status)
        return []

    ticks.ParseFromString(data)
    ticks = [protobuf_to_dict(tick) for tick in ticks.data]
    ticks = [_reform_tick_data(tick) for tick in ticks]

    if not fields_str or fields_str == '':
        return ticks
    else:
        fields = load_to_list(fields)
        new_ticks = []
        for tick in ticks:
            new_tick = {key: value for key, value in tick.items() if key in fields}
            new_ticks.append(new_tick)
        return new_ticks


def get_strerror(error_code):
    if not error_code:
        raise TypeError('get_strerror() : argument missing or incorrect argument type.')
    return py_nfi_strerror(error_code)


def schedule(schedule_func, date_rule, time_rule):
    """
    定时任务
    """
    if not schedule_func or not date_rule or not time_rule:
        raise TypeError('schedule() : argument missing or incorrect argument type.')

    schemdule_info = SCHEDULE_INFO.format(date_rule=date_rule, time_rule=time_rule)
    context.inside_schedules[schemdule_info] = schedule_func
    py_nfi_schedule(date_rule, time_rule)


def run(strategy_id='',
        filename='',
        mode=MODE_UNKNOWN,
        token='',
        backtest_params='',
        backtest_adjust=ADJUST_NONE,
        backtest_check_cache=1,
        serv_addr='127.0.0.1:7001'
        ):
    """
    执行策略
    """

    parser = OptionParser()
    parser.add_option("--strategy_id", action="store",
                      dest="strategy_id",
                      default=strategy_id,
                      help="strategy id")

    parser.add_option("--filename", action="store",
                      dest="filename",
                      default=filename,
                      help="strategy file name")

    parser.add_option("--mode", action="store",
                      dest="mode",
                      default=mode,
                      help="strategy mode: MODE_LIVE/MODE_BACKTEST")

    parser.add_option("--token", action="store",
                      dest="token",
                      default=token,
                      help="user token")

    parser.add_option("--backtest_params", action="store",
                      dest="backtest_params",
                      default=backtest_params,
                      help="backtest parameters")

    parser.add_option("--backtest_adjust", action="store",
                      dest="backtest_adjust",
                      default=backtest_adjust,
                      help="backtest adjust mode")

    parser.add_option("--backtest_check_cache", action="store",
                      dest="backtest_check_cache",
                      default=backtest_check_cache,
                      help="backtest check cache")

    parser.add_option("--serv_addr", action="store",
                      dest="serv_addr",
                      default=serv_addr,
                      help="term-serve address")

    (options, args) = parser.parse_args()
    strategy_id = options.strategy_id
    filename = options.filename
    mode = int(options.mode)
    token = options.token

    backtest_params = options.backtest_params

    backtest_adjust = int(options.backtest_adjust)
    backtest_check_cache = int(options.backtest_check_cache)
    serv_addr = options.serv_addr

    from nf import api
    if filename.endswith(".py"):
        filename = filename[:-3]
    filename = filename.replace("/", ".")
    filename = filename.replace('\\', ".")
    fmodule = import_module(filename)

    for name in api.__all__:
        if name not in fmodule.__dict__:
            fmodule.__dict__[name] = getattr(api, name)

    # 服务地址设置
    if serv_addr:
        set_serv_addr(serv_addr)

    set_token(token)

    # 实时模式下 1000毫秒触发一次timer事件 用来处理wait_group的过期
    py_nfi_set_timer(1000)
    py_nfi_set_strategy_id(strategy_id)
    nfi_set_mode(mode)

    context.mode = mode
    context.strategy_id = strategy_id

    # 调用户文件的init
    context.inside_file_module = fmodule
    context.token = token
    context.adjust_mode = backtest_adjust
    py_nfi_set_data_callback(callback_controller)

    if mode == MODE_BACKTEST:
        if isinstance(backtest_params, bytes) and (not backtest_params or backtest_params.isspace()):
            print('missing backtest parameters or invalid parameters', end="", file=sys.stderr)
            return
        # base64.b64decode
        # 解码base64字符串，得到json对象，再转换为参数字典对象
        try:
            backtest_params = base64.b64decode(backtest_params)
            backtest_params = json.loads(backtest_params)

        except Exception as e:
            _error_call_back(ERR_PARSE_MASSAGE)
            return
        req = BacktestReq()
        try:
            req.start_time.seconds = backtest_params["startTime"]
            req.end_time.seconds = backtest_params["endTime"]
            req.transaction_ratio = backtest_params["transactionRatio"]
            req.slippage_ratio = backtest_params["slippageRatio"]

            context.backtest_start_time = backtest_params["startTime"]
            context.backtest_end_time = backtest_params["endTime"]

        except Exception as e:
            _error_call_back(ERR_PARSE_MASSAGE)
            return

        req.strategy_id = strategy_id
        req.mode = BacktestMode_Stream
        req.commission_ratio = 0.01

        if backtest_params["initialPosition"]:
            try:
                for inipos in backtest_params["initialPosition"]:
                    if('subject' in inipos.keys()):
                        if((1 == inipos['subject']) or ('SecurityType_Future' == inipos['subject'])):
                            asset = Asset()
                            asset.available_balance = inipos['volume']
                            asset.currency = inipos['currency']
                            asset.exchange = inipos["exchange"]
                            req.initial_assets.extend([asset])
                            cms = Commission()
                            cms.exchange = inipos["exchange"]
                            cms.quote = inipos["currency"]
                            cms.commission_ratio = inipos["commissionRatio"]
                            req.comission_infos.extend([cms])
                            continue
                    position = Position()
                    position.available = inipos['volume']
                    position.currency = '{}.{}'.format(inipos["exchange"], inipos['currency'])
                    req.initial_positions.extend([position])

                    cms = Commission()
                    cms.exchange = inipos["exchange"]
                    cms.quote = inipos["currency"]
                    cms.commission_ratio = inipos["commissionRatio"]
                    req.comission_infos.extend([cms])

            except Exception as e:
                print("Unexpected Error: {}".format(e))

        preq = req.SerializeToString()

        status = py_nfi_set_backtest_config_by_pb(preq)
        if not status == CSDK_OPERATE_SUCCESS:
            _error_call_back_by_check(status)
            return
    if mode == MODE_LIVE:
        status = nfi_live_init()
        if not status == CSDK_OPERATE_SUCCESS:
            _error_call_back_by_check(status)
            return

    fmodule.init()
    if mode == MODE_BACKTEST:

        status = py_nfi_run()
        if not status == CSDK_OPERATE_SUCCESS:
            _error_call_back_by_check(status)
        return status

    while running:
        nfi_poll()


def log(level, msg, source):
    logs = Logs()
    newlog = logs.data.add()
    newlog.owner_id = context.strategy_id
    newlog.source = source
    newlog.level = level
    newlog.msg = msg

    req = logs.SerializeToString()
    py_nfi_log(req)


def stop():
    global running
    running = False
    os._exit(2)


def set_serv_addr(addr):
    if not addr:
        addr = '127.0.0.1:7001'

    py_nfi_set_serv_addr(addr)


def now():
    # 返回一个时间字符串
    now_time = nfi_now()

    # now_time == 0 说明是回测模式而且处于init装填 c sdk拿不到时间
    if now_time == 0:
        if context.backtest_start_time and isinstance(context.backtest_start_time, six.string_types):
            dt = datetime.datetime.strptime(context.backtest_start_time, "%Y-%m-%d %H:%M:%S")
        else:
            dt = timestamp2datetime(context.backtest_start_time)

    else:
        dt = timestamp2datetime(now_time)

    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _error_call_back(code):
    ''' 错误回调处理 '''
    if code == CSDK_OPERATE_SUCCESS:
        return code

    err_info = py_nfi_get_on_error()
    if isinstance(err_info, bytes):
        err_info = bytes.decode(err_info)

    callback_controller(CALLBACK_TYPE_ERROR, err_info)


def _error_call_back_by_check(code):
    if code == CSDK_OPERATE_SUCCESS:
        return code
    err_info = py_nfi_strerror(code)
    if isinstance(err_info, bytes):
        err_info = bytes.decode(err_info)
    err_info = '{}|{}'.format(code, err_info)
    callback_controller(CALLBACK_TYPE_ERROR, err_info)


def _error_call_back_for_py(code, error_msg):

    callback_controller(CALLBACK_TYPE_ERROR, error_msg)


def _check_frequency(frequency):
    frequency = frequency.lower()
    if frequency == DATA_TYPE_TICK:
        return frequency
    elif frequency.endswith('s'):
        return frequency
    elif frequency.endswith('m'):
        return '{}s'.format(int(frequency[0:-1]) * 60)
    elif frequency.endswith('h'):
        return '{}s'.format(int(frequency[0:-1]) * 60 * 60)
    elif frequency.endswith('d'):
        return '{}s'.format(int(frequency[0:-1]) * 60 * 60 * 24)
    elif frequency.endswith('w'):
        return '{}s'.format(int(frequency[0:-1]) * 60 * 60 * 24 * 7)
    elif frequency.endswith('y'):
        return '{}s'.format(int(frequency[0:-1]) * 60 * 60 * 24 * 365)
    else:
        return None


def _reform_tick_data(tick):
    remove_keys = ['frist_trade_id', 'last_trade_id', 'sequence', 'side',
                   'last_volume', 'quote_volume', 'high', 'low', 'previous_close',
                   'current_close', 'close_trade_quantity', 'open', 'trade_amount',
                   'front', 'rare', 'front_rate', 'rare_rate', 'nanos', 'mark_price', 'openInterest']

    for remove_key in remove_keys:
        tick.pop(remove_key, '')

    return tick


def get_history_future_symbol(symbol):

    status, result = py_nfi_get_future_symbol(symbol)

    if not status == CSDK_OPERATE_SUCCESS:
        _error_call_back(status)
        return
    if result is None:
        return [symbol]
    res = GetTargetSymbolForBTResp()
    res.ParseFromString(result)

    rs = protobuf_to_dict(res)
    symbol_infos = rs['symbolinfos']
    symbols = []

    for SymbolInfo in symbol_infos:
        symbols.append(SymbolInfo['symbole'])
    print("get_history_future_symbol", symbols)
    if(symbols == []):
        symbols.append(symbol)
    return symbols
