# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 16:40:35 2018

@author: michaelek
"""
import pandas as pd
from pdsql import mssql
from allotools import parameters as param
#import parameters as param

#########################################
### Functions


def rd_allo(from_date='1900-07-01', to_date='2020-06-30', where_in=None, include_hydroelectric=False):
    """
    Function to filter consents..

    Parameters
    ----------
    from_date : str
        The start date for the time series.
    to_date: str
        The end date for the time series.
    where_in : dict
        The keys should be the column names and the values should be a list of values on those columns.

    Returns
    -------
    DataFrame
        Allocation
    """
    ### allocation
    allo1 = mssql.rd_sql(param.crc_server, param.crc_database, param.allo_table, param.allo_cols, where_in=where_in)
    allo1 = allo1[allo1.ConsentStatus.isin(param.status_codes)].copy()
    if not include_hydroelectric:
        allo1 = allo1[allo1.WaterUse != 'hydroelectric']

    ### Time series filtering
    allo1.loc[:, 'ToDate'] = pd.to_datetime(allo1.loc[:, 'ToDate'], errors='coerce')
    allo1.loc[:, 'FromDate'] = pd.to_datetime(allo1.loc[:, 'FromDate'], errors='coerce')
#    allo1 = allo1[(allo1['ToDate'] - pd.Timestamp(from_date)).dt.days > 31]
#    allo1 = allo1[(pd.Timestamp(to_date) - allo2['FromDate']).dt.days > 31]
    allo1 = allo1[(allo1['ToDate'] - allo1['FromDate']).dt.days > 10]
    allo2 = allo1[(allo1.FromDate < to_date) & (allo1.ToDate > from_date)].copy()

    ### Index the DataFrame
    allo2.set_index(['RecordNumber', 'HydroFeature', 'AllocationBlock', 'ExtSiteID'], inplace=True)

    return allo2


def rd_sites(where_in=None):
    """
    where_in : dict
        The keys should be the column names and the values should be a list of values on those columns.
    """
    ### Site and attributes
    sites = mssql.rd_sql(param.hydro_server, param.hydro_database, param.site_table, param.site_cols, where_in=where_in)
    sites1 = sites[sites.ExtSiteID.str.contains('[A-Z]+\d\d/\d+')].copy()

    return sites1.set_index('ExtSiteID')
