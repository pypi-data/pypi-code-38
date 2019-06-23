# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 09:28:58 2019

@author: michaelek
"""
import pandas as pd
from lowflows import core
from lowflows import read_data as rd


#########################################
### Reporting functions


def site_summary_ts(from_date, to_date=None, ExtSiteID=None, SiteType=None, restr_category=None, only_active=True):
    """

    """
    ## Read data
    sites = core.sites(ExtSiteID=ExtSiteID).reset_index()
    min_max1 = core.min_max_trigs(ExtSiteID=ExtSiteID, only_active=only_active).reset_index()
    site_log1 = core.site_log_ts(from_date, to_date=to_date, ExtSiteID=ExtSiteID).reset_index()

    ## find min and max triggers
    grp1 = min_max1.groupby('ExtSiteID')
    min_loc = grp1['MinTrigger'].idxmin()
    max_loc = grp1['MaxTrigger'].idxmax()

    min_trig = min_max1.loc[min_loc].drop(['Month', 'MaxAllocation', 'MaxTrigger'], axis=1).copy()
    min_trig.rename(columns={'BandNumber': 'MinBandNumber'}, inplace=True)
    max_trig = min_max1.loc[max_loc].drop(['Month', 'MinAllocation', 'MinTrigger'], axis=1).copy()
    max_trig.rename(columns={'BandNumber': 'MaxBandNumber'}, inplace=True)

    min_max2 = pd.merge(min_trig, max_trig, on='ExtSiteID')

    ## Combine other tables
    min_max3 = pd.merge(sites, min_max2, on='ExtSiteID')
    min_max4 = pd.merge(min_max3, site_log1.drop('SourceReadLog', axis=1), on='ExtSiteID')

    ## Get OP Flag


    ## Assign restriction categories
    min_max4['RestrCategory'] = 'No'
    min_max4.loc[(min_max4['Measurement'] <= min_max4['MinTrigger']), 'RestrCategory'] = 'Full'
    min_max4.loc[(min_max4['flow'] < min_max4['max_trig']) & (min_max4['flow'] > min_max4['min_trig']), 'restr_category'] = 'Partial'
    min_max4.loc[min_max4.op_flag == 'NA', 'restr_category'] = 'Deactivated'
    min_max4.drop('op_flag', axis=1, inplace=True)


    ### Return
    return min_max4






