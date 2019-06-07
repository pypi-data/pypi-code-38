#!/usr/bin/env python

from sqlalchemy.ext.declarative import declarative_base

HummingbotBase = declarative_base()
SparrowBase = declarative_base()


def get_hummingbot_base():
    from .backtest_account_asset import BacktestAccountAsset
    from .backtest_account import BacktestAccount
    from .market_withdraw_rules import MarketWithdrawRules
    return HummingbotBase


def get_sparrow_base():
    pass
