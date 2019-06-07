# coding=utf-8
from __future__ import unicode_literals, print_function, absolute_import

from nf.constant import CSDK_OPERATE_SUCCESS, ERR_INVALID_PARAMETER

from nf.api.basic import _error_call_back, _check_frequency, _reform_tick_data,_error_call_back_by_check

from nf.csdk.c_sdk import (py_nfi_place_order, py_nfi_get_unfinished_orders,
                           py_nfi_get_orders, py_nfi_cancel_all_orders,
                           py_nfi_get_execution_reports_intraday, py_nfi_get_orders_intraday,
                           py_nfi_get_unfinished_orders_intraday,
                           py_nfi_cancel_order, py_nfi_get_orders_all,
                           py_nfi_get_execution_reports, py_nfi_get_positions,
                           py_nfi_get_instruments,
                           py_nfi_get_symbols_by_fc, py_nfi_get_symbols_by_front,
                           py_nfi_get_symbol_of_coins, py_nfi_get_symbol,
                           py_nfi_get_all_symbols_of_coin,
                           py_nfi_history_ticks, py_nfi_history_bars,
                           py_nfi_history_ticks_n, py_nfi_history_bars_n,
                           py_nfi_get_exchange_rate, py_nfi_get_market_depth,
                           nfi_now, py_nfi_vx_alert_msg,
                           py_nfi_alert_msg,
                           py_nfi_get_symbol_for_future, py_nfi_get_target_stats,
                           py_nfi_get_settlements, py_nfi_get_fundingRate,
                           py_nfi_get_margin_assets, py_nfi_set_margin_mode,
                           py_nfi_set_leverage, py_nfi_add_margin,
                           py_nfi_get_mark_price)

from nf.enum import OrderType_Limit, MODE_BACKTEST
from nf.model.storage import Context
from nf.pb.core.api.account_pb2 import (Order, Orders, ExecRpts, Positions, ExchangeRateList, SecurityType_Future,
                                        StatItems, SettlementItems, GetMarginAssetsResp, SecurityType_Physical)
from nf.pb.trade.api.trade.service_pb2 import (GetUnfinishedOrdersReq, GetIntradayExecrptsReq,GetIntradayOrdersReq,
                                               GetOrdersReq, GetExecrptsReq, PlaceOrderReq, GetPositionsReq,GetIntradayUnfinishedOrdersReq,
                                               SearchCoinPairsRsp, CancelOrderReq, AlertMeReq, WxAlertReq, TradingSymbolReq,
                                               SearchCoinPairsReq, TargetSymbolReq, StatsReq, GetSettlementReq,
                                               SymbolReq, FundingRateResp, GetMarginAssetsReq, SetModeReq, StatResp,
                                               SetLeverageReq, SetMarginReq, GetOrdersAllReq)

from nf.pb.data.api.data_pb2 import Ticks, Bars, DethpRateLists, MarkPrice


from nf.pb_to_dict import protobuf_to_dict, dict_to_protobuf
from nf.utils import load_to_list, dict_fields_filter, takePriceFromDepth, load_to_datetime_str, timestamp2datetime

from nf.pb.data.api.data_pb2 import InstrumentInfos
from nf.pb.core.api.common_pb2 import CommSymbolInfo
from nf.enum import *
import pandas as pd

from datetime import datetime
import time
context = Context()


def _place_order(**kwargs):
    order = Order()
    for key in kwargs:
        setattr(order, key, kwargs[key])
        if context.mode == MODE_BACKTEST:
            order.created_at.seconds = nfi_now()    # get timestamp from csdk

    place_order_req = PlaceOrderReq()

    place_order_req.orders.extend([order])
    req = place_order_req.SerializeToString()
    status, result = py_nfi_place_order(req)

    if not status == CSDK_OPERATE_SUCCESS:
        _error_call_back(status)
        return []

    if not result:
        return []

    res = Orders()
    res.ParseFromString(result)

    return [protobuf_to_dict(res_order, including_default_value_fields=True) for
            res_order in res.data]


def order_volume(symbol, volume, side, order_type, position_effect=0,
                 order_duration=0, order_qualifier=0,
                 account='', price=0):
    """
    按指定量委托
    """
    if not symbol or not volume or not side or not order_type or len(symbol) <= 0:
        raise TypeError('order_volume() : argument missing or incorrect argument type.')

    if order_type == OrderType_Limit and price <= 0:
        raise TypeError('order_volume() : argument error, whit price <= 0 for order type \'OrderType_Limit\'.')

    symbol_list = symbol.split(".")
    if len(symbol_list) > 1:
        if symbol_list[0] == "BITMEX" or symbol_list[0] == "OKEXFU":
            raise TypeError('Please use order_future to Placeorder!')

    account_id = ''
    account_name = ''

    order_src = 2  # sdk
    return _place_order(symbol=symbol, volume=volume, value=-1,  # when place an order by volume, 'value' should be set to a negtive number
                        side=side, account_id=account_id,
                        account_name=account_name, price=price,
                        order_type=order_type, order_src=order_src,
                        subject=SecurityType_Physical)


def order_value(symbol, value, side, order_type, position_effect=0,
                order_duration=0, order_qualifier=0,
                account='', price=0):
    """
    按指定价委托
    """
    if not symbol or not value or not side or not order_type or len(symbol) <= 0:
        raise TypeError('order_value() : argument missing or incorrect argument type.')

    if order_type == OrderType_Limit and price <= 0:
        raise TypeError('order_value() : argument error, whit price <= 0 for order type \'OrderType_Limit\'.')

    symbol_list = symbol.split(".")
    if len(symbol_list) > 1:
        if symbol_list[0] == "BITMEX" or symbol_list[0] == "OKEXFU":
            raise TypeError('Please use order_future to Placeorder!')

    account_id = ''
    account_name = ''

    order_src = 2  # sdk
    return _place_order(symbol=symbol, value=value, volume=-1,  # when place an order by volume, 'value' should be set to a negtive number
                        side=side, account_id=account_id,
                        account_name=account_name, price=price,
                        order_type=order_type, order_src=order_src, subject=SecurityType_Physical)


