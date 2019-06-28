# -*- coding: utf-8 -*-
"""
Created on Sat Feb 16 09:50:42 2019

@author: michaelek
"""
import numpy as np
import pandas as pd
from pdsql import mssql
from allotools import filters
#import filters
from allotools.allocation_ts import allo_ts_apply
#from allocation_ts import allo_ts_apply
from allotools.plot import plot_group as pg
from allotools.plot import plot_stacked as ps
from allotools import parameters as param
#import parameters as param
from datetime import datetime
from allotools import util

########################################
### Core class


class AlloUsage(object):
    """
    Class to to process the allocation and usage data at ECan.

    Parameters
    ----------
    from_date : str or None
        The start date of the consent and the final time series. In the form of '2000-01-01'. None will return all consents and subsequently all dates.
    to_date : str or None
        The end date of the consent and the final time series. In the form of '2000-01-01'. None will return all consents and subsequently all dates.
    site_filter : dict
        A dict in the form of {str: [values]} to select specific values from a specific column in the ExternalSite table.
    crc_filter : dict
        A dict in the form of {str: [values]} to select specific values from a specific column in the CrcAllo table.
    crc_wap_filter : dict
        A dict in the form of {str: [values]} to select specific values from a specific column in the CrcWapAllo table.
    in_allo : bool
        Should only the consumptive takes be included?
    include_hydroelectric : bool
        Should hydroelectric takes be included?

    Returns
    -------
    AlloUsage object
        with all of the base sites, allo, and allo_wap DataFrames

    """

    dataset_types = param.dataset_types
    plot_group = pg
    plot_stacked = ps
    ts_server = param.hydro_server
    ts_db = param.hydro_database
    crc_server = param.crc_server
    crc_db = param.crc_database


    ### Initial import and assignment function
    def __init__(self, from_date='1900-07-01', to_date='2020-06-30', site_filter=None, crc_filter=None, include_hydroelectric=False):
        """

        Parameters
        ----------
        from_date : str or None
            The start date of the consent and the final time series. In the form of '2000-01-01'. None will return all consents and subsequently all dates.
        to_date : str or None
            The end date of the consent and the final time series. In the form of '2000-01-01'. None will return all consents and subsequently all dates.
        site_filter : dict
            A dict in the form of {str: [values]} to select specific values from a specific column in the ExternalSite table.
        crc_filter : dict
            A dict in the form of {str: [values]} to select specific values from a specific column in the CrcAllo table.
        include_hydroelectric : bool
            Should hydroelectric takes be included?

        Returns
        -------
        AlloUsage object
            with all of the base sites, allo, and allo_wap DataFrames

        """
        allo1 = filters.rd_allo(from_date, to_date, crc_filter, include_hydroelectric).reset_index()
        allo1.FromMonth = allo1.FromMonth + 6
        allo1.loc[allo1.FromMonth > 12, 'FromMonth'] = allo1.loc[allo1.FromMonth > 12, 'FromMonth'] - 12
        allo1.ToMonth = allo1.ToMonth + 6
        allo1.loc[allo1.ToMonth > 12, 'ToMonth'] = allo1.loc[allo1.ToMonth > 12, 'ToMonth'] - 12
        sites1 = filters.rd_sites(site_filter).reset_index()

        allo_sites1 = pd.merge(allo1, sites1, on='ExtSiteID')
        allo_sites1.rename(columns={'ExtSiteID': 'Wap'}, inplace=True)

        waps = allo_sites1.Wap.unique()

        setattr(self, 'waps', waps)
        setattr(self, 'allo', allo_sites1.set_index(['RecordNumber', 'HydroFeature', 'AllocationBlock', 'Wap']))

        if from_date is None:
            from_date = '1900-01-01'
        if to_date is None:
            to_date = str(datetime.now().date())
        setattr(self, 'from_date', from_date)
        setattr(self, 'to_date', to_date)


    def _usage_summ(self):
        """

        """
        ### Get the ts summary tables
        ts_summ1 = mssql.rd_sql(self.ts_server, self.ts_db, param.ts_summ_table, ['ExtSiteID', 'DatasetTypeID', 'FromDate', 'ToDate'], {'DatasetTypeID': list(param.dataset_dict.keys())})
        ts_summ2 = ts_summ1[ts_summ1.ExtSiteID.isin(self.waps)].copy()
