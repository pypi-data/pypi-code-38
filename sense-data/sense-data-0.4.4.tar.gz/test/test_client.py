#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Copyright (C)2018 SenseDeal AI, Inc. All Rights _reserved
File: {name}.py
Author: xuwei
Email: weix@sensedeal.ai
Last modified: 2018.12.23
Description:
'''


from sense_data import SenseDataService
import sense_core as sd
sd.log_init_config('settings', sd.config('log_path'))

#1
def test_get_stock_price_tick():
    print(sd.config('data_rpc', 'host'))
    _xw = SenseDataService()
    _stock_code = '600892'
    _res = _xw.get_stock_price_tick(_stock_code)
    print(_res)
    print(_res.trade_date)
    print(_res.trade_time)
    print(_res.bid_buy)
    print(_res.bid_sell )
    print(_res.close_last)
#2
def test_get_stock_price_day():
    _xw = SenseDataService()
    _stock_code = '000002'
    _res = _xw.get_stock_price_day(_stock_code, '2019-5-21','2019-5-23')
    print(_res)
    # print(_res.company_name)
#3
def test_get_subcompany():
    _xw = SenseDataService()
    _stock_code = ['002195']
    _res = _xw.get_subcompany(_stock_code)
    print(_res)
    # print(_res[0].company_name)
#4
def test_get_company_info():
    _xw = SenseDataService()
    _stock_code = ['000045']
    _res = _xw.get_company_info(_stock_code)
    print(_res)
    print(_res.business_scope)
#5
def test_get_company_alias():
    _xw = SenseDataService()
    _stock_code = ['000045','000046']
    _res = _xw.get_company_alias(_stock_code)
    print(_res)
    # print(_res[0].other_name)
#6
def test_get_industry_concept():
    _xw = SenseDataService()
    _stock_code = ['000060']
    _res = _xw.get_industry_concept(_stock_code)
    print(_res.industry)
    print(_res.concept)
    # print(_res.company_name)
#7
def test_get_chairman_supervisor():
    _xw = SenseDataService()
    _stock_code = '000045'
    _res = _xw.get_chairman_supervisor(_stock_code)
    print(_res)
    # print(_res.company_name)
#8
def test_get_stockholder():
    _xw = SenseDataService()
    _stock_code = '000045'
    _res = _xw.get_stockholder(_stock_code)
    print(_res[0].shareholder_name)
    # print(_res.company_name)
#9
def test_get_trade_date():
    _xw = SenseDataService()
    _res = _xw.get_trade_date()
    print(_res)
#10
def test_get_market_rise_fall():
    _xw = SenseDataService()
    _res = _xw.get_market_rise_fall()
    print(_res)
#11
def test_get_industry_rise_fall():
    _xw = SenseDataService()
    _res = _xw.get_industry_rise_fall()
    print(_res)
#12
def test_get_concept_rise_fall():
    _xw = SenseDataService()
    _res = _xw.get_concept_rise_fall()
    print(_res)

#13
def test_get_entity_role():
    print(sd.config('data_rpc','host'))
    _entity_name = '庞升东'
    _xw = SenseDataService()
    _res = _xw.get_entity_role(_entity_name)
    print(_res[0].company_name)


#14
def test_get_financial_info():
    print(sd.config('data_rpc', 'host'))
    _xw = SenseDataService()
    _stock_code = ['002195']
    _res = _xw.get_financial_info(_stock_code)
    print(_res)
    print(_res.capital_increase_ratio)

    # for key in _res[0].keys():
    #     print('self.{}'.format(key) + ' = ' 'dct[' + "'" + key + "']")
    # print(_res.business_scope)

#15
def test_get_total_shares():
    _xw = SenseDataService()
    _stock_code = []
    _res = _xw.get_total_shares(_stock_code)
    # print(_res)
    # for key in _res[0].keys():
    #     print('self.{}'.format(key) + ' = ' 'dct[' + "'" + key + "']")
    print(_res[1].company_code)


#16
def test_get_company_name():
    _xw = SenseDataService()
    _res = _xw.get_company_name()
    print(_res)

# 17
def test_get_title_code():
    _xw = SenseDataService()
    _title = '沃格光电今天买进新大洲'
    _res = _xw.get_title_code(_title)
    print(_res)

#18
def test_get_actual_control_person():
    _xw = SenseDataService()
    _stock_code = ['000045']
    _res = _xw.get_actual_control_person(_stock_code)
    print(_res)
    # print(_res.business_scope)