def order_future_close(symbol, order_type, position_side, prop, price=0):
    if not symbol or not order_type or not prop or not position_side:
        raise TypeError('order_future_close() : argument missing or incorrect argument type.')
    if order_type == OrderType_Limit and price<=0:
        raise TypeError('order_future_close() :  argument error, whit price <= 0 for order type \'OrderType_Limit\'.')
    if not '.' in symbol:
        raise TypeError('order_future_close() :  argument error, the symbol eg : \'BITMEX.XBTUSD\'')
    exchange, symbol_info = symbol.split('.')
    order_positions = get_positions(exchange, symbol)
    print(order_positions)
    if order_positions == []:
        print('error : can not find the position of \'', symbol, '\' where is currency = \'', symbol_info, '\'')
        return []
    for position in order_positions:

        if position['side'] == position_side:
            volume = round(position['amount'] * prop, 0)
            if position_side == PositionSide_Long:
                return _place_order(symbol=symbol, value=-1, volume=volume, side=OrderSide_Sell_Close, price=price,
                                    order_type=order_type, order_src=2,subject=SecurityType_Future,leverage=position["leverage"],account_id='')
            if position_side == PositionSide_Short:
                return _place_order(symbol=symbol, value=-1, volume=volume, side=OrderSide_Buy_Close, price=price,
                                    order_type=order_type, order_src=2, subject=SecurityType_Future,leverage=position["leverage"],
                                    account_id='')
        if exchange=="BITMEX":
            volume = round(position['amount'] * prop, 0)
            if position['side'] == PositionSide_Long:
                return _place_order(symbol=symbol, value=-1, volume=volume, side=OrderSide_Sell_Close, price=price,
                                    order_type=order_type, order_src=2, subject=SecurityType_Future,
                                    leverage=position["leverage"], account_id='')
            if position_side == PositionSide_Short:
                return _place_order(symbol=symbol, value=-1, volume=volume, side=OrderSide_Buy_Close, price=price,
                                    order_type=order_type, order_src=2, subject=SecurityType_Future,
                                    leverage=position["leverage"],
                                    account_id='')
        if exchange == "BYBIT":
            timeInForce = ""
            if order_type == OrderType_Limit:
                timeInForce=GoodTillCancel
            volume = round(position['amount'] * prop, 0)
            if position['side'] == PositionSide_Long:
                return _place_order(symbol=symbol, value=-1, volume=volume, side=OrderSide_Sell, price=price,
                                    order_type=order_type, order_src=2, subject=SecurityType_Future,
                                    leverage=position["leverage"], account_id='',time_in_force=timeInForce)
            if position_side == PositionSide_Short:
                return _place_order(symbol=symbol, value=-1, volume=volume, side=OrderSide_Buy, price=price,
                                    order_type=order_type, order_src=2, subject=SecurityType_Future,
                                    leverage=position["leverage"],
                                    account_id='',time_in_force=timeInForce)


def order_prop(symbol, side, order_type, prop, price=0):
    if not symbol or not order_type or not prop or not side:
        raise TypeError('order_prop() : argument missing or incorrect argument type.')
    if order_type == OrderType_Limit and price <= 0:
        raise TypeError('order_prop() :  argument error, with price <= 0 for order type \'OrderType_Limit\'.')
    if not '.' in symbol:
        raise TypeError('order_prop() :  argument error, the symbol eg : \'BINANCE.BTCUSDT\'')
    symbol_info = get_instruments(symbol)

    if symbol_info == []:
        print('error : the \'', symbol, '\' can not find')
        return
    if side == OrderSide_Buy:
        positions = get_positions(symbol_info[0]['marcket'], symbol_info[0]['rear'])
        if positions == []:
            print('error : can not find the position of \'', symbol, '\' where is currency = \'', symbol_info[0]['rear'], '\'')
            return []
        for position in positions:
            value = float(position['available'])*float(prop)
            return _place_order(symbol=symbol, value=value, volume=-1,  # when place an order by volume, 'value' should be set to a negtive number
                                side=side, account_id='',
                                account_name='', price=price,
                                order_type=order_type, order_src=2, subject=SecurityType_Physical)
    if side == OrderSide_Sell:
        positions = get_positions(symbol_info[0]['marcket'], symbol_info[0]['front'])
        if positions == []:
            print('error : can not find the position of \'', symbol, '\' where is currency = \'', symbol_info[0]['front'],
                  '\'')
            return []
        for position in positions:
            volume = float(position['available'])*float(prop)
            return _place_order(symbol=symbol, value=-1, volume=volume,
                                # when place an order by volume, 'value' should be set to a negtive number
                                side=side, account_id='',
                                account_name='', price=price,
                                order_type=order_type, order_src=2, subject=SecurityType_Physical)


def order_batch(orders, combine=False, account=''):
    orders = load_to_list(orders)

    place_order_req = PlaceOrderReq()
    try:
        for order in orders:
            pb_order = Order()
            if 'created_at' in order.keys():
                order.pop('created_at')
            if 'updated_at' in order.keys():
                order.pop('updated_at')
            order["order_src"] = 2  # 对于自己组的orders，order_src 必须设置上
            ex = order["symbol"].split(".")
            if len(ex) > 1:
                if ex[0] == "BITMEX" or ex[0] == "OKEXFU":
                    order["subject"] = SecurityType_Future
            pb_order = dict_to_protobuf(pb_klass_or_instance=pb_order, values=order, ignore_none=True)
            place_order_req.orders.extend([pb_order])
    except TypeError:
        raise TypeError('order_batch() : argument missing or incorrect argument type.')
        return []

    req = place_order_req.SerializeToString()
    status, result = py_nfi_place_order(req)

    if not status == CSDK_OPERATE_SUCCESS:

        _error_call_back(status)
        return []

    if not result:
        return []

    res = Orders()
    res.ParseFromString(result)

    return [protobuf_to_dict(res_order, including_default_value_fields=True) for
            res_order in res.data]


