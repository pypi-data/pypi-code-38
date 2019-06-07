# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals

# 基本api
import getopt
import sys

from nf.model.storage import context

from nf import __version__
from nf.enum import *

from nf.csdk.c_sdk import py_nfi_set_version
from .basic import (
    set_token, get_version, subscribe, unsubscribe, current_bar, get_inst_depth,
    get_inst_trade, subscribe_tx, unsubscribe_tx, current, get_strerror, schedule, run, log,
    set_serv_addr, stop, now)

# 交易api
from .trade import (
    order_volume, order_value, order_batch, order_cancel, order_cancel_all,
    get_positions, get_orders, get_unfinished_orders, get_execution_reports,
    get_symbols_by_front, get_symbols_by_fc, get_symbol_of_coins,
    get_all_symbols_of_coin, get_symbol, get_execution_reports_intraday,
    get_orders_intraday, get_instruments, order_prop, order_future_close,
    history, history_n, get_unfinished_orders_intraday, get_exchange_rate,
    get_depth, alert_msg, vx_alert_msg, order_future, get_symbol_for_future,
    get_future_instruments, get_future_instruments_by_period,
    get_future_instruments_by_base, get_stats, get_mark_price,
    get_settlements, get_funding_rate, get_margin_assets, set_mode,
    set_leverage, add_margin, get_orders_all)

# 数据查询api
from .query import (get_trades)

from .strategies import run_strategy_duidao, run_strategy_budan, update_strategy_datas, add_strategy_rds,\
    run_strategy_kongpan
