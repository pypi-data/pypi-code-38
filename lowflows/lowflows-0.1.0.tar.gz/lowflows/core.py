# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 13:39:50 2018

@author: michaelek
"""
import numpy as np
import pandas as pd
from lowflows import read_data as rd
#import read_data as rd

###########################################
### Special functions


def min_max_trigs(ExtSiteID=None, only_active=None):
    """
    Function to determine the min/max triggers.

    Parameters
    ----------
    ExtSiteID: list of str
        ECan site IDs.
    only_active: bool
        Should the output only return active sites/bands?

    Returns
    -------
    DataFrames
        Outputs two DataFrames. The first includes the min and max triggger levels for all bands per site, while the second has the min and max trigger levels for each site and band.
    """
    ########################################
    ### Read in data

    sites1 = rd.rd_lf_sites(ExtSiteID=ExtSiteID)

    periods0 = rd.rd_lf_periods()

    all_trig = rd.rd_lf_min_flows()

    site_type = rd.rd_lf_site_type(only_active=only_active)

    #######################################
    ### Process data

    ## Periods by month
    periods = pd.merge(periods0, site_type, on=['SiteID', 'BandNumber'])

    periods['from_mon'] = periods['from_date'].dt.month
    periods['to_mon'] = periods['to_date'].dt.month

    ## filter by ExtSiteIDs
    periods = periods[periods.SiteID.isin(sites1.SiteID)]

    ## Process dates
    new1_list = []
    for group in periods.itertuples():
        if group.from_mon > group.to_mon:
            first1 = np.arange(group.from_mon, 13).tolist()
            sec1 = np.arange(1, group.to_mon + 1).tolist()
            first1.extend(sec1)
        else:
            first1 = np.arange(group.from_mon, group.to_mon + 1).tolist()

        index1 = [[group.SiteID, group.BandNumber, group.Period]] * len(first1)
        new1 = pd.DataFrame(index1, columns=['SiteID', 'BandNumber', 'Period'])
        new1['Month'] = first1

        new1_list.append(new1)

    periods1 = pd.concat(new1_list).drop_duplicates(['SiteID', 'BandNumber', 'Month'])

    periods1a = pd.merge(periods1, all_trig.reset_index(), on=['SiteID', 'BandNumber', 'Period']).drop('Period', axis=1)
    periods2 = pd.merge(periods1a, sites1, on='SiteID').drop('SiteID', axis=1)

    p_min = periods2[~periods2.Allocation.isin([103, 105, 106, 107, 108, 109])].groupby(['ExtSiteID', 'BandNumber', 'Month']).min()
    p_min.columns = ['MinAllocation', 'MinTrigger']
    p_max = periods2.groupby(['ExtSiteID', 'BandNumber', 'Month']).max()
    p_max.columns = ['MaxAllocation', 'MaxTrigger']

#    p_min_site = p_min.reset_index().groupby(['ExtSiteID', 'mon'])['min_trig'].min()
#    p_max_site = p_max.reset_index().groupby(['ExtSiteID', 'mon'])['max_trig'].max()
#    p_set_site = pd.concat([p_min_site, p_max_site], axis=1).reset_index()

    p_set = pd.concat([p_min, p_max], axis=1)

    return p_set


##################################
### Main functions


def sites(SiteID=None, ExtSiteID=None):
    """
    Function to get the site info for the lowflows sites that correspond in USM.

    Parameters
    ----------
    SiteID: int, str, or list
        LowFlow internal site IDs.
    ExtSiteID: int, str, or list
        ECan site IDs

    Returns
    -------
    DataFrame
        'ExtSiteID'
    """
    lf_sites = rd.rd_lf_sites(SiteID, ExtSiteID)
    usm_sites1 = rd.usm_sites(lf_sites.ExtSiteID.tolist())

    return usm_sites1.set_index('ExtSiteID')


def crc_trigs(SiteID=None, ExtSiteID=None, BandNumber=None, RecordNumber=None, SiteType=None, only_active=None):
    """
    Function to Determine the min and max trigger and allocations by the RecordNumber, BandNumber, and ExtSiteID.

    Parameters
    ----------
    SiteID: int, str, or list
        Lowflow internal site IDs.
    ExtSiteID: int, str, or list
        ECan site IDs
    BandNumber: int or list of int
        The Lowflow internal band numbers.
    RecordNumber: str or list of str
        The ECan record numbers.
    SiteType: str or list of str
        Options are 'Lowflow' or 'Residual'
    only_active: bool or None
        Should only the active bands be returned? None will contain all.

    Returns
    -------
    DataFrame
    """
    ### Read in tables
    crc = rd.rd_lf_crc(SiteID=SiteID, BandNumber=BandNumber, RecordNumber=RecordNumber)
    min_max = min_max_trigs(ExtSiteID=ExtSiteID, only_active=only_active).reset_index()
    sites = rd.rd_lf_sites(SiteID=SiteID, ExtSiteID=ExtSiteID)
    site_types = rd.rd_lf_site_type(SiteID=SiteID, BandNumber=BandNumber, SiteType=SiteType, only_active=only_active).reset_index()

    ### process min-max
    min_max2 = min_max.groupby(['ExtSiteID', 'BandNumber'])
    min1 = min_max2[['MinAllocation', 'MinTrigger']].min()
    max1 = min_max2[['MaxAllocation', 'MaxTrigger']].max()
    min_max3 = pd.concat([min1, max1], axis=1).reset_index()

    ## clean
    min_max3.loc[min_max3.MaxAllocation < 100, 'MaxAllocation'] = 100
    min_max3.loc[min_max3.MinAllocation == 100, 'MinAllocation'] = min_max3.loc[min_max3.MinAllocation == 100, 'MaxAllocation']
    min_max3.loc[(min_max3.MaxAllocation > 100) & (min_max3.MinAllocation < 100), 'MinAllocation'] = min_max3.loc[(min_max3.MaxAllocation > 100) & (min_max3.MinAllocation < 100), 'MaxAllocation']
    min_max3['MinTrigger'] = min_max3['MinTrigger'].round(2)
    min_max3['MaxTrigger'] = min_max3['MaxTrigger'].round(2)

#    min_max3[min_max3.MaxAllocation < 100].to_csv('max_allo_under_100.csv', index=False)
#    min_max3[min_max3.MinAllocation == 100].to_csv('min_allo_equals_100.csv', index=False)
#    min_max3.loc[(min_max3.MaxAllocation > 100) & (min_max3.MinAllocation < 100)].to_csv('min_allo_less_than_100.csv', index=False)

    ### Merges
    crc_sites = pd.merge(sites, crc, on='SiteID').drop('SiteID', axis=1)
    site_types2 = pd.merge(sites, site_types, on='SiteID').drop('SiteID', axis=1)
    min_max4 = pd.merge(crc_sites, min_max3, on=['ExtSiteID', 'BandNumber'])
    min_max5 = pd.merge(min_max4, site_types2, on=['ExtSiteID', 'BandNumber'])

    ### Return
    return min_max5.set_index(['RecordNumber', 'BandNumber', 'ExtSiteID'])


def site_log_ts(from_date, to_date=None, SiteID=None, ExtSiteID=None):
    """
    Function to return a time series log of site measurements read by Lowflows to the source systems.

    Parameters
    ----------
    from_date: str
        The start date for the log.
    to_date: str or None
        The end date for the log. None returns today's date.
    SiteID: int, str, or list
        LowFlow internal site IDs.
    ExtSiteID: int, str, or list
        ECan site IDs

    Returns
    -------
    DataFrame
        ['ExtSiteID', 'RestrDate']
    """
    ### Read in tables
    site_log1 = rd.rd_lf_db_log(SiteID=SiteID, from_date=from_date, to_date=to_date)
    sites = rd.rd_lf_sites(SiteID=SiteID, ExtSiteID=ExtSiteID)
    method1 = rd.rd_lf_last_readings_ts(from_date, to_date, SiteID)

    ### Combine tables
    method2 = pd.concat([method1, site_log1.drop('LogResult', axis=1)], axis=1, join='inner').reset_index()
    site_ts = pd.merge(sites, method2, on='SiteID').drop('SiteID', axis=1)

    ### Return
    return site_ts.set_index(['ExtSiteID', 'RestrDate'])


def allocation_ts(from_date, to_date=None, ExtSiteID=None, BandNumber=None, RecordNumber=None):
    """
    Function to return a time series of allocation restrictions by 'RecordNumber', 'BandNumber', 'ExtSiteID', and 'RestrDate'.

    Parameters
    ----------
    from_date: str
        The start date for the log.
    to_date: str or None
        The end date for the log. None returns today's date.
    SiteID: int, str, or list
        LowFlow internal site IDs.
    ExtSiteID: int, str, or list
        ECan site IDs
    BandNumber: int or list of int
        The Lowflow internal band numbers.
    RecordNumber: str or list of str
        The ECan record numbers.

    Returns
    -------
    DataFrame
        ['RecordNumber', 'BandNumber', 'ExtSiteID', 'RestrDate']
    """
    ## Read tables
    sites1 = rd.rd_lf_sites(ExtSiteID=ExtSiteID)
    crc1 = rd.rd_lf_crc(BandNumber=BandNumber, RecordNumber=RecordNumber)

    if ExtSiteID is not None:
        SiteID = sites1.SiteID.unique().tolist()
    else:
        SiteID = None
    restr_ts = rd.rd_lf_restr_ts(SiteID, BandNumber=BandNumber, from_date=from_date, to_date=to_date).drop('Measurement', axis=1).reset_index()

    ## Combine tables
    restr_crc1 = pd.merge(crc1, restr_ts, on=['SiteID', 'BandNumber']).drop_duplicates(['SiteID', 'BandNumber', 'RecordNumber', 'RestrDate'], keep='last')
    restr_crc2 = pd.merge(sites1, restr_crc1, on='SiteID').drop('SiteID', axis=1)

    ## Return
    return restr_crc2.set_index(['RecordNumber', 'BandNumber', 'ExtSiteID', 'RestrDate'])

