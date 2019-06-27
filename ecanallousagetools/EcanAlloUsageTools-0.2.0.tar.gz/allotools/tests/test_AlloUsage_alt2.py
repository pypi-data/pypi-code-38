# -*- coding: utf-8 -*-
"""
Created on Mon Feb 18 09:13:34 2019

@author: michaelek
"""
import os
from allotools import AlloUsage
from pdsql import mssql
import pandas as pd

pd.options.display.max_columns = 10


#######################################
### Parameters

server = 'edwprod01'
database = 'hydro'
sites_table = 'ExternalSite'

catch_group = ['Ashburton River']
summ_col = 'SwazName'

waitaki = {'CatchmentGroupName': ['Waitaki']}

crc_filter = {'use_type': ['stockwater', 'irrigation']}

from_date = '2015-07-01'
to_date = '2018-06-30'

datasets = ['Allo', 'RestrAllo', 'MeteredAllo', 'MeteredRestrAllo', 'Usage']
datasets = ['Allo', 'MeteredAllo', 'Usage']

freq = 'A-JUN'
#freq = 'M'

t1 = 'CRC012123'
t2 = 'Pendarves Area'

t3 = 'CRC011245'

cols = ['SwazName', 'WaterUse', 'Date']

export_path = r'E:\ecan\local\Projects\requests\Ilja\2019-02-27'


########################################
### Test 1
sites1 = mssql.rd_sql(server, database, sites_table, ['ExtSiteID', 'CatchmentGroupName', summ_col], where_in={'CatchmentGroupName': catch_group})

site_filter = {'SwazName': sites1.SwazName.unique().tolist()}

a1 = AlloUsage(from_date, to_date, site_filter=site_filter, crc_filter=crc_filter)

allo_ts1 = a1._get_allo_ts(freq, groupby=['crc', 'date'])

metered_allo_ts1 = a1._get_metered_allo_ts(freq, ['crc', 'date'])

usage1 = a1._get_usage_ts(freq, ['crc', 'date'])

a1._lowflow_data(freq)

restr_allo = a1._get_restr_allo_ts(freq, ['crc', 'wap', 'date'])

combo_ts1 = a1.get_ts(datasets, freq, ['date'])
combo_ts2 = a1.get_ts(datasets, freq, ['date'], irr_season=True)

combo_ts1.resample('A-JUN').sum().round(-4)
combo_ts2.resample('A-JUN').sum().round(-4)

### Test 2
a1 = AlloUsage(from_date, to_date)

combo_ts = a1.get_ts(datasets, freq, ['date'])

a1 = AlloUsage(from_date, to_date, crc_filter={'crc': ['CRC157373']})

a1 = AlloUsage(from_date, to_date, crc_filter={'crc': ['CRC182351']})
combo_ts = a1.get_combo_ts(datasets, freq, ['date'])


### Test3
a1 = AlloUsage(from_date, to_date, crc_filter={'RecordNumber': [t3]})

combo_ts1 = a1.get_ts(datasets, freq, cols)
combo_ts2 = a1.get_ts(datasets, freq, ['date'], irr_season=True)

c1 = combo_ts1.resample('A-JUN').sum().round(-4)[['total_allo', 'total_metered_allo', 'total_restr_allo', 'total_metered_restr_allo', 'total_usage']]
c2 = combo_ts2.resample('A-JUN').sum().round(-4)[['total_allo', 'total_metered_allo', 'total_restr_allo', 'total_metered_restr_allo', 'total_usage']]

c1['total_restr_allo']/c1['total_allo']
c2['total_restr_allo']/c2['total_allo']


combo_ts3 = a1.get_ts(datasets, 'A-JUN', ['date'], irr_season=True)[['total_allo', 'total_metered_allo', 'total_restr_allo', 'total_metered_restr_allo', 'total_usage']].round(-4)

### Test 4
sites1 = mssql.rd_sql(server, database, sites_table, ['ExtSiteID', 'CatchmentGroupName', summ_col], where_in={'CatchmentGroupName': catch_group})

site_filter = {'SwazName': sites1.SwazName.unique().tolist()}

a1 = AlloUsage(from_date, to_date, site_filter=site_filter)

ts1 = a1.get_ts(datasets, freq, cols, irr_season=True)

a1.plot_group('A-JUN', val='total', with_restr=True, export_path=r'E:\ecan\local\Projects\requests\suz\2018-12-17\plots')

a1.plot_stacked('A-JUN', val='total', export_path=r'E:\ecan\local\Projects\requests\suz\2018-12-17\plots')

### Test 5
a1 = AlloUsage(from_date, to_date, site_filter=waitaki)

a1.allo.to_csv(os.path.join(export_path, 'waitaki_allo_2019-02-27.csv'))

a1.allo_wap.to_csv(os.path.join(export_path, 'waitaki_allo_wap_2019-02-27.csv'))




a1 = AlloUsage(from_date, to_date, site_filter={'CatchmentGroupName': ['Waitaki']})
self = a1
a1.freq = freq