def order_future(symbol, volume, side, order_type, leverage=0, price=0,
                 exec_inst='', stop_price=0, account='',timeInForce = -1):
    if not symbol or not volume or not side or not order_type or len(symbol) <= 0:
        raise TypeError('order_future() : argument missing or incorrect argument type.')

    if volume <= 0:
        raise TypeError('order_future() : volume must > 0')
    if side < OrderSide_Buy_Open or side > OrderSide_Sell_Close:
        raise TypeError('order_future() : side wrong')
    if order_type < OrderType_Limit or order_type > OrderType_ProfitLimit:
        raise TypeError('order_future() : order_type wrong')

    order_src = 2  # sdk

    if isinstance(exec_inst, list):
        for i in range(len(exec_inst)):
            exec_inst[i] = str(exec_inst[i])
        exec_inst = ",".join(exec_inst)
    time_In_Force = ""
    if timeInForce>=0:
        if timeInForce==0:
            time_In_Force="GoodTillCancel"
        if timeInForce==1:
            time_In_Force= "ImmediateOrCancel"
        if timeInForce==2:
            time_In_Force= "FillOrKill"
    return _place_order(symbol=symbol, value=-1, volume=volume, side=side, price=price,
                        order_type=order_type, order_src=order_src, leverage=leverage,
                        subject=SecurityType_Future, exec_inst=exec_inst, stop_price=stop_price, account_id=account,time_in_force=time_In_Force )


def get_unfinished_orders(exchange=None, symbols=None):
    """
    查询所有未结委托
    """
    req = GetUnfinishedOrdersReq()
    if exchange:
        exchange = exchange.upper()
        req.exchange = exchange

    if symbols:
        symbols = load_to_list(symbols)
        for symbol in symbols:
            new_symbol = str(symbol).split(".")  # 只能要 'BINANCE.BTCUSDT' 中的 BTCUSDT
            if len(new_symbol) > 1:
                #symbol = symbols[1]
                if exchange and exchange==new_symbol[0]:
                    req.symbol.append(symbol)
                else:
                    req.symbol.append(symbol)
    req = req.SerializeToString()
    status, result = py_nfi_get_unfinished_orders(req)
    if not status == CSDK_OPERATE_SUCCESS:

        _error_call_back(status)
        return []

    res = Orders()
    res.ParseFromString(result)

    orders = [protobuf_to_dict(res_order, including_default_value_fields=True) for res_order in res.data]
    orders.sort(key=_created_time, reverse=True)

    if exchange:
        orders = [order for order in orders if exchange in order['symbol']]

    if symbols:
        order_list = []
        for order in orders:
            for symbol in symbols:
                if order['symbol'] == symbol:
                    new_order = order
                    order_list.append(new_order)
        orders = order_list
    return orders
    '''
    if not exchange:
        return orders
    else:
        orders = [order for order in orders if exchange in order['symbol']]
        return orders
    '''


def get_orders(exchange=None, symbols=None, cl_ord_ids=None):
    """
    查询日内全部委托
    """
    req = GetOrdersReq()
    if exchange:
        exchange = exchange.upper()
        req.exchange = exchange

    if symbols:
        symbols = load_to_list(symbols)
        for symbol in symbols:
            new_symbol = str(symbol).split(".")
            if len(new_symbol) > 1:#必须是BITMEX.XBTUSD这种格式
                if exchange and exchange == new_symbol[0]:#如果有交易所参数按照交易所过滤不符合规则的symbol
                    req.symbols.append(symbol)
                else:                                    #没有交易所参数直接把symbol加入
                    req.symbols.append(symbol)

    if cl_ord_ids:
        cl_ord_ids = load_to_list(cl_ord_ids)
        for cl_ord_id in cl_ord_ids:
            req.cl_ord_ids.append(cl_ord_id)

    req = req.SerializeToString()
    status, result = py_nfi_get_orders(req)

    if not status == CSDK_OPERATE_SUCCESS:
        _error_call_back(status)
        return []

    if not result:
        return []

    res = Orders()
    res.ParseFromString(result)

    orders = [protobuf_to_dict(res_order, including_default_value_fields=True) for res_order in res.data]

    orders.sort(key=_created_time, reverse=True)
    if exchange:
        orders = [order for order in orders if exchange in order['symbol']]
    if symbols:
        order_list = []
        for order in orders:
            for symbol in symbols:
                if order['symbol'] == symbol:
                    new_order = order
                    order_list.append(new_order)
        orders = order_list
    return orders
    '''
    if not exchange:
        return orders
    else:
        orders = [order for order in orders if exchange in order['symbol']]
        return orders
    '''


def get_orders_all(exchange=None, symbols=None, ord_status=None):
    req = GetOrdersAllReq()
    if exchange:
        exchange = exchange.upper()
        req.exchange = exchange

    if symbols:
        symbols = load_to_list(symbols)
        for symbol in symbols:
            new_symbol = str(symbol).split(".")
            if len(new_symbol) > 1:#必须是BITMEX.XBTUSD这种格式
                if exchange and exchange == new_symbol[0]:#如果有交易所参数按照交易所过滤不符合规则的symbol
                    req.symbols.append(symbol)
                else:                                    #没有交易所参数直接把symbol加入
                    req.symbols.append(symbol)

    if not ord_status:
        ord_status = [OrderStatus_New, OrderStatus_PartiallyFilled]

    if isinstance(ord_status, list):
        req.status.extend(ord_status)
    else:
        req.status.append(ord_status)
    # ord_status = load_to_list(ord_status)
    # for stat in ord_status:
    #     req.status.append(stat)

    req = req.SerializeToString()
    status, result = py_nfi_get_orders_all(req)

    if not status == CSDK_OPERATE_SUCCESS:
        _error_call_back(status)
        return []

    if not result:
        return []

    res = Orders()
    res.ParseFromString(result)

    orders = [protobuf_to_dict(res_order, including_default_value_fields=True) for res_order in res.data]

    orders.sort(key=_created_time, reverse=True)
    return orders


def order_cancel(wait_cancel_orders):
    """
    撤销委托
    """
    wait_cancel_orders = load_to_list(wait_cancel_orders)

    orders = Orders()
    cancel_order_req = CancelOrderReq()

    try:
        cl_ord_ids = [order['cl_ord_id'] for order in wait_cancel_orders]
    except Exception as e:
        # 传入的参数不是Order 类
        raise TypeError('order_cancel() : argument missing or incorrect argument type.')
    else:
        for cl_ord_id in cl_ord_ids:
            order = orders.data.add()
            order.cl_ord_id = cl_ord_id
            cancel_order_req.orders.extend([order])

        req = cancel_order_req.SerializeToString()

        status = py_nfi_cancel_order(req)
        if not status == CSDK_OPERATE_SUCCESS:
            _error_call_back(status)


