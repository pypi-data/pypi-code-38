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


def site_summary_ts(from_date, to_date=None, ExtSiteID=None, SiteType=None, only_active=True):
    """
    Function to provide a site summary time series.

    Parameters
    ----------
    from_date: str
        The start date for the log.
    to_date: str or None
        The end date for the log. None returns today's date.
    ExtSiteID: int, str, or list
        ECan site IDs
    SiteType: str or list of str
        Options are 'Lowflow' or 'Residual'
    only_active: bool or None
        Should only the active bands be returned? None will contain all.

    Returns
    -------
    DataFrame
        ['ExtSiteID', 'RestrDate']
    """
    ## Read data
    sites = core.sites(ExtSiteID=ExtSiteID).reset_index()
    site_link = rd.rd_lf_sites(ExtSiteID=ExtSiteID)
    min_max1 = core.min_max_trigs(ExtSiteID=ExtSiteID, only_active=only_active).reset_index()
    site_log1 = core.site_log_ts(from_date, to_date=to_date, ExtSiteID=ExtSiteID).reset_index()
    site_types = rd.rd_lf_site_type(SiteType=SiteType, only_active=only_active).reset_index()

    ## Determine site type by site
    site_types1 = site_types.sort_values('SiteType').drop_duplicates('SiteID')[['SiteID', 'SiteType']]
    band_count = site_types.groupby('SiteID')['BandNumber'].count()
    band_count.name = 'BandCount'
    site_types2 = pd.merge(site_types1, band_count.reset_index(), on='SiteID')

    # Convert SiteIDs
    site_types3 = pd.merge(site_link, site_types2, on='SiteID').drop('SiteID', axis=1)

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
    min_max3a = pd.merge(min_max3, site_types3, on='ExtSiteID')
    min_max4 = pd.merge(min_max3a, site_log1.drop('SourceReadLog', axis=1), on='ExtSiteID')

    ## Assign restriction categories
    min_max4['RestrCategory'] = 'No'
    min_max4.loc[(min_max4['Measurement'] <= min_max4['MinTrigger']), 'RestrCategory'] = 'Full'
    min_max4.loc[(min_max4['Measurement'] < min_max4['MaxTrigger']) & (min_max4['Measurement'] > min_max4['MinTrigger']), 'RestrCategory'] = 'Partial'
    min_max4.loc[min_max4.OPFlag == 'NA', 'RestrCategory'] = 'Deactivated'
    min_max4.drop('OPFlag', axis=1, inplace=True)

    ### Return
    return min_max4.set_index(['ExtSiteID', 'RestrDate']).sort_index()