__all__ = [
    'context',
    'set_token', 'get_version', 'subscribe', 'subscribe_tx', 'unsubscribe','unsubscribe_tx',
    'current', 'get_strerror', 'schedule', 'run', 'get_instruments',
    'log', 'stop', 'now', 'set_serv_addr', 'current_bar',
    'order_volume', 'order_value', 'order_batch', 'order_cancel', 'order_cancel_all',
    'get_positions', 'get_orders', 'get_unfinished_orders', 'get_execution_reports',
    'get_execution_reports_intraday', 'get_orders_intraday',
    'get_unfinished_orders_intraday', 'get_orders_all',

    'get_symbols_by_front', 'get_symbols_by_fc', 'get_symbol_of_coins',
    'get_all_symbols_of_coin', 'get_symbol',

    'history', 'history_n',

    'get_exchange_rate',
    'get_depth',
    'alert_msg', 'vx_alert_msg',

    'get_trades', 'get_inst_depth', 'get_inst_trade',

    'order_future', 'get_symbol_for_future', 'get_future_instruments',
    'get_future_instruments_by_period', 'get_future_instruments_by_base',
    'get_stats', 'get_mark_price', 'get_settlements', 'get_funding_rate',
    'get_margin_assets', 'set_mode', 'set_leverage', 'add_margin',
    'order_prop', 'order_future_close',

    'run_strategy_duidao', 'run_strategy_budan', 'update_strategy_datas',
    'add_strategy_rds', 'run_strategy_kongpan',

    'SecurityType_Physical',
    'SecurityType_Future',
    'ExecType_Unknown',
    'ExecType_Failed',
    'ExecType_New',
    'ExecType_PartiallyFilled',
    'ExecType_PartiallyCanceled',
    'ExecType_Filled',
    'ExecType_Canceled',
    'ExecType_Expired',
    'ExecType_Rejected',
    'ExecType_PendingNew',
    'ExecType_CancelRejected',

    'OrderStatus_Unknown',
    'OrderStatus_Failed',
    'OrderStatus_New',
    'OrderStatus_PartiallyFilled',
    'OrderStatus_PartiallyCanceled',
    'OrderStatus_Filled',
    'OrderStatus_Canceled',
    'OrderStatus_Expired',
    'OrderStatus_Rejected',
    'OrderStatus_PendingNew',

    'OrderRejectReason_Unknown',
    'OrderRejectReason_RiskRuleCheckFailed',
    'OrderRejectReason_NoEnoughCash',
    'OrderRejectReason_NoEnoughPosition',
    'OrderRejectReason_IllegalAccountId',
    'OrderRejectReason_IllegalStrategyId',
    'OrderRejectReason_IllegalSymbol',
    'OrderRejectReason_IllegalVolume',
    'OrderRejectReason_IllegalPrice',
    'OrderRejectReason_AccountDisabled',
    'OrderRejectReason_AccountDisconnected',
    'OrderRejectReason_AccountLoggedout',
    'OrderRejectReason_NotInTradingSession',
    'OrderRejectReason_OrderTypeNotSupported',
    'OrderRejectReason_Throttle',
    'OrderRejectReason_SymbolSuspended',
    'OrderRejectReason_Internal',
    'CancelOrderRejectReason_OrderFinalized',
    'CancelOrderRejectReason_UnknownOrder',
    'CancelOrderRejectReason_BrokerOption',
    'CancelOrderRejectReason_AlreadyInPendingCancel',

    'OrderSide_Unknown',
    'OrderSide_Buy',
    'OrderSide_Sell',
    'OrderSide_Buy_Open',
    'OrderSide_Buy_Close',
    'OrderSide_Sell_Open',
    'OrderSide_Sell_Close',
    'OrderSide_Sell_Liquidation',
    'OrderSide_Sell_Reduce',
    'OrderSide_Buy_Liquidation',
    'OrderSide_Buy_Reduce',

    'OrderType_Unknown',
    'OrderType_Limit',
    'OrderType_Market',
    'OrderType_StopMarket',
    'OrderType_StopLimit',
    'OrderType_ProfitMarket',
    'OrderType_ProfitLimit',

    'OrderDuration_Unknown',
    'OrderDuration_FAK',
    'OrderDuration_FOK',
    'OrderDuration_GFD',
    'OrderDuration_GFS',
    'OrderDuration_GTD',
    'OrderDuration_GTC',
    'OrderDuration_GFA',

    'OrderQualifier_Unknown',
    'OrderQualifier_BOC',
    'OrderQualifier_BOP',
    'OrderQualifier_B5TC',
    'OrderQualifier_B5TL',

    'OrderStyle_Unknown',
    'OrderStyle_Volume',
    'OrderStyle_Value',

    'PositionSide_Unknown',
    'PositionSide_Long',
    'PositionSide_Short',

    'PositionEffect_Unknown',
    'PositionEffect_Open',
    'PositionEffect_Close',
    'PositionEffect_CloseToday',
    'PositionEffect_CloseYesterday',

    'PositionMode_Unknown',
    'PositionMode_Full',
    'PositionMode_Isolate',

    'CashPositionChangeReason_Unknown',
    'CashPositionChangeReason_Trade',
    'CashPositionChangeReason_Inout',

    'MODE_LIVE',
    'MODE_BACKTEST',
    'ADJUST_NONE',
    'ADJUST_PREV',
    'ADJUST_POST',

    'ExecInstType_PostOnly',
    'ExecInstType_MarkPrice',
    'ExecInstType_IndexPrice',
    'ExecInstType_LastPrice',
    'ExecInstType_ReduceOnly',

    'GoodTillCancel',
    'ImmediateOrCancel',
    'FillOrKill'
]

try:
    __all__ = [str(item) for item in __all__]
    py_nfi_set_version(__version__.__version__, 'python')

    command_argv = sys.argv[1:]
    options, args = getopt.getopt(command_argv, None,
                                  ['strategy_id=', 'filename=',
                                   'mode=', 'token=',
                                   'backtest_start_time=',
                                   'backtest_end_time=',
                                   'backtest_initial_cash=',
                                   'backtest_transaction_ratio=',
                                   'backtest_commission_ratio=',
                                   'backtest_slippage_ratio=',
                                   'backtest_adjust=',
                                   'backtest_check_cache=',
                                   'serv_addr='
                                   ])

    for option, value in options:
        if option == '--serv_addr' and value:
            set_serv_addr(value)
            break
except BaseException as e:
    pass