def get_execution_reports(exchange=None,symbols=None):
    req = GetExecrptsReq()
    if exchange:
        exchange = exchange.upper()
        req.exchange = exchange
    if symbols:
        symbols = load_to_list(symbols)
        for symbol in symbols:
            new_symbol = str(symbol).split(".")  # 只能要 'BINANCE.BTCUSDT' 中的 BTCUSDT
            if len(new_symbol) > 1:
                # symbol = symbols[1]
                if exchange and exchange == new_symbol[0]:
                    req.symbols.append(symbol)
                else:
                    req.symbols.append(symbol)
    req = req.SerializeToString()
    status, result = py_nfi_get_execution_reports(req)
    if not status == CSDK_OPERATE_SUCCESS:

        _error_call_back(status)
        return []

    res = ExecRpts()
    res.ParseFromString(result)
    reports = [protobuf_to_dict(Execrpt, including_default_value_fields=True) for
                Execrpt in res.data]

    reports.sort(key=_created_time, reverse=True)
    if exchange:
        reports = [order for order in reports if exchange in order['symbol']]
    if symbols:
        report_list = []
        for report in reports:
            for symbol in symbols:
                if report['symbol'] == symbol:
                    new_report = report
                    report_list.append(new_report)
        reports = report_list
    return reports
    '''
    if not exchange:
        return reports
    else:
        reports = [order for order in reports if exchange in order['symbol']]
        return reports
    '''


def get_positions(exchange=None, currency=None,symbol=None):
    # 持仓信息
    req = GetPositionsReq()
    if not currency:
        currency = ''

    if not exchange:
        exchange = ''
    if not symbol:
        symbol = ''
    exchange = exchange.upper()
    currency = currency.lower()

    req.exchange = exchange
    req.currency = currency
    req.symbol = symbol
    req = req.SerializeToString()
    status, result = py_nfi_get_positions(req)

    # 如果调用rpc返回的状态不正确
    if not status == CSDK_OPERATE_SUCCESS:

        _error_call_back(status)
        return []

    positions = Positions()
    positions.ParseFromString(result)

    positions = [protobuf_to_dict(position, including_default_value_fields=True)
                 for position in positions.data]

    res = []
    for position in positions:
        t_crc = position["currency"]
        if "." not in t_crc:
            continue
        t_crc_list = t_crc.split(".")
        if('valid_available' in position.keys()):
            del position['valid_available']
        if ('can_reduce' in position.keys()):
            del position['can_reduce']
        if ('close_tfv' in position.keys()):
            del position['close_tfv']
        if ('filled_balance' in position.keys()):
            del position['filled_balance']
        if ('profit' in position.keys()):
            del position['profit']
        if ('pft_close_tfv' in position.keys()):
            del position['pft_close_tfv']
        if ('symbol_old'in position.keys()):
            del position['symbol_old']
        if ("liquidation_price_rl" in position.keys()):
            del position['liquidation_price_rl']

        if len(t_crc_list) != 2:
            continue
        t_exchange = t_crc_list[0]
        t_currency = t_crc_list[1]

        if exchange.strip() and exchange.upper() != t_exchange.upper():
            continue
        if 0 == position['subject']:
            if currency.strip() and currency.upper() != t_currency.upper():
                continue
        if 1 == position['subject']:
            if currency.strip() and currency.upper() != t_crc.upper():
                continue
        if 0 != position['subject']:
            if symbol.strip() and symbol != t_crc_list[0] + '.' + position["symbol"]:
                continue
        #if symbol != t_
        #if 0 != position['']
        '''原position中的currency格式为 交易所代码.币代码，如OKEX.btc，将此字段拆成两个独立的key，即在原posiiton中增加exchange'''
        if 0 == position["subject"]:  # 现货把currency改一下，期货不用改
            position['currency'] = t_currency
        position['exchange'] = t_exchange

        res.append(position)

    return res


def get_symbols_by_front(market, currency, df=False):
    if not market or not currency:
        raise TypeError('get_symbols_by_front() : argument missing or incorrect argument type.')

    market = market.upper()
    currency = currency.lower()

    status, result = py_nfi_get_symbols_by_front(market, currency)

    if not status == CSDK_OPERATE_SUCCESS:

        _error_call_back(status)
        return []

    symbols = InstrumentInfos()
    symbols.ParseFromString(result)

    symbols = [protobuf_to_dict(symbol, including_default_value_fields=True) for symbol in symbols.data]

    instrument_infos = [
        '{}'.format(instrumentinfo['symbol']) for instrumentinfo in symbols]

    if not df:
        return instrument_infos

    data = pd.DataFrame(instrument_infos)

    return data


def get_symbols_by_fc(market, from_currency, df=False):
    if not market or not from_currency:
        raise TypeError('get_symbols_by_fc() : argument missing or incorrect argument type.')

    market = market.upper()
    from_currency = from_currency.lower()

    status, result = py_nfi_get_symbols_by_fc(market, from_currency)

    if not status == CSDK_OPERATE_SUCCESS:

        _error_call_back(status)
        return []

    symbols = InstrumentInfos()
    symbols.ParseFromString(result)

    symbols = [protobuf_to_dict(symbol, including_default_value_fields=True)
               for symbol in symbols.data]

    instrument_infos = [
        '{}'.format(symbol['symbol']) for
        symbol in symbols]

    if not df:
        return instrument_infos

    data = pd.DataFrame(instrument_infos)

    return data


def get_symbol_of_coins(market, currency_a, currency_b, df=False):
    if not market or not currency_a or not currency_b:
        raise TypeError('get_symbol_of_coins() : argument missing or incorrect argument type.')

    market = market.upper()

    preq = TradingSymbolReq()
    preq.market = market

    preq.coin_a = currency_a.lower()
    preq.coin_b = currency_b.lower()

    req = preq.SerializeToString()

    status, result = py_nfi_get_symbol_of_coins(req)

    if not status == CSDK_OPERATE_SUCCESS:

        _error_call_back(status)
        return

    common_symbol_info = CommSymbolInfo()
    common_symbol_info.ParseFromString(result)

    # coins_info = {
    #   '{}'.format(common_symbol_info.data['symbol'])}

    if not df:
        return [common_symbol_info.data.symbole]

    data = pd.DataFrame([common_symbol_info.data.symbole])

    return data


