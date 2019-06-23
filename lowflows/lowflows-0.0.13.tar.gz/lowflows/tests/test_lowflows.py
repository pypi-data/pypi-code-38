# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 11:50:50 2019

@author: michaelek
"""
import pandas as pd
import lowflows as lf

pd.options.display.max_columns = 10

##############################################
### Parameters

ExtSiteID = ['270', '66213']
from_date = '2019-06-15'
to_date = '2019-06-20'

##############################################
### Tests


def test_sites():
    sites1 = lf.sites(ExtSiteID=ExtSiteID)
    assert len(sites1) == 2

def test_crc_trigs():
    trigs1 = lf.crc_trigs(ExtSiteID=ExtSiteID)
    assert len(trigs1) > 10

def test_site_log_ts():
    site_log1 = lf.site_log_ts(from_date, to_date, ExtSiteID=ExtSiteID)
    assert len(site_log1) == 12

def test_allocation_ts():
    allo1 = lf.allocation_ts(from_date, to_date, ExtSiteID=ExtSiteID)
    assert len(allo1) == 180

def test_site_summary_ts():
    site_summ1 = lf.site_summary_ts(from_date, to_date, ExtSiteID=ExtSiteID)
    assert len(site_summ1) == 12

