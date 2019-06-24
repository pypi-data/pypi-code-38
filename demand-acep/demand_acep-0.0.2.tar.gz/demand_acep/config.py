""" 
This file has the global configuration so we do not have to repeat those in every function. 

We can create separate configuration files for production and test system, but they should atleast define the following:

Attributes
----------
DATA_ROOT: string 
    This is the absolute path of data. 

METADATA_PATH: string
    This is the absolute path of the metadata for our data. The metadata contains information about channels per meter, names and years of meters etc. 
    Sample metadata files are found in `https://github.com/demand-consults/demand_acep/tree/master/demand_acep/data/properties`.
    
METER_CHANNEL_FILE: string
    This is the absolute path of the files containing the names of channels for each meter. Each meter can have different channels it reads. 
    An example `METER_CHANNEL_FILE` is here: https://github.com/demand-consults/demand_acep/blob/master/demand_acep/data/properties/NetCDF%20Meter%20File%20Generation%20Matrix%20Copy%20Poker%20Flats.xlsx
    If the format of this file changes, then the parsing logic below will have to change accordingly.

DATA_YEARS_FILE: string 
    This is the absolute path of the data years file. This file lists all the years that we have the data for. The code then creates a new table for each meter for each year. 
    A sample data years file is here: https://github.com/demand-consults/demand_acep/blob/master/demand_acep/data/properties/data_years.txt

METER_NAMES_FILE: string 
    This is the absolute path of the meter names file. This file lists the names of the all the meters and their type. 
    A sample `METER_NAMES_FILE` is here: https://github.com/demand-consults/demand_acep/blob/master/demand_acep/data/properties/meter_names.txt

METER_NAMES: list
    This list contains the names of the meters. 

METER_CHANNEL_DICT: dictionary
    This dictionary should contain the available meter names as keys and the channels for that meter as values for the corresponding. 
    The generation of this dictionary is related to the structure of the `METER_CHANNEL_FILE`.

DATA_YEARS: list
    This list contains the years of the data. 

DATA_START_DATE: datetime.datetime
    The start date for the data to process. 

DATA_END_DATE: datetime.datetime
    The end date for the date to process. 

DB_NAME: string
    The name of the database to create the schema in. This database will store the processed data, with one table per meter per year. 

tsdb_pc_path: string
    The absolute path of the timescaledb-parallel-copy Go executable.

DB_USER: string 
    The username to connect to the TimescaleDB with

DB_PASSWORD: string 
    The password for the TimescaleDB database. 

SAMPLE_TIME: string 
    The argument needed to downsample the data, 1T = 1 min etc. Please refer to the pandas `resample` documentation here: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.resample.html


 """

import pandas as pd
import os, sys
import datetime

# This is for production environment
# The tests will define these paths separately
print("Config imported")
DATA_ROOT = "/gscratch/stf/demand_acep/Data"

dirname = os.path.dirname(__file__)
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

#######################################################
############ Database related configuration ###########
#######################################################


# Datebase IP address
DB_ADDRESS = "localhost"
# Database port 
DB_PORT = 5432
################################################################
############### !!!! NEVER COMMIT THE CREDENTIALS TO GIT !!!!!!!
################# Only demonstrated here as an example #########
################################################################
# DB username 
DB_USER = "cp84"
# DB password
DB_PWD = "neotao123"
# Database name 
DB_NAME = 'demand_acep'
#  path of timescaledb-parallel-copy
tsdb_pc_path = "/gscratch/stf/demand_acep/go/bin"

# Downsampling duration
# sample_time allows the user determine what time interval the data should be resampled at
# For 1 minute - 1T, 1 hour - 1H, 1 month - 1M, 1 Day - 1D
SAMPLE_TIME = '1T'