def get_symbol(market, front, rear, df=False):
    if not market or not front or not rear:
        raise TypeError('get_symbol() : argument missing or incorrect argument type.')

    market = market.upper()

    preq = TradingSymbolReq()
    preq.market = market

    preq.coin_a = front.lower()
    preq.coin_b = rear.lower()

    req = preq.SerializeToString()

    status, result = py_nfi_get_symbol(req)
    if not status == CSDK_OPERATE_SUCCESS:

        _error_call_back(status)
        return None

    common_symbol_info = CommSymbolInfo()
    common_symbol_info.ParseFromString(result)
    '''
    common_symbol_info = [protobuf_to_dict(symbol_info, including_default_value_fields=True)
                          for symbol_info in common_symbol_info.data]
    symbol = {
        '{}'.format(symbol_info['symbol']): symbol_info for
        symbol_info in common_symbol_info}
    '''

    if not df:
        return common_symbol_info.data.symbole

    data = pd.DataFrame([{'symbol': common_symbol_info.data.symbole}])

    return data


def get_execution_reports_intraday(exchange=None,symbols=None):
    req = GetIntradayExecrptsReq()
    if not exchange:
        exchange = ''

    exchange = exchange.upper()
    req.exchange=exchange
    if symbols:
        symbols = load_to_list(symbols)
        for symbol in symbols:
            new_symbol = str(symbol).split(".")  # 只能要 'BINANCE.BTCUSDT' 中的 BTCUSDT
            if len(new_symbol) > 1:
                #symbol = symbols[1]
                if exchange and exchange==new_symbol[0]:
                    req.symbols.append(symbol)
                else:
                    req.symbols.append(symbol)

    req = req.SerializeToString()
    status, result = py_nfi_get_execution_reports_intraday(req)

    if not status == CSDK_OPERATE_SUCCESS:

        _error_call_back(status)
        return []

    res = ExecRpts()
    res.ParseFromString(result)

    reports = [protobuf_to_dict(Execrpt, including_default_value_fields=True) for
               Execrpt in res.data]

    reports.sort(key=_created_time, reverse=True)
    if exchange:
        reports = [order for order in reports if exchange in order['symbol']]
    if symbols:
        report_list = []
        for report in reports:
            for symbol in symbols:
                if report['symbol'] == symbol:
                    new_report = report
                    report_list.append(new_report)
        reports = report_list
    return reports
    '''
    if not exchange:
        return reports
    else:
        reports = [order for order in reports if exchange in order['symbol']]
        return reports
    '''


def get_orders_intraday(exchange=None,symbols=None):
    req=GetIntradayOrdersReq()
    if not exchange:
        exchange = ''
    exchange = exchange.upper()
    req.exchange=exchange
    if symbols:
        symbols = load_to_list(symbols)
        for symbol in symbols:
            new_symbol = str(symbol).split(".")  # 只能要 'BINANCE.BTCUSDT' 中的 BTCUSDT
            if len(new_symbol) > 1:
                # symbol = symbols[1]
                if exchange and exchange == new_symbol[0]:
                    req.symbols.append(symbol)
                else:
                    req.symbols.append(symbol)

    req = req.SerializeToString()
    status, result = py_nfi_get_orders_intraday(req)
    if not status == CSDK_OPERATE_SUCCESS:
        _error_call_back(status)
        return []

    res = Orders()
    res.ParseFromString(result)

    orders = [protobuf_to_dict(res_order, including_default_value_fields=True) for res_order in res.data]

    orders.sort(key=_created_time, reverse=True)
    if exchange:
        orders = [order for order in orders if exchange in order['symbol']]
    if symbols:
        order_list = []
        for order in orders:
            for symbol in symbols:
                if order['symbol'] == symbol:
                    new_order = order
                    order_list.append(new_order)
        orders = order_list
    return orders
    '''
    if not exchange:
        return orders
    else:
        orders = [order for order in orders if exchange in order['symbol']]
        return orders
    '''


def get_all_symbols_of_coin(market, from_currency, df=False):
    if not market or not from_currency:
        raise TypeError('get_all_symbols_of_coin() : argument missing or incorrect argument type.')

    market = market.upper()
    from_currency = from_currency.lower()

    status, result = py_nfi_get_all_symbols_of_coin(market, from_currency)

    if not status == CSDK_OPERATE_SUCCESS:

        _error_call_back(status)
        return []

    instruments = InstrumentInfos()
    instruments.ParseFromString(result)

    instruments = [protobuf_to_dict(instrument, including_default_value_fields=True)
                   for instrument in instruments.data]

    coins_info = ['{}'.format(instrument['symbol']) for instrument in instruments]

    if not df:
        return coins_info

    data = pd.DataFrame(coins_info)

    return data


def history(symbol, frequency, start_time, end_time, fields='', skip_suspended=True, fill_missing='', df=False):
    if not symbol or not frequency or not start_time or not end_time:
        raise TypeError('history() : argument missing or incorrect argument type.')

    if len(symbol) <= 0:
        return []

    start_time = load_to_datetime_str(start_time)
    end_time = load_to_datetime_str(end_time)

    if frequency == 'tick':

        status, result = py_nfi_history_ticks(symbol, start_time, end_time, fields, skip_suspended,
                                              fill_missing, 1)

        if not status == CSDK_OPERATE_SUCCESS:

            _error_call_back(status)
            return []

        ticks = Ticks()
        ticks.ParseFromString(result)
        ticks = [protobuf_to_dict(tick) for tick in ticks.data]
        ticks = [_reform_tick_data(tick) for tick in ticks]
        for tick in ticks:
            tick['symbol'] = symbol
        if not df:
            if not fields or fields == '':
                return ticks
            else:
                fields = load_to_list(fields)
                new_ticks = []
                for tick in ticks:
                    new_tick = {key: value for key, value in tick.items() if key in fields}
                    new_ticks.append(new_tick)
                return new_ticks

        if not ticks:
            return pd.DataFrame(columns=[fields])

        data = pd.DataFrame(ticks)
        if not fields or fields == '':
            return data
        else:
            fields = load_to_list(fields)
            return data[fields]

    else:

        frequency = _check_frequency(frequency)
        if not frequency:
            _error_call_back_by_check(ERR_INVALID_PARAMETER)
            return

        status, result = py_nfi_history_bars(symbol, frequency, start_time, end_time, fields, skip_suspended, fill_missing, 1)

        if not status == CSDK_OPERATE_SUCCESS:

            _error_call_back(status)
            return []

        bars = Bars()
        bars.ParseFromString(result)
        bars = [protobuf_to_dict(bars) for bars in bars.data]
        for bar in bars:
            bar['symbol'] = symbol
        if not df:
            if not fields or fields == '':
                return bars
            else:
                fields = load_to_list(fields)
                new_bars = []
                for bar in bars:
                    new_bar = {key: value for key, value in bar.items() if key in fields}
                    new_bars.append(new_bar)
                return new_bars

        if not bars:
            return pd.DataFrame(columns=[fields])

        data = pd.DataFrame(bars)
        if not fields or fields == '':
            return data
        else:
            fields = load_to_list(fields)
            return data[fields]


