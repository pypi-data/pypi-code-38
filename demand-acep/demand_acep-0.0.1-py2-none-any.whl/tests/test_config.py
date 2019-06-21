# Configuation for the test environment

# This file has the global configuration 
# so we do not have to repeat those in every function 

import pandas as pd
import os, sys
import datetime

# This is for production environment
# The tests will define these paths separately
print(" Test Config imported")

dirname = os.path.dirname(os.path.dirname(__file__))
###################################################
# This is the main change from the production config 
DATA_ROOT = os.path.join(dirname, "data/measurements")
######################################################
print(DATA_ROOT)
METADATA_PATH = os.path.join(dirname, "data/properties/")
METER_CHANNEL_FILE = os.path.join(METADATA_PATH, "NetCDF Meter File Generation Matrix Copy Poker Flats.xlsx")
DATA_YEARS_FILE = os.path.join(METADATA_PATH, "data_years.txt")
METER_NAMES_FILE = os.path.join(METADATA_PATH, "meter_names.txt")

# Get meter names from meter names file 
meter_names_df = pd.read_csv(METER_NAMES_FILE)
print(meter_names_df)
METER_NAMES = meter_names_df['meter_name'].tolist()

# Read in files containing channel names for WattsOn
meter_channel_metadata_WattsOnMetadata = pd.read_excel(METER_CHANNEL_FILE, sheet_name="WattsOnMk2")
meter_channel_metadata_PQube = pd.read_excel(METER_CHANNEL_FILE, sheet_name="PQube3PF")

# Extract channel names

###########################################################################
# TODO: Create a metadata file with channel names for every meter 
# ----------------------------------------------------------------
# this is hardcoded to read upto line 48, 
# as the file contains other lines at the end. This should be changed to a 
# file containing channels per meter, as different meters can have different
# channels and that file should be a source of truth across applications, 
# the new database schema is created when this file changes
############################################################################

# # Additional column name time is added to store the timestamp of measurement
# channel_names = ['time'] + list(meter_details['Channels'][:48])
# # Extract name of meters 
# # TODO: Change this part to remmove the hardcoding
# #  when the metadata files are sorted
# # ---------------------------------------------------------
# meter_names = list(meter_details.columns.values)[-4:]

# Create a dictionary to store the channels per meter. So keys are the meter 
# names and the values are a list of channel per meter
METER_CHANNEL_DICT = {}
# Loop across the meter_names list to add channels for each meter
for index, row in meter_names_df.iterrows():
    if row['meter_type'] == 'WattsOnMk2':
        channel_names = meter_channel_metadata_WattsOnMetadata['Filename'][0:48]
        METER_CHANNEL_DICT[row['meter_name']] = ['time'] + list(channel_names) 
    elif row['meter_type'] == 'PQube':
        channel_names = meter_channel_metadata_PQube['Filename'][0:46]
        METER_CHANNEL_DICT[row['meter_name']] = ['time'] + list(channel_names)
        
# Get years from the years file
years_df = pd.read_csv(DATA_YEARS_FILE)

DATA_YEARS = years_df['years'].values.tolist()

# Data start and end date
DATA_START_DATE = datetime.datetime(2017, 11, 1)
DATA_END_DATE = datetime.datetime(2019, 4, 30)

# Database name 
DB_NAME = 'demand_acep'

# Downsampling duration
# sample_time allows the user determine what time interval the data should be resampled at
# For 1 minute - 1T, 1 hour - 1H, 1 month - 1M, 1 Day - 1D
SAMPLE_TIME = '1T'

# Data imputation related settings
# Data Imputation by interpolation
# interp_method and interp_order allows the user specify the method of interpolation and the order
INTERP_METHOD = 'spline'
INTERP_ORDER = 2