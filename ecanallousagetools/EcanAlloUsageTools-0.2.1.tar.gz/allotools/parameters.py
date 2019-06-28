# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 13:17:03 2018

@author: michaelek
"""

#####################################
### Misc parameters for the various functions

hydro_server = 'edwprod01'
hydro_database = 'hydro'
crc_server = 'edwdev01'
crc_database = 'ConsentsReporting'
allo_table = 'reporting.CrcAlloSiteSumm'
site_table = 'ExternalSite'
ts_summ_table = 'TSDataNumericDailySumm'
ts_table = 'TSDataNumericDaily'
lf_table = 'reporting.TSCrcBlockRestr'

dataset_dict = {9: 'Surface Water', 12: 'Groundwater'}

#sd_dict = {7: 'sd1_7', 30: 'sd1_30', 150: 'sd1_150'}

status_codes = ['Terminated - Replaced', 'Issued - Active', 'Terminated - Surrendered', 'Terminated - Cancelled', 'Terminated - Expired', 'Terminated - Lapsed', 'Issued - s124 Continuance', 'Issued - Inactive']

#use_type_dict = {'Aquaculture': 'irrigation', 'Dairy Shed (Washdown/Cooling)': 'stockwater', 'Intensive Farming - Dairy': 'irrigation', 'Intensive Farming - Other (Washdown/Stockwater/Cooling)': 'stockwater', 'Intensive Farming - Poultry': 'irrigation', 'Irrigation - Arable (Cropping)': 'irrigation', 'Irrigation - Industrial': 'irrigation', 'Irrigation - Mixed': 'irrigation', 'Irrigation - Pasture': 'irrigation', 'Irrigation Scheme': 'irrigation' , 'Viticulture': 'irrigation', 'Community Water Supply': 'water_supply', 'Domestic Use': 'water_supply', 'Construction': 'industrial', 'Construction - Dewatering': 'industrial', 'Cooling Water (non HVAC)': 'industrial', 'Dewatering': 'industrial', 'Gravel Extraction/Processing': 'industrial', 'HVAC': 'industrial', 'Industrial Use - Concrete Plant': 'industrial', 'Industrial Use - Food Products': 'industrial', 'Industrial Use - Other': 'industrial', 'Industrial Use - Water Bottling': 'industrial', 'Mining': 'industrial', 'Firefighting ': 'municipal', 'Firefighting': 'municipal', 'Flood Control': 'municipal', 'Landfills': 'municipal', 'Stormwater': 'municipal', 'Waste Water': 'municipal', 'Stockwater': 'stockwater', 'Snow Making': 'industrial', 'Augment Flow/Wetland': 'other', 'Fisheries/Wildlife Management': 'other', 'Other': 'other', 'Recreation/Sport': 'other', 'Research (incl testing)': 'other', 'Power Generation': 'hydroelectric', 'Drainage': 'municipal', 'Frost Protection': 'municipal'}

#restr_type_dict = {'max rate': 'max_rate_crc', 'daily volume': 'daily_vol', 'annual volume': 'feav'}

allo_type_dict = {'D': 'AllocatedRate', 'W': 'AllocatedRate', 'M': 'AllocatedAnnualVolume', 'A-JUN': 'AllocatedAnnualVolume', 'A': 'AllocatedAnnualVolume'}

freq_codes = ['D', 'W', 'M', 'A-JUN', 'A']

dataset_types = ['Allo', 'RestrAllo', 'MeteredAllo', 'MeteredRestrAllo', 'Usage']

pk = ['RecordNumber', 'AllocationBlock', 'Wap', 'Date']

allo_cols = ['RecordNumber', 'HydroFeature', 'AllocationBlock', 'ExtSiteID', 'FromDate', 'ToDate', 'FromMonth', 'ToMonth', 'AllocatedRate', 'AllocatedAnnualVolume', 'WaterUse', 'IrrigationArea', 'ConsentStatus']

site_cols = ['ExtSiteID', 'ExtSiteName', 'NZTMX', 'NZTMY', 'CatchmentName', 'CatchmentNumber', 'CatchmentGroupName', 'CatchmentGroupNumber', 'SwazName', 'SwazGroupName', 'SwazSubRegionalName', 'GwazName', 'CwmsName']


#temp_datasets = ['allo_ts', 'total_allo_ts', 'restr_allo_ts', 'lf_restr', 'usage_crc_ts', 'usage_ts', 'usage_crc_ts', 'metered_allo_ts', 'metered_restr_allo_ts']

#datasets = {'allo': ['total_allo', 'sw_allo', 'gw_allo'],