def history_n(symbol, frequency, count, end_time, fields='', skip_suspended=True, fill_missing='', df=False):
    if not symbol or not frequency or not count or not end_time:
        raise TypeError('history_n() : argument missing or incorrect argument type.')

    if len(symbol) <= 0:
        return []

    end_time = load_to_datetime_str(end_time)

    if frequency == 'tick':

        status, result = py_nfi_history_ticks_n(symbol, count, end_time, fields, skip_suspended,
                                                fill_missing, 1)

        if not status == CSDK_OPERATE_SUCCESS:

            _error_call_back(status)
            return []

        ticks = Ticks()
        ticks.ParseFromString(result)
        ticks = [protobuf_to_dict(tick) for tick in ticks.data]
        ticks = [_reform_tick_data(tick) for tick in ticks]
        for tick in ticks:
            tick['symbol'] = symbol
        if not df:
            if not fields or fields == '':
                return ticks
            else:
                fields = load_to_list(fields)
                new_ticks = []
                for tick in ticks:
                    new_tick = {key: value for key, value in tick.items() if key in fields}
                    new_ticks.append(new_tick)
                return new_ticks

        if not ticks:
            return pd.DataFrame(columns=[fields])

        data = pd.DataFrame(ticks)
        if not fields or fields == '':
            return data
        else:
            fields = load_to_list(fields)
            return data[fields]

    else:
        frequency = _check_frequency(frequency)
        if not frequency:
            _error_call_back_by_check(ERR_INVALID_PARAMETER)
            return

        status, result = py_nfi_history_bars_n(symbol, frequency, count, end_time, fields, skip_suspended,
                                               fill_missing, 1)

        if not status == CSDK_OPERATE_SUCCESS:

            _error_call_back(status)
            return []

        bars = Bars()
        bars.ParseFromString(result)
        bars = [protobuf_to_dict(bars) for bars in bars.data]
        for bar in bars:
            bar['symbol'] = symbol
        if not df:
            if not fields or fields == '':
                return bars
            else:
                fields = load_to_list(fields)
                new_bars = []
                for bar in bars:
                    new_bar = {key: value for key, value in bar.items() if key in fields}
                    new_bars.append(new_bar)
                return new_bars

        if not bars:
            return pd.DataFrame(columns=[fields])

        data = pd.DataFrame(bars)
        if not fields or fields == '':
            return data
        else:
            fields = load_to_list(fields)
            return data[fields]


def get_unfinished_orders_intraday(exchange=None,symbols=None):
    req=GetIntradayUnfinishedOrdersReq()
    if not exchange:
        exchange = ''

    exchange = exchange.upper()
    req.exchange=exchange
    if symbols:
        symbols = load_to_list(symbols)
        for symbol in symbols:
            new_symbol = str(symbol).split(".")  # 只能要 'BINANCE.BTCUSDT' 中的 BTCUSDT
            if len(new_symbol) > 1:
                # symbol = symbols[1]
                if exchange and exchange == new_symbol[0]:
                    req.symbols.append(symbol)
                else:
                    req.symbols.append(symbol)
    req = req.SerializeToString()
    status, result = py_nfi_get_unfinished_orders_intraday(req)

    if not status == CSDK_OPERATE_SUCCESS:

        _error_call_back(status)
        return []

    res = Orders()
    res.ParseFromString(result)

    orders = [protobuf_to_dict(res_order, including_default_value_fields=True) for res_order in res.data]

    if exchange:
        orders = [order for order in orders if exchange in order['symbol']]
    if symbols:
        order_list = []
        for order in orders:
            for symbol in symbols:
                if order['symbol'] == symbol:
                    new_order=order
                    order_list.append(new_order)
        orders=order_list
    return orders


def get_instruments(symbol):
    if not symbol or len(symbol) <= 0:
        raise TypeError('get_instruments() : argument missing or incorrect argument type.')

    if isinstance(symbol, list):
        symbol = symbol[0]

    preq = SearchCoinPairsReq()
    preq.symbol.append(symbol)
    preq.subject = SecurityType_Physical
    req = preq.SerializeToString()

    status, result = py_nfi_get_instruments(req)

    if not status == CSDK_OPERATE_SUCCESS:

        _error_call_back(status)
        return []

    res = SearchCoinPairsRsp()
    res.ParseFromString(result)
    instrument = protobuf_to_dict(res)["symbolinfos"]

    return instrument


def order_cancel_all(exchange=""):
    exchange = exchange.upper()

    status = py_nfi_cancel_all_orders(exchange)

    return status


def get_exchange_rate(currencies, from_currency=None, start_time=None, end_time=None):
    """
    查询公允汇率，返回python list[dictionary]
    :param currencies:
    :param from_currency:
    :param start_time:
    :param end_time:
    :return:
    """
    if not currencies:
        raise TypeError('get_exchange_rate() : argument missing or incorrect argument type.')

    currencies_list = load_to_list(currencies)
    currencies = ','.join(currencies_list)

    if not from_currency:
        from_currency = 'USD'

    if not start_time:
        start_time = ''
    if not end_time:
        end_time = ''

    currencies = currencies.lower()
    from_currency = from_currency.lower()

    status, result = py_nfi_get_exchange_rate(currencies, from_currency, start_time, end_time)

    if not status == CSDK_OPERATE_SUCCESS:

        _error_call_back(status)
        return []

    # 反序列化。ExchangeRates是一个list类型，每个健对应的值是一个字典
    rates = ExchangeRateList()
    rates.ParseFromString(result)

    # 把返回的字典中的值取出来，放到一个字典列表中返回给用户
    rates = [protobuf_to_dict(currency, including_default_value_fields=True) for currency in rates.data]

    return rates