#        ts_summ2['HydroFeature'] = ts_summ2['DatasetTypeID']
#        ts_summ2.replace({'HydroFeature': param.dataset_dict}, inplace=True)
        ts_summ2.rename(columns={'ExtSiteID': 'Wap'}, inplace=True)

        ts_summ2['FromDate'] = pd.to_datetime(ts_summ2['FromDate'])
        ts_summ2['ToDate'] = pd.to_datetime(ts_summ2['ToDate'])

        ts_summ3 = ts_summ2[(ts_summ2.FromDate < self.to_date) & (ts_summ2.ToDate > self.from_date)].copy()

        setattr(self, 'ts_usage_summ', ts_summ3)


    def _est_allo_ts(self):
        """

        """
        restr_col = param.allo_type_dict[self.freq]

        allo3 = self.allo.apply(allo_ts_apply, axis=1, from_date=self.from_date, to_date=self.to_date, freq=self.freq, restr_col=restr_col, remove_months=True)

        allo4 = allo3.stack()
        allo4.index.set_names(['RecordNumber', 'HydroFeature', 'AllocationBlock', 'Wap', 'Date'], inplace=True)
        allo4.name = 'allo'

        ## Rearrange
        allo5 = allo4.unstack(1).rename(columns={'Groundwater': 'GwAllo', 'Surface Water': 'SwAllo'})
        if not 'GwAllo' in allo5:
            allo5['GwAllo'] = 0
        if not 'SwAllo' in allo5:
            allo5['SwAllo'] = 0
        allo5.loc[allo5['GwAllo'].isnull(), 'GwAllo'] = 0
        allo5.loc[allo5['SwAllo'].isnull(), 'SwAllo'] = 0
        allo5['TotalAllo'] = allo5['GwAllo'] + allo5['SwAllo']

        ## Remove date if requested
        if self.irr_season and ('A' not in self.freq):
            dates1 = allo5.index.levels[3]
            dates2 = dates1[dates1.month.isin([10, 11, 12, 1, 2, 3, 4])]
            allo5 = allo5.loc[(slice(None), slice(None), slice(None), dates2)]

        setattr(self, 'allo_ts', allo5)


    def _get_allo_ts(self):
        """
        Function to create an allocation time series.

        """
        if self.freq not in param.allo_type_dict:
            raise ValueError('freq must be one of ' + str(param.allo_type_dict))

        if not hasattr(self, 'allo_ts'):
            self._est_allo_ts()


    def _get_metered_allo_ts(self, restr_allo=False, proportion_allo=True):
        """

        """
        setattr(self, 'proportion_allo', proportion_allo)

        ### Get the allocation ts either total or metered
        if restr_allo:
            if not hasattr(self, 'restr_allo_ts'):
                self._get_restr_allo_ts()
            allo1 = self.restr_allo_ts.drop(['restr_ratio'], axis=1).copy().reset_index()
            rename_dict = {'SwRestrAllo': 'SwMeteredRestrAllo', 'GwRestrAllo': 'GwMeteredRestrAllo', 'TotalRestrAllo': 'TotalMeteredRestrAllo'}
        else:
            if not hasattr(self, 'allo_ts'):
                self._get_allo_ts()
            allo1 = self.allo_ts.copy().reset_index()
            rename_dict = {'SwAllo': 'SwMeteredAllo', 'GwAllo': 'GwMeteredAllo', 'TotalAllo': 'TotalMeteredAllo'}

        ### Combine the usage data to the allo data
        if not hasattr(self, 'usage_crc_ts'):
            self._get_usage_ts()
        allo2 = pd.merge(self.usage_crc_ts.reset_index()[param.pk], allo1, on=param.pk, how='right', indicator=True)

        ## Re-categorise
        allo2['_merge'] = allo2._merge.cat.rename_categories({'left_only': 2, 'right_only': 0, 'both': 1}).astype(int)

        if proportion_allo:
            allo2.loc[allo2._merge != 1, list(rename_dict.keys())] = 0
            allo3 = allo2.drop('_merge', axis=1).copy()
        else:
            allo2['usage_waps'] = allo2.groupby(['RecordNumber', 'AllocationBlock', 'Date'])['_merge'].transform('sum')

            allo2.loc[allo2.usage_waps == 0, list(rename_dict.keys())] = 0
            allo3 = allo2.drop(['_merge', 'usage_waps'], axis=1).copy()

        allo3.rename(columns=rename_dict, inplace=True)
        allo3.set_index(param.pk, inplace=True)

        if 'TotalMeteredAllo' in allo3:
            setattr(self, 'metered_allo_ts', allo3)
        else:
            setattr(self, 'metered_restr_allo_ts', allo3)


    def _process_usage(self):
        """

        """
        ### Get the ts summary tables
        if not hasattr(self, 'ts_usage_summ'):
            self._usage_summ()
        ts_usage_summ = self.ts_usage_summ.copy()

        ## Get the ts data and aggregate
        if hasattr(self, 'usage_ts_daily'):
            tsdata1 = self.usage_ts_daily
        else:
            tsdata1 = mssql.rd_sql(self.ts_server, self.ts_db, param.ts_table, ['ExtSiteID', 'DateTime', 'Value'], where_in={'ExtSiteID': ts_usage_summ.Wap.unique().tolist(), 'DatasetTypeID': ts_usage_summ.DatasetTypeID.unique().tolist()}, from_date=self.from_date, to_date=self.to_date, date_col='DateTime')

            tsdata1['DateTime'] = pd.to_datetime(tsdata1['DateTime'])
            tsdata1.rename(columns={'DateTime': 'Date', 'ExtSiteID': 'Wap', 'Value': 'TotalUsage'}, inplace=True)

            ### filter - remove individual spikes and negative values
            tsdata1.loc[tsdata1['TotalUsage'] < 0, 'TotalUsage'] = 0

            def remove_spikes(x):
                val1 = bool(x[1] > (x[0] + x[2] + 2))
                if val1:
                    return (x[0] + x[2])/2
                else:
                    return x[1]

            tsdata1.iloc[1:-1, 2] = tsdata1['TotalUsage'].rolling(3, center=True).apply(remove_spikes, raw=True).iloc[1:-1]

            setattr(self, 'usage_ts_daily', tsdata1)

        ### Aggregate
        tsdata2 = util.grp_ts_agg(tsdata1, 'Wap', 'Date', self.freq).sum()

        setattr(self, 'usage_ts', tsdata2)


    def _get_usage_ts(self, usage_allo_ratio=2):
        """

        """
        ### Get the usage data if it exists
        if not hasattr(self, 'usage_ts'):
            self._process_usage()
        tsdata2 = self.usage_ts.copy()

        if not hasattr(self, 'allo_ts'):
            allo1 = self._get_allo_ts()
        allo1 = self.allo_ts.copy().reset_index()

        allo1['combo_allo'] = allo1.groupby(['Wap', 'Date'])['TotalAllo'].transform('sum')
        allo1['combo_ratio'] = allo1['TotalAllo']/allo1['combo_allo']

        ### combine with consents info
        usage1 = pd.merge(allo1, tsdata2, on=['Wap', 'Date'])
        usage1['TotalUsage'] = usage1['TotalUsage'] * usage1['combo_ratio']

        ### Remove high outliers
        usage1.loc[usage1['TotalUsage'] > (usage1['TotalAllo'] * usage_allo_ratio), 'TotalUsage'] = np.nan

        ### Split the GW and SW components
        usage1['SwRatio'] = usage1['SwAllo']/usage1['TotalAllo']

        usage1['SwUsage'] = usage1['SwRatio'] * usage1['TotalUsage']
        usage1['GwUsage'] = usage1['TotalUsage'] - usage1['SwUsage']
        usage1.loc[usage1['GwUsage'] < 0, 'GwUsage'] = 0

        usage1.drop(['SwAllo', 'GwAllo', 'TotalAllo', 'combo_allo', 'combo_ratio', 'SwRatio'], axis=1, inplace=True)

        usage2 = usage1.dropna().set_index(param.pk)

        setattr(self, 'usage_crc_ts', usage2)


    def _lowflow_data(self):
        """

        """
        if hasattr(self, 'lf_restr_daily'):
            lf_crc2 = self.lf_restr_daily
        else:
            ## Pull out the lowflows data
            lf_crc1 = mssql.rd_sql(self.crc_server, self.crc_db, param.lf_table, ['RecordNumber', 'AllocationBlock', 'RestrDate', 'Allocation'], where_in={'RecordNumber': self.allo.index.levels[0].unique().tolist()}, from_date=self.from_date, to_date=self.to_date, date_col='RestrDate')
            lf_crc1.rename(columns={'RestrDate': 'Date'}, inplace=True)
            lf_crc1.Date = pd.to_datetime(lf_crc1.Date)

            ## Aggregate to the crc and date - min restr ratio
            lf_crc2 = util.grp_ts_agg(lf_crc1, 'RecordNumber', 'Date', 'D')['Allocation'].min() * 0.01
            lf_crc2.name = 'restr_ratio'

            setattr(self, 'lf_restr_daily', lf_crc2)

        ### Aggregate to the appropriate freq
        lf_crc3 = util.grp_ts_agg(lf_crc2.reset_index(), 'RecordNumber', 'Date', self.freq)['restr_ratio'].mean()

        setattr(self, 'lf_restr', lf_crc3)


    def _get_restr_allo_ts(self):
        """

        """
        ### Get the allocation ts
        if not hasattr(self, 'allo_ts'):
            allo1 = self._get_allo_ts()
        if not hasattr(self, 'lf_restr'):
            self._lowflow_data()

        allo1 = self.allo_ts.copy().reset_index()
        lf_restr = self.lf_restr.copy().reset_index()

        ### Combine base data
        allo2 = pd.merge(allo1, lf_restr, on=['RecordNumber', 'Date'], how='left')
        allo2.loc[allo2.restr_ratio.isnull(), 'restr_ratio'] = 1

        ### Update allo
        allo2.rename(columns={'SwAllo': 'SwRestrAllo', 'GwAllo': 'GwRestrAllo', 'TotalAllo': 'TotalRestrAllo'}, inplace=True)
        allo2['SwRestrAllo'] = allo2['SwRestrAllo'] * allo2['restr_ratio']
        allo2['GwRestrAllo'] = allo2['GwRestrAllo'] * allo2['restr_ratio']
        allo2['TotalRestrAllo'] = allo2['TotalRestrAllo'] * allo2['restr_ratio']

        allo2.set_index(param.pk, inplace=True)

        setattr(self, 'restr_allo_ts', allo2)


    def get_ts(self, datasets, freq, groupby, irr_season=False, usage_allo_ratio=2):
        """
        Function to create a time series of allocation and usage.

        Parameters
        ----------
        datasets : list of str
            The dataset types to be returned. Must be one or more of {ds}.
        freq : str
            Pandas time frequency code for the time interval. Must be one of 'D', 'W', 'M', 'A', or 'A-JUN'.
        groupby : list of str
            The fields that should grouped by when returned. Can be any variety of fields including crc, take_type, allo_block, 'Wap', CatchmentGroupName, etc. Date will always be included as part of the output group, so it doesn't need to be specified in the groupby.
        irr_season : bool
            Should the calculations and the resulting time series be only over the irrigation season? The irrigation season is from October through to the end of April.
        usage_allo_ratio : int or float
            The cut off ratio of usage/allocation. Any usage above this ratio will be removed from the results (subsequently reducing the metered allocation).

        Results
        -------
        DataFrame
            Indexed by the groupby (and date)
        """
        ### Add in date to groupby if it's not there
        if not 'Date' in groupby:
            groupby.append('Date')

        ### Check the dataset types
        if not np.in1d(datasets, self.dataset_types).all():
            raise ValueError('datasets must be a list that includes one or more of ' + str(self.dataset_types))

        ### Check new to old parameters and remove attributes if necessary
        if 'A' in freq:
            freq_agg = freq
            freq = 'M'
        else:
            freq_agg = freq

        if hasattr(self, 'freq'):
            if (self.freq != freq) or (self.irr_season != irr_season):
                for d in param.temp_datasets:
                    if hasattr(self, d):
                        delattr(self, d)

        ### Assign pararameters
        setattr(self, 'freq', freq)
        setattr(self, 'irr_season', irr_season)

        ### Get the results and combine
        all1 = []

        if 'Allo' in datasets:
            self._get_allo_ts()
            all1.append(self.allo_ts)
        if 'MeteredAllo' in datasets:
            self._get_metered_allo_ts()
            all1.append(self.metered_allo_ts)
        if 'RestrAllo' in datasets:
            self._get_restr_allo_ts()
            all1.append(self.restr_allo_ts)
        if 'MeteredRestrAllo' in datasets:
            self._get_metered_allo_ts(True)
            all1.append(self.metered_restr_allo_ts)
        if 'Usage' in datasets:
            self._get_usage_ts(usage_allo_ratio)
            all1.append(self.usage_crc_ts)

        if 'A' in freq_agg:
            all2 = util.grp_ts_agg(pd.concat(all1, axis=1).reset_index(), ['RecordNumber', 'AllocationBlock', 'Wap'], 'Date', freq_agg).sum().reset_index()
        else:
            all2 = pd.concat(all1, axis=1).reset_index()

        if not np.in1d(groupby, param.pk).all():
            all2 = self._merge_extra(all2, groupby)

        all3 = all2.groupby(groupby).sum()

        return all3


    def _merge_extra(self, data, cols):
        """

        """
        allo_col = [c for c in cols if c in self.allo.columns]

        data1 = data.copy()

        if allo_col:
            all_allo_col = ['RecordNumber', 'AllocationBlock']
            all_allo_col.extend(allo_col)
            data1 = pd.merge(data1, self.allo.reset_index()[all_allo_col], on=['RecordNumber', 'AllocationBlock'])

        data1.set_index(param.pk, inplace=True)

        return data1

