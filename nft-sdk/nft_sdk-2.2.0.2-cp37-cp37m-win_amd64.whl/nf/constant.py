# coding=utf-8
from __future__ import unicode_literals, print_function, absolute_import

SUB_ID = 'SUB_ID:{}:{}:{}'  # 订阅股票唯一id  由三部分组成  symbol frequency count
SUB_TAG = 'SUB_TAG:{}:{}'  # 取消订阅股票标签 由两部分组成  symbol frequency

DATA_TYPE_TICK = 'tick'
DATA_TYPE_BAR = 'bar'

"""
c-sdk回调的类型
"""
CALLBACK_TYPE_TICK = 'data.api.Tick'
CALLBACK_TYPE_BAR = 'data.api.Bar'
CALLBACK_TYPE_SCHEDULE = 'schedule'
CALLBACK_TYPE_EXECRPT = 'core.api.ExecRpt'
CALLBACK_TYPE_ORDER = 'core.api.Order'
CALLBACK_TYPE_INDICATOR = 'core.api.Indicator'
CALLBACK_TYPE_CASH = 'core.api.Cash'
CALLBACK_TYPE_POSITION = 'core.api.Position'
CALLBACK_TYPE_PARAMETERS = 'runtime-config'
CALLBACK_TYPE_ERROR = 'error'
CALLBACK_TYPE_TIMER = 'timer'
CALLBACK_TYPE_BACKTEST_FINISH = 'backtest_finish'
CALLBACK_TYPE_STOP = 'STOP'

CALLBACK_TYPE_TRADE_CONNECTED = 'trade_connected'
CALLBACK_TYPE_TRADE_DISCONNECTED = 'data_disconnected'

CALLBACK_TYPE_DATA_CONNECTED = 'data_connected'
CALLBACK_TYPE_DATA_DISCONNECTED = 'data_disconnected'

CALLBACK_TYPE_ACCOUNTSTATUS = 'core.api.AccountStatus'

TRADE_CONNECTED = 1
DATA_CONNECTED = 2


SCHEDULE_INFO = 'date_rule={date_rule},time_rule={time_rule}'

HISTORY_ADDR = 'ds-history-rpc'
HISTORY_REST_ADDR = 'ds-history-rpcgw'
FUNDAMENTAL_ADDR = 'ds-fundamental-rpc'

CSDK_OPERATE_SUCCESS = 0  # c-sdk 操作成功

ERROR_FORMAT = 'error code={}, error info={}'

''' error codes  '''
SUCCESS = 0       # "成功"
ERR_INVALID_TOKEN = 1000    # "错误或无效的token"
ERR_CONNECT_TERM_SERV = 1001    # "无法连接到终端服务"
ERR_CONNECT_HISTORY_SERV = 1002    # "无法连接到历史行情服务"
ERR_QUERY_SERVER_ADDR_ERROR = 1010    # "无法获取服务器地址列表"
ERR_PARSE_MASSAGE = 1011    # "消息包解析错误"
ERR_PARSE_NETWORK_MASSAGE = 1012    # "网络消息包解析错误"
ERR_CALL_TRADE_SERVICE = 1013    # "交易服务调用错误"
ERR_CALL_HISTORY_SERVICE = 1014    # "历史行情服务调用错误"
ERR_CALL_STRATEGY_SERIVCE = 1015    # "策略服务调用错误"
ERR_CALL_RTCONFIG_SERIVCE = 1016    # "动态参数调用错误"
ERR_CALL_FUNDMENTAL_SERVICE = 1017    # "基本面数据服务调用错误"
ERR_CALL_BACKTEST_SERVICE = 1018    # "回测服务调用错误"
ERR_CALL_TRADEGW_SERIVCE = 1019    # "交易网关服务调用错误"
ERR_INVALID_ACCOUNT_ID = 1020    # "无效的ACCOUNT_ID"
ERR_INVALID_DATE = 1021    # "非法日期格式"


# 交易部分 1100～1199 */

ERR_TD_LIVE_CONNECT = 1100    # "交易消息服务连接失败"
ERR_TD_LIVE_CONNECT_LOST = 1101    # "交易消息服务断开"

# 数据部分 1200～1299*/

ERR_MD_LIVE_CONNECT = 1200    # "实时行情服务连接失败"
ERR_MD_LIVE_CONNECT_LOST = 1201    # "实时行情服务连接断开"


# 回测部分 1300~1399*/

ERR_BT_BEGIN = 1300    # "初始化回测失败，可能是终端未启动或无法连接到终端"
ERR_BT_INVALID_TIMESPAN = 1301    # "回测时间区间错误"
ERR_BT_READ_CACHE_ERROR = 1302    # "回测读取缓存数据错误"
ERR_BT_WRITE_CACHE_ERROR = 1303    # "回测写入缓存数据错误"

ERR_RUNTIME_EXCEPTION = 1400    # "运行时异常"

ERR_INVALID_PARAMETER = 1500    # "参数错误"

"""
trade
"""
ExecInstType_PostOnly = 'ExecInstType_PostOnly'
ExecInstType_Hidden = 'ExecInstType_Hidden'
ExecInstType_AllOrNone = 'ExecInstType_AllOrNone'
ExecInstType_MarkPrice = 'ExecInstType_MarkPrice'
ExecInstType_IndexPrice = 'ExecInstType_IndexPrice'
ExecInstType_LastPrice = 'ExecInstType_LastPrice'
ExecInstType_Close = 'ExecInstType_Close'
ExecInstType_ReduceOnly = 'ExecInstType_ReduceOnly'
ExecInstType_Iceberg = 'ExecInstType_Iceberg'
ExecInstType_CloseOnTrigger = 'ExecInstType_CloseOnTrigger'