def get_depth(symbol, points=50):
    '''
    :param symbol:  trade symbol, like:BITFINEX.btcusd
    :param points:  levels of depth
    :return:    {'bids':[], 'asks':[]}
    :info: 用于获取交易深度
    '''
    if not symbol or len(symbol) <= 0:
        return

    if points > 50:
        points = 50

    status, result = py_nfi_get_market_depth(symbol)

    if not status == CSDK_OPERATE_SUCCESS:
        print('status: ', status)
        _error_call_back(status)
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

    bids.sort(key=takePriceFromDepth, reverse=True)     # 买盘，降序
    asks.sort(key=takePriceFromDepth, reverse=False)    # 卖盘，升序
    acc_vol = 0
    for dpt in asks:
        acc_vol += dpt['volume']
        dpt['accumulate'] = acc_vol

    acc_vol = 0
    for dpt in bids:
        acc_vol += dpt['volume']
        dpt['accumulate'] = acc_vol

    depth = {'points': len(bids), 'created_at': timestamp2datetime(created_at), 'bids': bids, 'asks': asks}

    return depth


def vx_alert_msg(message):
    if not message:
        return
    alert_req = WxAlertReq()
    alert_req.message = message
    req = alert_req.SerializeToString()

    status = py_nfi_vx_alert_msg(req)
    if not status == CSDK_OPERATE_SUCCESS:
        _error_call_back(status)


def alert_msg(message):
    if not message:
        return
    alert_req = AlertMeReq()
    alert_req.message = message
    req = alert_req.SerializeToString()

    status = py_nfi_alert_msg(req)
    if not status == CSDK_OPERATE_SUCCESS:
        _error_call_back(status)


def get_symbol_for_future(exchange, base, quote, period='', date=''):
    if not exchange or not base or not quote:
        raise TypeError('get_symbol_for_future() : argument missing or incorrect argument type.')
    if not period and not date:
        raise TypeError('get_symbol_for_future() : argument missing or incorrect argument type.')
    preq = TargetSymbolReq()
    preq.market = exchange
    preq.front = base.lower()
    preq.rear = quote.lower()
    preq.contract_period = period.lower()
    preq.subject = SecurityType_Future
    preq.date = date
    req = preq.SerializeToString()

    status, result = py_nfi_get_symbol_for_future(req)
    if not status == CSDK_OPERATE_SUCCESS:
        _error_call_back(status)
        return None

    common_symbol_info = CommSymbolInfo()
    common_symbol_info.ParseFromString(result)
    '''
    common_symbol_info = [protobuf_to_dict(symbol_info, including_default_value_fields=True)
                          for symbol_info in common_symbol_info.data]
    symbol = {
        '{}'.format(symbol_info['symbol']): symbol_info for
        symbol_info in common_symbol_info}
    '''
    return common_symbol_info.data.symbole


def get_future_instruments(symbol, df=False):
    if not symbol:
        raise TypeError('get_future_instruments() : argument \'symbol\' must be provided.')
    print('api.trade.get_future_instruments: symbol=', symbol, ', ds=', df)
    preq = SearchCoinPairsReq()
    preq.symbol.append(symbol)
    preq.subject = SecurityType_Future
    req = preq.SerializeToString()

    status, result = py_nfi_get_instruments(req)

    if not status == CSDK_OPERATE_SUCCESS:
        _error_call_back(status)
        return

    res = SearchCoinPairsRsp()
    res.ParseFromString(result)

    instrument = protobuf_to_dict(res)["symbolinfos"]

    for symbol in instrument:
        symbol["symbol"] = symbol.pop("symbole")
        symbol["market"] = symbol.pop("marcket")
        symbol["symbol"] = symbol["market"] + "." + symbol["symbol"]
        symbol["settle_currency"] = symbol.pop("settlCurrency")
        symbol["period"] = symbol.pop("contract_period")
        if "settle_date" not in symbol.keys():
            symbol["settle_date"] = ""

    if df:
        instrument = pd.DataFrame(instrument)

    return instrument


def get_future_instruments_by_period(period, exchange=None, df=False):
    if not period:
        raise TypeError('get_future_instruments_by_period() : argument \'contract_period\' must be provided.')

    preq = SearchCoinPairsReq()
    if exchange:
        preq.exchange = exchange.upper()

    preq.subject = SecurityType_Future

    preq.contract_period = period.lower()
    # print('get_future_instruments_by_period preq = \n', preq)
    req = preq.SerializeToString()
    # print('get_future_instruments_by_period req = \n', req)

    status, result = py_nfi_get_instruments(req)
    # print('get_future_instruments_by_period status = ', status)
    if not status == CSDK_OPERATE_SUCCESS:

        _error_call_back(status)
        return

    res = SearchCoinPairsRsp()
    res.ParseFromString(result)
    # print('get_future_instruments_by_period: ', res)

    instrument = protobuf_to_dict(res)["symbolinfos"]
    for symbol in instrument:
        symbol["symbol"] = symbol.pop("symbole")
        symbol["market"] = symbol.pop("marcket")
        symbol["symbol"] = symbol["market"] + "." + symbol["symbol"]
        symbol["settle_currency"] = symbol.pop("settlCurrency")
        symbol["period"] = symbol.pop("contract_period")
        if "settle_date" not in symbol.keys():
            symbol["settle_date"] = ""
    if df:
        instrument = pd.DataFrame(instrument)

    return instrument


def get_future_instruments_by_base(base, period=None, df=False):
    if not base:
        raise TypeError('get_future_instruments_by_base() : argument \'base\' must be provided.')

    preq = SearchCoinPairsReq()
    if period:

        preq.contract_period = period.lower()

    preq.base = base.lower()
    preq.subject = SecurityType_Future
    # print('get_future_instruments_by_period preq = ', preq)
    req = preq.SerializeToString()

    status, result = py_nfi_get_instruments(req)

    if not status == CSDK_OPERATE_SUCCESS:

        _error_call_back(status)
        # print('get_future_instruments_by_base status = ', status)
        return

    res = SearchCoinPairsRsp()
    res.ParseFromString(result)

    instrument = protobuf_to_dict(res)["symbolinfos"]
    for symbol in instrument:
        symbol["symbol"] = symbol.pop("symbole")
        symbol["market"] = symbol.pop("marcket")
        symbol["symbol"] = symbol["market"] + "." + symbol["symbol"]
        symbol["settle_currency"] = symbol.pop("settlCurrency")
        symbol["period"] = symbol.pop("contract_period")
        if "settle_date" not in symbol.keys():
            symbol["settle_date"] = ""
    if df:
        instrument = pd.DataFrame(instrument)

    return instrument


