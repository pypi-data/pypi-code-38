# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 11:48:42 2018

@author: michaelek
"""
from allotools import allo_ts, allo_filter

#################################
### Parameters

server = 'sql2012test01'

from_date = '1998-07-01'
to_date = '2003-06-30'
freq = 'A-JUN'
restr_type = 'annual volume'
remove_months=False
site_filter = {'SwazName': ['Selwyn-Waimakariri']}

####################################
### Run tests

def test_allo_filter():
    sites, allo, allo_wap = allo_filter(server, from_date, to_date, site_filter=site_filter)

    assert (len(sites) > 1000) and (len(allo) > 1400) and (len(allo_wap) > 1500)

def test_allo_ts():
    ts_allo = allo_ts(server, from_date, to_date, freq, restr_type, site_filter=site_filter)

    assert len(ts_allo) > 5000








































