#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''                                                          
Copyright (C)2018 SenseDeal AI, Inc. All Rights Reserved                                                      
File: {name}.py
Author: xuwei                                        
Email: weix@sensedeal.ai                                 
Last modified: 2018.12.23
Description:                                            
'''

class StockPriceTickObj(object):
    def __init__(self,dct):
        self.stock_code = dct['stock_code']
        self.name = dct['name']
        self.open_today = dct['open_today']
        self.close_last = dct['close_last']
        self.price_current = dct['price_current']
        self.price_high = dct['price_high']
        self.price_low = dct['price_low']
        self.bid_buy = dct['bid_buy']
        self.bid_sell = dct['bid_sell']
        self.deal_amount = dct['deal_amount']
        self.turnover = dct['turnover']
        self.buy_amount_1 = dct['buy_amount_1']
        self.buy_price_1 = dct['buy_price_1']
        self.buy_amount_2 = dct['buy_amount_2']
        self.buy_price_2 = dct['buy_price_2']
        self.buy_amount_3 = dct['buy_amount_3']
        self.buy_price_3 = dct['buy_price_3']
        self.buy_amount_4 = dct['buy_amount_4']
        self.buy_price_4 = dct['buy_price_4']
        self.buy_amount_5 = dct['buy_amount_5']
        self.buy_price_5 = dct['buy_price_5']
        self.sell_amount_1 = dct['sell_amount_1']
        self.sell_price_1 = dct['sell_price_1']
        self.sell_amount_2 = dct['sell_amount_2']
        self.sell_price_2 = dct['sell_price_2']
        self.sell_amount_3 = dct['sell_amount_3']
        self.sell_price_3 = dct['sell_price_3']
        self.sell_amount_4 = dct['sell_amount_4']
        self.sell_price_4 = dct['sell_price_4']
        self.sell_amount_5 = dct['sell_amount_5']
        self.sell_price_5 = dct['sell_price_5']
        self.trade_date = dct['trade_date']
        self.trade_time = dct['trade_time']

class CompanyInfoObj(object):
    def __init__(self,dct):
        self.stock_code = dct['stock_code']
        self.company_code = dct['company_code']
        self.company_name_full = dct['company_name_full']
        self.company_name = dct['company_name']
        self.region = dct['region']
        self.city = dct['city']
        self.register_address = dct['register_address']
        self.web = dct['web']
        self.profile = dct['profile']
        self.main_products = dct['main_products']
        self.business_scope = dct['business_scope']
        self.legal_represent = dct['legal_represent']
        self.chairman = dct['chairman']
        self.manager = dct['manager']

class StockPriceDayObj(object):
    def __init__(self,dct):
        self.stock_code = dct['stock_code']
        self.company_name = dct['company_name']
        self.time = dct['time']
        self.last_close = dct['last_close']
        self.open = dct['open']
        self.high = dct['high']
        self.low = dct['low']
        self.close = dct['close']
        self.before_open = dct['before_open']
        self.before_high = dct['before_high']
        self.before_low = dct['before_low']
        self.before_close = dct['before_close']
        self.after_open = dct['after_open']
        self.after_high = dct['after_high']
        self.after_low = dct['after_low']
        self.after_close = dct['after_close']
        self.volume = dct['volume']
        self.turnover = dct['turnover']
        self.change = dct['change']
        self.turn_rate = dct['turn_rate']

class CompanyAliasObj(object):
    def __init__(self,dct):
        # self.stock_code = dct['stock_code']
        self.company_code = dct['company_code']
        self.company_name = dct['company_name']
        self.other_name = dct['other_name']

class SubcompanyInfoObj(object):
    def __init__(self, dct):
        self.stock_code = dct['stock_code']
        self.company_code = dct['company_code']
        self.company_name = dct['company_name']
        self.sub_company_code = dct['sub_company_code']
        self.sub_company_name = dct['sub_company_name']
        self.industry_type = dct['industry_type']

class IndustryConceptObj(object):
    def __init__(self, dct):
        self.stock_code = dct['stock_code']
        self.company_code = dct['company_code']
        self.concept = dct['concept']
        self.industry = dct['industry']
        self.company_name = dct['company_name']

class ChairmanSupervisorObj(object):
    def __init__(self, dct):
        self.person_name = dct['person_name']
        self.post = dct['post']
        self.role = dct['role']
        self.degree = dct['degree']
        self.age = dct['age']

class StockHolderObj(object):
    def __init__(self, dct):
        self.stock_code = dct['stock_code']
        self.company_code = dct['company_code']
        self.shareholder_name = dct['shareholder_name']
        self.stock_num = dct['stock_num']
        self.stock_ratio = dct['stock_ratio']
        self.stock_type = dct['stock_type']
        self.shareholder_nature = dct['shareholder_nature']
        self.rank = dct['rank']

class IndustryDataObj(object):
    def __init__(self, dct):
        self.PUBKEYCODE = dct['PUBKEYCODE']
        self.PUBLISHNAME = dct['PUBLISHNAME']
        self.TRADEDATE = dct['TRADEDATE']
        self.CHG = dct['CHG']

class ConceptDataObj(object):
    def __init__(self, dct):
        self.PUBKEYCODE = dct['PUBKEYCODE']
        self.PUBLISHNAME = dct['PUBLISHNAME']
        self.TRADEDATE = dct['TRADEDATE']
        self.CHG = dct['CHG']

class MarketDataObj(object):
    def __init__(self, dct):
        self.stock_code = dct['stock_code']
        self.trade_date = dct['trade_date']
        self.raise_fall = dct['raise_fall']
        self.name = dct['name']

class EntityRoleObj(object):
    def __init__(self, dct):
        self.stock_code = dct['stock_code']
        self.company_code = dct['company_code']
        self.company_name = dct['company_name']
        self.role_type = dct['role_type']
        self.role_content = dct['role_content']

class FinancialInfoObj(object):
    def __init__(self, dct):
        self.stock_code = dct['stock_code']
        self.company_code = dct['company_code']
        self.debt_ratio = dct['debt_ratio']
        self.cash_flow_ratio = dct['cash_flow_ratio']
        self.goodwill_ratio = dct['goodwill_ratio']
        self.asset_income_ratio = dct['asset_income_ratio']
        self.flow_ratio = dct['flow_ratio']
        self.turnover_ratio = dct['turnover_ratio']
        self.profit_increase_ratio = dct['profit_increase_ratio']
        self.capital_increase_ratio = dct['capital_increase_ratio']
        self.equity_interest_debt_ratio = dct['equity_interest_debt_ratio']
        self.finance_cost_ratio = dct['finance_cost_ratio']
        self.capital_impairment_ratio = dct['capital_impairment_ratio']
        self.pre_account_ratio = dct['pre_account_ratio']
        self.net_assets_ratio = dct['net_assets_ratio']
        self.retain_income_ratio = dct['retain_income_ratio']
        self.debt_change_rate = dct['debt_change_rate']
        self.record_time = dct['record_time']

class TotalSharesObj(object):
    def __init__(self, dct):
        self.company_code = dct['company_code']
        self.total_shares = dct['total_shares']