def get_stats(base, df=False):
    if not base:
        raise TypeError('get_stats() : argument \'base\' must be provided.')

    preq = StatsReq()

    preq.Underlying_base = base.lower()

    req = preq.SerializeToString()

    status, result = py_nfi_get_target_stats(req)

    if not status == CSDK_OPERATE_SUCCESS:

        _error_call_back(status)
        return

    res = StatItems()
    res.ParseFromString(result)

    stats = protobuf_to_dict(res)["data"]

    if df:
        stats = pd.DataFrame(stats)

    return stats


def get_mark_price(symbol):
    if not symbol:
        raise TypeError('get_mark_price() : argument \'symbol\' must be provided.')

    status, price = py_nfi_get_mark_price(symbol)

    if not status == CSDK_OPERATE_SUCCESS:

        _error_call_back(status)
        return None

    return price


def get_settlements(symbol, count=100, end_time=None):
    if not symbol:
        raise TypeError('get_settlements() : argument \'symbol\' must be provided.')

    preq = GetSettlementReq()
    preq.data.symbol = symbol
    if count:
        preq.data.count = count
    if end_time:
        if isinstance(end_time, datetime):
            timestamp = end_time.timestamp()

        preq.data.end_time.seconds = int(timestamp)

    req = preq.SerializeToString()

    status, result = py_nfi_get_settlements(req)

    if not status == CSDK_OPERATE_SUCCESS:

        _error_call_back(status)
        return

    res = SettlementItems()
    res.ParseFromString(result)

    stats = protobuf_to_dict(res)["data"]

    return stats


def get_funding_rate(symbol):
    if not symbol:
        raise TypeError('get_funding_rate() : argument \'symbol\' must be provided.')

    preq = SymbolReq()
    preq.symbol = symbol

    req = preq.SerializeToString()

    status, result = py_nfi_get_fundingRate(req)

    if not status == CSDK_OPERATE_SUCCESS:

        _error_call_back(status)
        return

    res = FundingRateResp()
    res.ParseFromString(result)

    rate = protobuf_to_dict(res)["data"]

    return rate


def get_margin_assets(exchange, currency=None):
    if not exchange:
        raise TypeError('get_margin_assets() : argument \'exchange\' must be provided.')

    preq = GetMarginAssetsReq()
    preq.exchange = exchange.upper()

    if currency:

        preq.currency = currency.lower()

    req = preq.SerializeToString()

    status, result = py_nfi_get_margin_assets(req)

    if not status == CSDK_OPERATE_SUCCESS:

        _error_call_back(status)
        return

    res = GetMarginAssetsResp()
    res.ParseFromString(result)

    asset = protobuf_to_dict(res)["data"]["data"]  # 要返回一个map,而不是嵌套的

    return asset


def set_mode(exchange, symbol, model):
    if not symbol or not model or not exchange:
        raise TypeError('set_mode() : argument missing or incorrect argument type.')

    if "." not in symbol:

        raise TypeError('set_mode() : incorrect symbol.')

    preq = SetModeReq()
    t_crc_list = symbol.split(".")
    preq.exchange = t_crc_list[0]
    preq.symbol = symbol
    preq.model = model
    preq.exchange = exchange.upper()

    req = preq.SerializeToString()

    status, result = py_nfi_set_margin_mode(req)

    if not status == CSDK_OPERATE_SUCCESS:

        _error_call_back(status)
        return

    res = StatResp()
    res.ParseFromString(result)

    rs = protobuf_to_dict(res)

    # print('sdk-set_mode: response = ', rs)

    rs = rs['data']

    if rs['ret'] != CSDK_OPERATE_SUCCESS:
        print('set_mode failed with reason: ', rs['reason'])

    return rs


def set_leverage(exchange, symbol, leverage,position_side=None):
    if not symbol or not exchange:
        raise TypeError('set_leverage() : argument missing or incorrect argument type.')

    if "." not in symbol:
        raise TypeError('set_leverage() : incorrect symbol.')

    if position_side != None and (position_side < 1 or position_side > 2):
        raise TypeError('set_leverage() : error position_side.')

    preq = SetLeverageReq()
    t_crc_list = symbol.split(".")

    preq.exchange = t_crc_list[0]
    preq.symbol = symbol
    preq.leverage = leverage
    preq.exchange = exchange.upper()
    if position_side != None:
        preq.side = position_side
    req = preq.SerializeToString()

    status, result = py_nfi_set_leverage(req)

    if not status == CSDK_OPERATE_SUCCESS:

        _error_call_back(status)
        return

    res = StatResp()
    res.ParseFromString(result)

    rs = protobuf_to_dict(res)

    # print('sdk-set_leverage: response = ', rs)
    rs = rs['data']

    if rs['ret'] != CSDK_OPERATE_SUCCESS:
        print('set_leverage failed with reason: ', rs['reason'])

    return rs


def add_margin(exchange, symbol, amount):
    if not symbol or not amount or not exchange:
        raise TypeError('add_margin() : argument missing or incorrect argument type.')

    if "." not in symbol:
        raise TypeError('set_leverage() : incorrect symbol.')

    preq = SetMarginReq()
    t_crc_list = symbol.split(".")
    preq.exchange = t_crc_list[0]
    preq.symbol = symbol
    preq.amount = amount
    preq.exchange = exchange.upper()

    req = preq.SerializeToString()

    status, result = py_nfi_add_margin(req)

    if not status == CSDK_OPERATE_SUCCESS:
        _error_call_back(status)
        return

    res = StatResp()
    res.ParseFromString(result)

    rs = protobuf_to_dict(res)

    print('sdk-add_margin: response = ', rs)

    rs = rs['data']

    if rs['ret'] != CSDK_OPERATE_SUCCESS:
        print('add_margin failed with reason: ', rs['reason'])

    return rs


def _created_time(ele):
    return ele['created_at']
