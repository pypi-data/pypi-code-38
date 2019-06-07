# coding=utf8
from __future__ import print_function, absolute_import, unicode_literals

SecurityType_Physical = 0   # 现货
SecurityType_Future = 1     # 期货

ExecType_Unknown = 0
ExecType_Failed = 1             # 报送失败
ExecType_New = 2                # 已报送
ExecType_PartiallyFilled = 3    # 部分成交
ExecType_PartiallyCanceled = 4  # 部分成交撤销
ExecType_Filled = 5             # 已完成
ExecType_Canceled = 6           # 已撤销
ExecType_Expired = 7            # 过期
ExecType_Rejected = 8           # 已拒绝
ExecType_PendingNew = 10        # 待报
ExecType_CancelRejected = 19    # 撤单被拒绝

OrderStatus_Unknown = 0
OrderStatus_Failed = 1              # 报送失败
OrderStatus_New = 2                 # 已报送
OrderStatus_PartiallyFilled = 3     # 部分成交
OrderStatus_PartiallyCanceled = 4   # 部分成交撤销
OrderStatus_Filled = 5              # 已完成
OrderStatus_Canceled = 6            # 已撤销
OrderStatus_Expired = 7             # 过期
OrderStatus_Rejected = 8            # 已拒绝
OrderStatus_PendingNew = 10         # 待报

OrderRejectReason_Unknown = 0                           # 未知原因
OrderRejectReason_RiskRuleCheckFailed = 1               # 不符合风控规则
OrderRejectReason_NoEnoughCash = 2                      # 资金不足
OrderRejectReason_NoEnoughPosition = 3                  # 仓位不足
OrderRejectReason_IllegalAccountId = 4                  # 非法账户ID
OrderRejectReason_IllegalStrategyId = 5                 # 非法策略ID
OrderRejectReason_IllegalSymbol = 6                     # 非法交易代码
OrderRejectReason_IllegalVolume = 7                     # 非法委托量
OrderRejectReason_IllegalPrice = 8                      # 非法委托价
OrderRejectReason_AccountDisabled = 10                  # 交易账号被禁止交易
OrderRejectReason_AccountDisconnected = 11              # 交易账号未连接
OrderRejectReason_AccountLoggedout = 12                 # 交易账号未登录
OrderRejectReason_NotInTradingSession = 13              # 非交易时段
OrderRejectReason_OrderTypeNotSupported = 14            # 委托类型不支持
OrderRejectReason_Throttle = 15                         # 流控限制
OrderRejectReason_SymbolSuspended = 16                  # 交易代码停牌
OrderRejectReason_Internal = 999                        # 内部错误
CancelOrderRejectReason_OrderFinalized = 101            # 委托已完成
CancelOrderRejectReason_UnknownOrder = 102              # 未知委托
CancelOrderRejectReason_BrokerOption = 103              # 柜台设置
CancelOrderRejectReason_AlreadyInPendingCancel = 104    # 委托撤销中

OrderSide_Unknown = 0
OrderSide_Buy = 1                   # 买入
OrderSide_Sell = 2                  # 卖出
OrderSide_Buy_Open = 3              # 买入开仓
OrderSide_Buy_Close = 4             # 买入平仓
OrderSide_Sell_Open = 5             # 卖出开仓
OrderSide_Sell_Close = 6            # 卖出平仓
OrderSide_Sell_Liquidation = 7      # 强平卖出，以下4种交易所下单返回
OrderSide_Sell_Reduce = 8           # 减仓卖出
OrderSide_Buy_Liquidation = 9       # 强平买入
OrderSide_Buy_Reduce = 10           # 减仓买入

OrderType_Unknown = 0
OrderType_Limit = 1         # 限价委托
OrderType_Market = 2        # 市价委托
OrderType_StopMarket = 3    # 市价止损委托
OrderType_StopLimit = 4     # 限价止损委托
OrderType_ProfitMarket = 5  # 市价止盈委托
OrderType_ProfitLimit = 6   # 限价止盈委托

OrderDuration_Unknown = 0
OrderDuration_FAK = 1  # 即时成交剩余撤销(fill and kill)
OrderDuration_FOK = 2  # 即时全额成交或撤销(fill or kill)
OrderDuration_GFD = 3  # 当日有效(good for day)
OrderDuration_GFS = 4  # 本节有效(good for section)
OrderDuration_GTD = 5  # 指定日期前有效(goodltilldate)
OrderDuration_GTC = 6  # 撤销前有效(goodtillcancel)
OrderDuration_GFA = 7  # 集合竞价前有效(good for auction)

OrderQualifier_Unknown = 0
OrderQualifier_BOC = 1  # 对方最优价格(best of counterparty)
OrderQualifier_BOP = 2  # 己方最优价格(best of party)
OrderQualifier_B5TC = 3  # 最优五档剩余撤销(best 5 then cancel)
OrderQualifier_B5TL = 4  # 最优五档剩余转限价(best 5 then limit)

OrderStyle_Unknown = 0
OrderStyle_Volume = 1
OrderStyle_Value = 2

PositionSide_Unknown = 0
PositionSide_Long = 1  # 多方向
PositionSide_Short = 2  # 空方向

PositionEffect_Unknown = 0
PositionEffect_Open = 1  # 开仓
PositionEffect_Close = 2  # 平仓, 具体语义取决于对应的交易所
PositionEffect_CloseToday = 3  # 平今仓
PositionEffect_CloseYesterday = 4  # 平昨仓

PositionMode_Unknown = 0
PositionMode_Full = 1
PositionMode_Isolate = 2

CashPositionChangeReason_Unknown = 0
CashPositionChangeReason_Trade = 1  # 交易
CashPositionChangeReason_Inout = 2  # 出入金 / 出入持仓

MODE_UNKNOWN = 0
MODE_LIVE = 1
MODE_BACKTEST = 2

ADJUST_NONE = 0
ADJUST_PREV = 1
ADJUST_POST = 2


ExecInstType_PostOnly = 0  # 被动委托 Valid options: ParticipateDoNotInitiate, AllOrNone, MarkPrice, IndexPrice, LastPrice, Close, ReduceOnly, Fixed. 'AllOrNone' instruction requires displayQty to be 0. 'MarkPrice', 'IndexPrice' or 'LastPrice' instruction valid for 'Stop', 'StopLimit', 'MarketIfTouched', and 'LimitIfTouched' orders.
ExecInstType_MarkPrice = 1  # 在止损/盈单中触发价使用标记价格MarkPrice 此3个价格不可多选
ExecInstType_IndexPrice = 2  # 在止损/盈单中触发价使用指数价格（bitmex指数）IndexPrice
ExecInstType_LastPrice = 3  # 在止损/盈单中触发价使用最新的合约价格LastPrice
ExecInstType_ReduceOnly = 4  # 只减仓，只减少持有的仓位，而不允许另开当前持仓反向的仓位；不影响其他活跃但没有执行的订单，打算减仓建议使用ReduceOnly

GoodTillCancel = 0
ImmediateOrCancel =1
FillOrKill = 2