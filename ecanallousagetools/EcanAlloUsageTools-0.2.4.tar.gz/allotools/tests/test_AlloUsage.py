# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 11:48:42 2018

@author: michaelek
"""
import os
from allotools import AlloUsage
import pandas as pd

pd.options.display.max_columns = 10

#################################
### Parameters

from_date = '2008-07-01'
to_date = '2010-06-30'
freq = 'A-JUN'
datasets = ['Allo', 'RestrAllo', 'MeteredAllo', 'MeteredRestrAllo', 'Usage']
cols = ['CatchmentName', 'WaterUse', 'Date']
site_filter = {'SwazName': ['Selwyn-Waimakariri']}
crc_filter = {'RecordNumber': ['CRC000354.3']}

base_dir = os.path.realpath(os.path.dirname(__file__))

####################################
### Run tests

def test_AlloUsage1():
    a1 = AlloUsage(from_date, to_date, site_filter=site_filter)
    combo_ts1 = a1.get_ts(datasets, 'A-JUN', cols)
    combo_ts2 = a1.get_ts(datasets, 'M', cols)
    a1.plot_group(freq, export_path=base_dir)
    a1.plot_stacked(freq, export_path=base_dir)

    assert (len(combo_ts1) == 73) & (len(combo_ts2) == 869)

def test_AlloUsage2():
    a2 = AlloUsage(from_date, to_date, crc_filter=crc_filter)
    combo_ts3 = a2.get_ts(datasets, freq, cols)

    assert (combo_ts3.SwAllo.sum() == 1480908) & (combo_ts3.SwUsage.sum() == 1017923)





































