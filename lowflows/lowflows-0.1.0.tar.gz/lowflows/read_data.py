# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 11:37:13 2019

@author: michaelek
"""
import pandas as pd
from datetime import date
from pdsql.mssql import rd_sql
from lowflows import util


##########################################
### Parameters

## Lowflows
lf_server = 'sql2012prod03'
lf_db = 'lowflows'

# Internal site id, band, and min flow
min_flow_table = 'LowFlowSiteBandPeriodAllocation'

min_flow_fields = ['SiteID', 'BandNo', 'PeriodNo', 'Allocation', 'Flow']
min_flow_names = ['SiteID', 'BandNumber', 'Period', 'Allocation', 'trig_level']

# period info
period_table = 'LowFlowSiteBandPeriod'

period_fields = ['SiteID', 'BandNo', 'PeriodNo', 'fmDate', 'toDate']
period_names = ['SiteID', 'BandNumber', 'Period', 'from_date', 'to_date']

# site band active
site_type_table = 'LowFlowSiteBand'

site_type_fields = ['SiteID', 'BandNo', 'Description', 'RestrictionType', 'isActive']
site_type_names = ['SiteID', 'BandNumber', 'BandName', 'SiteType', 'IsActive']

# daily restrictions
restr_table = 'LowFlowSiteRestrictionDaily'

restr_fields = ['SiteID', 'BandNo', 'RestrictionDate', 'AsmtFlow', 'BandAllocation', 'SnapshotType']
restr_names = ['SiteID', 'BandNumber', 'RestrDate', 'Measurement', 'Allocation', 'SnapshotType']

# Sites info
lf_sites_table = 'LowFlowSite'

lf_sites_fields = ['SiteID', 'RefDBaseKey']
lf_sites_names = ['SiteID', 'ExtSiteID']

# crc, sites, and bands
crc_table = 'tagLowFlow'

crc_fields = ['SiteID', 'BandNo', 'RecordNo']
crc_names = ['SiteID', 'BandNumber', 'RecordNumber']

# RefDBase table
db_log_table = 'LowFlowSiteRefDBaseReadSite'

db_log_fields = ['forDate', 'SiteID', 'RefDBase', 'Result']
db_log_names = ['RestrDate', 'SiteID', 'SourceSystem', 'LogResult']

# Assessment table
ass_table = 'LowFlowSiteAssessment'

#ass_stmt_alt = "select SiteID, MethodID, Flow as Value, AppliesFromDate, MeasuredDate from LowFlows.dbo.LowFlowSiteAssessment t1 WHERE EXISTS(SELECT 1 FROM LowFlows.dbo.LowFlowSiteAssessment t2 WHERE t2.SiteID = t1.SiteID  and t2.MeasuredDate <= '{date}' GROUP BY t2.SiteID HAVING t1.MeasuredDate = MAX(t2.MeasuredDate))"
ass_stmt = "select SiteID, AppliesFromDate from LowFlows.dbo.LowFlowSiteAssessment t1 WHERE EXISTS(SELECT 1 FROM LowFlows.dbo.LowFlowSiteAssessment t2 WHERE t2.SiteID = t1.SiteID and t2.AppliesFromDate <= '{date}'{site} GROUP BY t2.SiteID HAVING t1.AppliesFromDate = MAX(t2.AppliesFromDate))"

ass_fields = ['SiteID', 'MethodID', 'AppliesFromDate', 'MeasuredDate', 'Flow', 'OP', 'Notes']

#ass_names = ['SiteID', 'MeasurementMethod', 'AppliesFromDate', 'MeasurementDate', 'Value', 'SourceReadLog']

ass_names = {'MethodID': 'MeasurementMethod', 'MeasuredDate': 'MeasurementDate', 'Flow': 'Measurement', 'Notes': 'SourceReadLog', 'OP': 'OPFlag'}


# Method dict
method_dict = {1: 'Manual Field', 2: 'Manual Visual', 3: 'Telemetered', 4: 'Manual Override', 5: 'Correlated from Telem'}

## Hydrotel
hydrotel_server = 'sql2012prod04'
hydrotel_db = 'hydrotel'

sites_tab = 'Sites'

sites_fields = ['Site', 'ExtSysID']

obj_tab = 'Objects'

obj_fields = ['Site', 'Name']

## USM

usm_server = 'sql2012prod03'
usm_db = 'USM'

usm_sites_table = 'Site'

usm_fields = ['UpstreamSiteID', 'Name', 'NZTMX', 'NZTMY']
usm_names = ['ExtSiteID', 'SiteName', 'NZTMX', 'NZTMY']


################################################
### Specific table reading functions


def usm_sites(ExtSiteID=None):
    """
    USM Site table.
    """
    where_in = util.where_gen(ExtSiteID, 'UpstreamSiteID')

    usm_sites1 = rd_sql(usm_server, usm_db, usm_sites_table, usm_fields, where_in=where_in, rename_cols=usm_names).round()

    return usm_sites1


def rd_lf_sites(SiteID=None, ExtSiteID=None):
    """
    LowFlowSite table.
    """
    where_in1 = util.where_gen(SiteID, 'SiteID')
    where_in = util.where_gen(ExtSiteID, 'RefDBaseKey', where_in1)

    sites = rd_sql(lf_server, lf_db, lf_sites_table, lf_sites_fields, where_in=where_in, rename_cols=lf_sites_names)

    ## Clean
    sites['ExtSiteID'] = sites['ExtSiteID'].str.upper()

    ## Return
    return sites


def rd_lf_min_flows(SiteID=None, BandNumber=None):
    """
    LowFlowSiteBandPeriodAllocation table.
    """
    where_in1 = util.where_gen(SiteID, 'SiteID')
    where_in = util.where_gen(BandNumber, 'BandNo', where_in1)

    restr_val = rd_sql(lf_server, lf_db, min_flow_table, min_flow_fields, where_in=where_in, rename_cols=min_flow_names)

    ## clean - Fix duplicate zero allocations at zero flow
    grp1 = restr_val.groupby(['SiteID', 'BandNumber', 'Period'])
    zeros1 = grp1.min()
    zeros2 = zeros1[zeros1.trig_level == 0]['Allocation']
    zeros3 = pd.merge(restr_val, zeros2.reset_index(), on=['SiteID', 'BandNumber', 'Period', 'Allocation'])
    max_zero = zeros3.groupby(['SiteID', 'BandNumber', 'Period', 'Allocation'])['trig_level'].max()

    all_trig = restr_val.groupby(['SiteID', 'BandNumber', 'Period', 'Allocation'])['trig_level'].min()

    all_trig[max_zero.index] = max_zero

    ## Return
    return all_trig


def rd_lf_periods(SiteID=None, BandNumber=None):
    """
    LowFlowSiteBandPeriod table.
    """
    where_in1 = util.where_gen(SiteID, 'SiteID')
    where_in = util.where_gen(BandNumber, 'BandNo', where_in1)

    periods = rd_sql(lf_server, lf_db, period_table, period_fields, where_in=where_in, rename_cols=period_names)

    ## Return
    return periods


def rd_lf_site_type(SiteID=None, BandNumber=None, SiteType=None, only_active=None):
    """
    LowFlowSiteBand table.
    """
    where_in1 = util.where_gen(SiteID, 'SiteID')
    where_in2 = util.where_gen(BandNumber, 'BandNo', where_in1)
    where_in3 = util.where_gen(only_active, 'isActive', where_in2)
    where_in = util.where_gen(SiteType, 'RestrictionType', where_in3)

    site_type = rd_sql(lf_server, lf_db, site_type_table, site_type_fields, where_in=where_in, rename_cols=site_type_names)

    ## clean
    site_type['BandName'] = site_type['BandName'].str.strip()
    site_type['SiteType'] = site_type['SiteType'].str.strip().str.title()

    ## Return
    return site_type.set_index(['SiteID', 'BandNumber']).sort_index()


def rd_lf_restr_ts(SiteID=None, BandNumber=None, from_date=None, to_date=None):
    """
    LowFlowSiteRestrictionDaily table.
    """
#    where_in1 = util.where_gen('Live', 'SnapshotType')
    where_in2 = util.where_gen(SiteID, 'SiteID')
    where_in = util.where_gen(BandNumber, 'BandNo', where_in2)

    restr_ts = rd_sql(lf_server, lf_db, restr_table, restr_fields, where_in=where_in, rename_cols=restr_names, from_date=from_date, to_date=to_date, date_col='RestrictionDate').sort_values('SnapshotType')

    ## clean
    restr_ts.drop_duplicates(['SiteID', 'BandNumber', 'RestrDate'], inplace=True)

    ## Return
    return restr_ts.drop('SnapshotType', axis=1).set_index(['SiteID', 'BandNumber', 'RestrDate']).sort_index()


def rd_lf_crc(SiteID=None, BandNumber=None, RecordNumber=None):
    """
    tagLowFlow table.
    """
    where_in1 = util.where_gen(SiteID, 'SiteID')
    where_in2 = util.where_gen(BandNumber, 'BandNo', where_in1)
    where_in = util.where_gen(RecordNumber, 'RecordNo', where_in2)

    crc = rd_sql(lf_server, lf_db, crc_table, crc_fields, where_in=where_in, rename_cols=crc_names)

    ## clean
    crc['RecordNumber'] = crc['RecordNumber'].str.strip().str.upper()
    crc1 = crc.drop_duplicates()

    ## Return
    return crc1


def rd_lf_db_log(SiteID=None, from_date=None, to_date=None, LogResult=None):
    """
    LowFlowSiteRefDBaseReadSite table.
    """
    if to_date is None:
        to_date = str(date.today())

    where_in1 = util.where_gen(SiteID, 'SiteID')
    where_in = util.where_gen(LogResult, 'Result', where_in1)

    db_log = rd_sql(lf_server, lf_db, db_log_table, db_log_fields, where_in=where_in, from_date=from_date, to_date=to_date, date_col='forDate', rename_cols=db_log_names).drop_duplicates(['SiteID', 'RestrDate'])

    ## Return
    return db_log.set_index(['SiteID', 'RestrDate']).sort_index()


def rd_lf_last_reading_from_date(from_date, SiteID=None):
    """
    """
    if SiteID is None:
        site_str = ''
    elif isinstance(SiteID, (str, int)):
        site_str = ' and SiteID = ' + str(SiteID)
    elif isinstance(SiteID, list):
        site_str = ' and SiteID in ({})'.format(', '.join([str(i) for i in SiteID]))

    stmt1 = ass_stmt.format(date=from_date, site=site_str)
    df1 = rd_sql(lf_server, lf_db, stmt=stmt1)

    return df1


def rd_lf_last_readings_ts(from_date, to_date=None, SiteID=None):
    """
    LowFlowSiteAssessment table
    """
    if to_date is None:
        to_date = str(date.today())

    dates1 = pd.date_range(from_date, to_date)

    list1 = []
    for d in dates1:
        df1 = rd_lf_last_reading_from_date(d, SiteID)
        df1['RestrDate'] = d
        list1.append(df1)
    df2 = pd.concat(list1)
    if df2.empty:
        return None
    dates2 = df2.AppliesFromDate.astype(str).unique().tolist()

    where_in1 = util.where_gen(SiteID, 'SiteID')
    where_in = util.where_gen(dates2, 'AppliesFromDate', where_in1)

    df3 = rd_sql(lf_server, lf_db, ass_table, ass_fields, where_in=where_in)

    df4 = pd.merge(df2, df3, on=['SiteID', 'AppliesFromDate'], how='left')

    # Rename
    ass1 = df4.rename(columns=ass_names)

    # Clean
    ass1.loc[:, 'SourceReadLog'] = ass1.loc[:, 'SourceReadLog'].str.strip().str[:150]
    ass1['MeasurementDate'] = pd.to_datetime(ass1['MeasurementDate'].dt.date)
    ass1['OPFlag'] = ass1['OPFlag'].str.strip().str.upper()

    ## Add in how it was measured and when
    sites = rd_lf_sites(SiteID)

    tel_sites1 = ass1[ass1.MeasurementMethod == 3].SiteID
    if not tel_sites1.empty:
        tel_sites2 = sites.loc[sites.SiteID.isin(tel_sites1), 'ExtSiteID']
        corr_sites1 = telem_corr_sites(tel_sites2.tolist())
        corr_sites2 = sites.loc[sites.ExtSiteID.isin(corr_sites1), 'SiteID']
        ass1.loc[ass1.SiteID.isin(corr_sites2), 'MeasurementMethod'] = 5

    site_type2 = ass1.replace({'MeasurementMethod': method_dict}).set_index(['SiteID', 'RestrDate']).sort_index()

    return site_type2


def telem_corr_sites(site_num=None):
    """
    Function to determine if sites are telemetered or are correlated from telemetered sites in Hydrotel. Output is a list of correlated sites.

    Parameters
    ----------
    site_num: list of str
        Site numbers for the selection.

    Returns
    -------
    List of str
        List of site numbers that are correlated sites.
    """
    ### Parameters
    sites_tab = 'Sites'
    obj_tab = 'Objects'

    sites_fields = ['Site', 'ExtSysID']
    obj_fields = ['Site', 'Name']

    where_dict = {'Name': ['calculated flow']}

    ### Read in data
    if isinstance(site_num, list):
        sites = rd_sql(hydrotel_server, hydrotel_db, sites_tab, sites_fields, {'ExtSysID': site_num})
        sites['ExtSysID'] = pd.to_numeric(sites['ExtSysID'], 'coerce')
    else:
        sites = rd_sql(hydrotel_server, hydrotel_db, sites_tab, sites_fields)
        sites['ExtSysID'] = pd.to_numeric(sites['ExtSysID'], 'coerce')
        sites = sites[sites.ExtSysID.notnull()]

    sites['Site'] = sites['Site'].astype('int32')

    where_dict.update({'Site': sites.Site.tolist()})

    obj = rd_sql(hydrotel_server, hydrotel_db, obj_tab, obj_fields, where_dict)
    corr_sites = sites[sites.Site.isin(obj.Site)]

    return corr_sites.ExtSysID.astype('int32').astype(str).tolist()

