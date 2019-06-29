# -*- coding: utf-8 -*-
"""
Created on Mon Feb 18 09:13:34 2019

@author: michaelek
"""
import os
import pandas as pd
from allotools import AlloUsage
#from pdsql import mssql

pd.options.display.max_columns = 10

date1 = pd.Timestamp.now()
date2 = date1.strftime('%Y%m%d%H%M')

#######################################
### Parameters

test_sites_csv = 'TestSitesDataQuality.csv'

from_date = '2015-07-01'
to_date = '2018-06-30'

datasets = ['allo', 'restr_allo', 'metered_allo', 'metered_restr_allo', 'usage']
datasets = ['allo', 'metered_allo', 'usage']

freq = 'A-JUN'

cols = ['crc', 'wap', 'date']

export_path = r'E:\ecan\local\Projects\requests\Ilja\2019-02-26'
export1 = 'test_crcs_{}.csv'.format(date2)

########################################
### Read in sites

test_crc = pd.read_csv(test_sites_csv).crc.unique().tolist()

########################################
### generate!


#sites1 = mssql.rd_sql(server, database, sites_table, ['ExtSiteID', 'CatchmentGroupName', summ_col], where_in={'CatchmentGroupName': catch_group})
#
#site_filter = {'SwazName': sites1.SwazName.unique().tolist()}

a1 = AlloUsage(from_date, to_date, crc_filter={'crc': test_crc})

ts1 = a1.get_ts(datasets, freq, cols, usage_allo_ratio=10).round()

ts1.to_csv(os.path.join(export_path, export1))

a1.plot_group('A-JUN', val='total', group='crc', with_restr=False, export_path=export_path)

a1.plot_stacked('A-JUN', val='total', export_path=r'E:\ecan\local\Projects\requests\suz\2018-12-17\plots')

















