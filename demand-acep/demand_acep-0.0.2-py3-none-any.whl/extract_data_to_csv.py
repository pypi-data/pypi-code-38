""" The functions in this file convert the netcdf files to a dataframe and then 
write them to disk using multiprocessing. So, if we have a multi-core system, the 
extraction can happen in parallel. """

import os
import pandas as pd
import numpy as np
import pdb
import datetime
import io
import multiprocessing as mp

from demand_acep import extract_data
from demand_acep import extract_ppty
from demand_acep import data_resample
from demand_acep import data_impute
from dateutil.parser import parse


def extract_csv_for_date(config, data_date):
    """ 
    This function writes the data for the data_date specified to a csv on disk.
    
    Parameters
    ----------
    config : 
        `config` contains the configuration for paths etc. needed by files. As
        an argument we can change the config files for different production 
        vs test configs 
    data_date : string
        `data_date` string will be used to extract the year and the path to the
        data. It should be in the 'mm/dd/yyyy' format. 

    Returns
    -------
    list
        Names of the csv's written to disk.
    """    
    
    ### TODO: test config separately 
    
    # print(config.DATA_ROOT)
    # print(data_date)
    
    # Raise an exception if attribute DATA_ROOT does not exist
    if not 'DATA_ROOT' in vars(config):
        raise AttributeError("Attribute DATA_ROOT does not exist")
        
    # Raise an exception if DATA_ROOT does not exist
    if not os.path.exists(config.DATA_ROOT):
        raise NotADirectoryError("The path " + config.DATA_ROOT + " not found")
        
    # Raise an exception if attribute METER_CHANNEL_DICT does not exist
    if not 'METER_CHANNEL_DICT' in vars(config):
        raise AttributeError("Attribute METER_CHANNEL_DICT does not exist")
        
    # Raise an exception if attribute METER_CHANNEL_DICT does not exist
    if not 'SAMPLE_TIME' in vars(config):
        raise AttributeError("Attribute METER_CHANNEL_DICT does not exist")
    
    data_date_dt = parse(data_date)
    
    if data_date_dt > config.DATA_END_DATE:
        raise ValueError("data_date entered is greater than the DATA_END_DATE: " + 
                        str(config.DATA_END_DATE))
                        
    if data_date_dt < config.DATA_START_DATE:
        raise ValueError("data_date entered is less than the DATA_START_DATE: " + 
                        str(config.DATA_START_DATE))
                        
    # Get the year, month and and day from date entered
    data_year = data_date_dt.year
    data_month = data_date_dt.month
    data_day = data_date_dt.day
    
    # Get the corresponding path in the directory to look for the data for the day
    data_path = os.path.join(config.DATA_ROOT, str(data_year), "{:02}".format(data_month), "{:02}".format(data_day))
    # print(data_path)
    # Find the count of meters
    meter_count = len(config.METER_CHANNEL_DICT)

    # Dictionary to store the names of the resulting csv files
    meter_csv_names = {}
    
    # Get the down-sampling time
    sample_time = config.SAMPLE_TIME
    
    # Create a dictionary with keys are meter names and values as dataframes 
    # containing the data for the day
    meter_collection = {}
    
    # for meter_name in config.METER_CHANNEL_DICT:
    #     # Create an empty dataframe, the columns will be created later
    #     meter_collection[meter_name] = pd.DataFrame()

    #print(meter_collection)
    if os.path.exists(data_path):
        # Walk through all the files in the directory for the day's data
        for dirpath, dirnames, files in os.walk(data_path, topdown=True):
            # `files` contains the names of all the files at the location
            if len(files) == 0:
                print("No files found for day: " + data_path)
                continue
            for filename in files:
                # Get the netcdf files, these are files with `.nc` extension
                if filename.lower().endswith('.nc'):
                    # For the particular file, find out the corresponding meter and channel 
                    [meter, channel] = extract_ppty(filename, config.METER_CHANNEL_DICT.keys())
                    # Create an entry in the `meter_collection` dict if it does not exist yet
                    if meter not in meter_collection:
                        meter_collection[meter] = pd.DataFrame()
                    # Form the resulting csv name from the meter name if it doesnt exist yet
                    # They are of the type - meter_name@Timestamp@Duration@Frequency
                    # For e.g.: PQube3@2017-11-01T080002Z@PT23H@PT227F.cs
                    #print(meter, channel)
                    if meter not in meter_csv_names:
                        meter_csv_names[meter] = '@'.join([meter, '@'.join(filename.split('@')[1:4])])[:-3] + '.csv'
                    #print(meter_csv_names)
                    # Get the full path of the csv
                    csv_name = os.path.join(data_path, meter_csv_names[meter])
                    # Only extract if not already extracted to csv
                    if (not os.path.isfile(csv_name)):
                        # Get the dataframe containing time and channel values
                        channel_df = extract_data(dirpath, filename)
                        # Give the dataframe column a name
                        channel_df.columns = [channel]
                        # Down-sample the data to the sampling time intended
                        channel_resampled = data_resample(channel_df, sample_time)
                        # If our meter dataframe is empty so far, i.e. if this is the 
                        # first channel being entered, then create a copy of the 
                        # resampled dataframe
                        if meter_collection[meter].empty:
                            meter_collection[meter] = channel_resampled.copy()
                        ####################### 
                        # This `else` clause handles two cases:
                        # 1. If the dataframe is not empty, then add other columns to
                        #    the dataframe. (the else case)
                        # 2. Some days have data downloaded more than once, this means 
                        #    that channels can occur more than once. (like 05/21/2018)
                        #######################
                        else:
                            # If the channel already exists in the dataframe
                            # then either the other file has updated data or 
                            # subsequent data. 
                            if channel in meter_collection[meter].columns:
                                # Get index from total dataframe 
                                idx_1 = meter_collection[meter].index
                                # Get index from file dataframe
                                idx_2 = channel_resampled.index
                                # Compare the two, if the index is contained within,
                                # then **update** the channel's value for file's indices. 
                                if np.all(np.isin(idx_2, idx_1)):
                                    meter_collection[meter][channel].loc[idx_2] = channel_resampled.values.tolist()
                                # If the index is not contained, append the file df to
                                # the total dataframe
                                else:
                                    meter_collection[meter] = meter_collection[meter].append(channel_resampled, sort=False)
                                    meter_collection[meter].sort_index(inplace=True)
                                    #######################
                                    # This data is resampled a second time to handle two cases:
                                    # 1. When appending a resampled dataframe to an already resampled dataframe, the last
                                    #    index of the original dataframe and the first index of the new dataframe can have
                                    #    the same time. Resampling the appended dataframe will eliminate the repetitions.
                                    # 2. If the new dataframe to be appended starts at a much later time, resampling the
                                    #    appended dataframe will create rows of missing data (NaN) at the times with no
                                    #    measurement values. This makes it easier to detect missing measurement values and
                                    #    perform data imputation at a later phase.
                                    #######################
                                    meter_collection[meter] = data_resample(meter_collection[meter], sample_time)
                            # If the channel does not already exist, then add the
                            # file dataframe to the total df. 
                            else:
                                meter_collection[meter] = meter_collection[meter].join(channel_resampled, how='outer')
    else:
        print("Path not found: " + data_path)
                
    # Perform data imputation wherrever needed
    # print(meter_collection)
    meter_collection = data_impute(meter_collection)
    
    # Write the total dataframes to csv file
    for meter in meter_collection:
        # Reorganize the order of columns to match the database tables 
        meter_channels = config.METER_CHANNEL_DICT[meter]
        # meter_collection[meter].reset_index(inplace=True)
        meter_collection[meter] = meter_collection[meter].reindex(columns=meter_channels[1:])
        csv_name = os.path.join(data_path, meter_csv_names[meter])
        # print(csv_name)
        # Only write csv if it does not exist yet
        if(not os.path.isfile(csv_name)):
            meter_collection[meter].to_csv(csv_name, header=False)

    return meter_csv_names

def printResult(result):
    # print(result)
    return
    