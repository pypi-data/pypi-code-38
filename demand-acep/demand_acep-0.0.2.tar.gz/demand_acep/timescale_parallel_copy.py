"""
Functions in this file insert the data into the timescaledb database using the 
go utility provided by timescaledb called timescaledb-parallel-copy
"""

import os
import pandas as pd
import pdb
import datetime
import io
import glob
import multiprocessing
import subprocess

from demand_acep import extract_data
from demand_acep import extract_ppty

def parallel_copy_data_for_date(config, data_date):
    """ 
    This function parallel copies the data for the data_date specified to the 
    appropriate table of TSDB.
    
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
    int
        Description of anonymous integer return value.
    """    
    print(data_date)
    # Look for the pickle and file and use pandas_to_sql to insert the data 
    # into the database. 
    data_year = data_date[-4:]
    # print(data_year)
    # print(config.DATA_ROOT)
    # find this path, extract data from those files, create a dataframe, and 
    # store it as pickle in the folder. 
    data_month = data_date[0:2]
    data_day = data_date[3:5]
    data_path = os.path.join(config.DATA_ROOT, data_year, data_month, data_day)
    # print(data_path)
    # print(config.METER_CHANNEL_DICT)
    # print(config.DATA_YEARS)
    
    meter_count = len(config.METER_CHANNEL_DICT)
    # Create a list of lists of size of number of meters
    meter_collection = {}
    meter_pickle_names = {}
    # Path of the tsdb parallel copy go executable
    timescaledb_parallel_copy_path = os.path.join(config.tsdb_pc_path, "timescaledb-parallel-copy")
    db_address = config.DB_ADDRESS
    db_name = config.DB_NAME
    db_username = config.DB_USER
    db_pwd = config.DB_PWD
    # Get the CPU count for parallelizing the process
    num_workers = multiprocessing.cpu_count()
    # Generate the connection string for the database
    connection_string = 'host={0} user={1} password={2} sslmode=disable'.format(db_address, db_username, db_pwd)
    
    
    for fname in glob.glob(os.path.join(data_path, '*.csv')):
        # print(os.path.basename(fname))
        file_name = os.path.basename(fname)
        table_name = file_name.split('@')[0] + '_' + data_year
        parallel_copy_cmd = [timescaledb_parallel_copy_path, '--db-name', 
                            db_name, '--table', table_name, '--file', fname, 
                            '--workers', str(num_workers), '--connection', 
                            connection_string, '--skip-header', 'true']
        # print(parallel_copy_cmd)
        pcopy = subprocess.run(parallel_copy_cmd, encoding='utf-8', stdout=subprocess.PIPE)
        for line in pcopy.stdout.split('\n'):
            print(line)

    return 

def parallel_copy_data_for_dates(config, start, end):
    """ 
    This function extracts the data to disk for the data_date_range specified.
    
    Parameters
    ----------
    config : 
        `config` contains the configuration for paths etc. needed by files. As
        an argument we can change the config files for different production 
        vs test configs 
    start : str or datetime-like
        Left bound for generating dates.
    end : str or datetime-like
        Right bound for generating dates.
 
    Returns
    -------
    int
        Description of anonymous integer return value.
    """
    
    # Get the list of dates within the range and convert to the format we want
    dates_in_range = pd.date_range(start, end).strftime("%m/%d/%Y")
    print(dates_in_range)
    # Perform the insert for the said days
    for date in dates_in_range:
        parallel_copy_data_for_date(config, date)

    return 
    
    