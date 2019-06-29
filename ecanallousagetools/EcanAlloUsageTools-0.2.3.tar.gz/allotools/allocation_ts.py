# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 09:55:07 2018

@author: michaelek
"""
import numpy as np
import pandas as pd

###################################
### Functions


def allo_ts_apply(row, from_date, to_date, freq, restr_col, remove_months=True):
    """
    Pandas apply function that converts the allocation data to a monthly time series.
    """

    crc_from_date = pd.Timestamp(row['FromDate'])
    crc_to_date = pd.Timestamp(row['ToDate'])
    start = pd.Timestamp(from_date)
    end = pd.Timestamp(to_date)

    if crc_from_date > start:
        start = crc_from_date
    if crc_to_date < end:
        end = crc_to_date

    end_date = end - pd.DateOffset(hours=1) + pd.tseries.frequencies.to_offset(freq)
    dates1 = pd.date_range(start, end_date, freq=freq)
    if remove_months and ('A' not in freq):
        mon1 = np.arange(row['FromMonth'], 13)
        mon2 = np.arange(1, row['ToMonth'] + 1)
        in_mons = np.concatenate((mon1, mon2))
        dates2 = dates1[dates1.month.isin(in_mons)].copy()
    else:
        dates2 = dates1.copy()

    if dates2.empty:
        return None

    if freq == 'D':
        val1 = 1
    elif freq == 'W':
        val1 = 7
    elif freq == 'M':
        val1 = dates1.daysinmonth.values
    else:
        val1 = dates1.dayofyear.values + 184

    s1 = pd.Series(val1, index=dates1, name='allo')
    s1.loc[~s1.index.isin(dates2)] = 0

    if freq in ['A-JUN', 'D', 'W']:
        vol1 = s1.copy()
        vol1[:] = row[restr_col]
    elif 'M' in freq:
        year1 = s1.resample('A-JUN').transform('sum')
        vol1 = s1/year1 * row[restr_col]
    else:
        raise ValueError("freq must be either 'A-JUN', 'M', 'W', or 'D'")

    alt_dates = s1.values.copy()
    if len(s1) == 1:
        alt_dates[0] = s1[0] - (dates2[-1] - end).days - (s1[0] - (dates2[0] - start).days)
    else:
        start_diff = (dates2[0] - start).days + 1
        if start_diff < s1[0]:
            alt_dates[0] = start_diff
        end_diff = s1[-1] - (dates2[-1] - end).days
        if end_diff < s1[-1]:
            alt_dates[-1] = end_diff
    ratio_days = alt_dates/s1

    vols = (ratio_days * vol1).round().fillna(0)

    return vols


#def allo_ts(server, from_date, to_date, freq, restr_type, site_filter=None, crc_filter=None, crc_wap_filter=None, remove_months=False, in_allo=True):
#    """
#    Combo function to completely create a time series from the allocation DataFrame. Source data must be from an instance of the Hydro db.
#
#    Parameters
#    ----------
#    server : str
#        The server where the Hydro db lays.
#    from_date : str
#        The start date for the time series.
#    to_date: str
#        The end date for the time series.
#    freq : str
#        Pandas frequency str. Must be 'D', 'W', 'M', or 'A-JUN'.
#    restr_type : str
#        The allocation rate/volume used as the values in the time series. Must be 'max rate', 'daily volume', or 'annual volume'.
#    remove_months : bool
#        Should the months that are defined in the consent only be returned?
#    in_allo : bool
#        Should the consumptive consents be returned?
#
#    Returns
#    -------
#    Series
#        indexed by crc, take_type, and allo_block
#    """
#
#    if restr_type not in param.restr_type_dict:
#        raise ValueError('restr_type must be one of ' + str(list(param.restr_type_dict.keys())))
#    if freq not in param.freq_codes:
#        raise ValueError('freq must be one of ' + str(param.freq_codes))
#
#    sites, allo2, wap_allo = allo_filter(server, from_date=from_date, to_date=to_date, site_filter=site_filter, crc_filter=crc_filter, crc_wap_filter=crc_wap_filter, in_allo=in_allo)
#
#    restr_col = param.restr_type_dict[restr_type]
#
#    allo3 = allo2.apply(allo_ts_apply, axis=1, from_date=from_date, to_date=to_date, freq=freq, restr_col=restr_col, remove_months=remove_months)
#
#    allo4 = allo3.stack()
#    allo4.index.set_names(['crc', 'take_type', 'allo_block', 'date'], inplace=True)
#    allo4.name = 'allo'
#
#    return allo4





