"""
This is the place for all the unit tests for the package demand_acep.
We can refactor this if this becomes too large.

"""
# %% Imports

import os
import sys
import numpy as np
import pandas as pd
import pdb
import pytest
import copy
import importlib
import unittest

from itertools import groupby
from operator import itemgetter

# To import files from the parent directory
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from demand_acep import extract_data
from demand_acep import extract_ppty
from demand_acep import data_resample
from demand_acep import data_impute
from demand_acep import compute_interpolation
from demand_acep import build_interpolation
from demand_acep import long_missing_data_prep
from extract_data_to_csv import extract_csv_for_date
# %% Paths
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# dirpath = os.path.join(path, 'data/measurements/2018/07/01')
# filename = 'PokerFlatResearchRange-PokerFlat-PkFltM1AntEaDel@2018-07-02T081007Z@PT23H@PT146F.nc'
dirpath = os.path.join(path, 'data/measurements/2019/01/03')
filename = 'PokerFlatResearchRange-PokerFlat-PkFltM3SciEaDel@2019-01-03T093004Z@P1D@PT179F.nc'

# Test config 
import test_config as config

def test_extract_data():
    test_df = extract_data(dirpath, filename)
    column_name = test_df.columns.tolist()[0]

    assert (test_df.index.dtype == 'datetime64[ns]'), "The first output from this function should be a timedelta object"

    assert (test_df[column_name].dtype == 'float64'), "The second output from this function should be numpy array"

    return


def test_extract_ppty():
    meter_name = ['PkFltM1Ant', 'PkFltM2Tel', 'PkFltM3Sci', 'PQube3']
    [test_meter, test_channel] = extract_ppty(filename, meter_name)

    assert (any(val == test_meter for val in meter_name)), "Returned meter name does not exist"

    assert (test_channel in filename), "Returned measurement channel does not exist"

    return


def test_data_resample():
    test_df = extract_data(dirpath, filename)
    test_resampled = data_resample(test_df, sample_time='1T')
    diff_test = np.diff(test_resampled.index)
    time_1T_ns = np.timedelta64(60000000000,'ns') # sample_time 1T in nanoseconds
    assert (np.all(np.equal(diff_test, time_1T_ns))), "Data not properly downsamples"

    return


def test_data_impute():
    test_df = extract_data(dirpath, filename)
    test_df = data_impute(test_df)
    dict_assert = []
    if isinstance(test_df, dict):
        for meter in test_df:
            dict_assert.append(test_df[meter].notnull().values.all())
        assert (all(val for val in dict_assert)), "Data imputations in dictionary not functioning properly as data " \
                                                  "still contains NaN"
    else:
        assert (test_df.notnull().values.all()), "Data imputations in Dataframes not functioning properly as data " \
                                                 "still contains NaN"

    return

def test_extract_csv_for_date_badIn():
    
    # Test that bad input throws the right kind of exceptions 
    
    # DATA_ROOT attribute does not exist
    config_1 = importlib.reload(config)
    vars(config_1).pop('DATA_ROOT', None)
    # Correct date 
    data_date_1 = "07/01/2018"
    
    #print(config_1.DATA_ROOT)
    
    with pytest.raises(AttributeError):
        extract_csv_for_date(config_1, data_date_1)
    
    config_2 = importlib.reload(config)
    # Bad data_root
    config_2.DATA_ROOT = "/not_a_directory"
    # Correct date 
    data_date_2 = "07/01/2018"
    
    #print(config.DATA_ROOT)
    
    with pytest.raises(NotADirectoryError):
        extract_csv_for_date(config_2, data_date_2)
    
    config_3 = importlib.reload(config)
    data_date_3 = "07/01/2018"
    # No meter_channel_dict
    vars(config_3).pop('METER_CHANNEL_DICT', None)
    
    with pytest.raises(AttributeError):
        extract_csv_for_date(config_3, data_date_3)
    
    config_4 = importlib.reload(config)
    data_date_4 = "07/01/2018"
    
    # No SAMPLE_TIME
    vars(config_4).pop('SAMPLE_TIME', None)
    
    with pytest.raises(AttributeError):
        extract_csv_for_date(config_4, data_date_4)
        
    
    config_5 = importlib.reload(config)
    data_date_5 = "10/01/2017"
    
    with pytest.raises(ValueError):
        extract_csv_for_date(config_5, data_date_5)
    
    return 


def test_extract_csv_for_date():
    # Test date 
    test_data_date = '2019/01/03'
    # Re-import the config to make changes for this test
    test_config1 = importlib.reload(config)
    # Get the new DATA_ROOT to the location of the test data
    test_config1.DATA_ROOT = os.path.join(test_config1.DATA_ROOT, 'part_data')
    # Run the test function with the inputs
    test_csv_names = extract_csv_for_date(test_config1, test_data_date)
    print(test_csv_names)
    # Test the output filenames
    # Get correct names
    correct_csv_path = os.path.join(test_config1.DATA_ROOT, test_data_date, "correct_csvs")
    print(correct_csv_path)
    correct_names = [f for f in os.listdir(correct_csv_path) if os.path.isfile(os.path.join(correct_csv_path, f))]
    print(correct_names)
    # test_names_result = all(elem in correct_names for elem in test_csv_names)
    assert(checkEqual(correct_names, list(test_csv_names.values())), "The output csv names do not match the expected name format - meter_name@date@freq.csv")

    # Test the output values
    # Read in the correct csvs 
    correct_dfs = {}
    for dirpath, dirnames, correct_csvfiles in os.walk(correct_csv_path, topdown=True):
        for csvfilename in correct_csvfiles:
            csvfile_abspath = os.path.join(correct_csv_path, csvfilename)
            correct_dfs[csvfilename] = pd.read_csv(csvfile_abspath, header=None)
    
    test_csv_path = os.path.join(test_config1.DATA_ROOT, test_data_date)
    test_dfs = {}
    for dirpath, dirnames, test_files in os.walk(test_csv_path, topdown=True):
        for filename in test_files:
            if filename.lower().endswith('.csv'):
                csvfile_abspath = os.path.join(test_csv_path, filename)
                test_dfs[filename] = pd.read_csv(csvfile_abspath, header=None)
                # Remove the NA columns - these are introduced since we have only two channels
                test_dfs[filename].dropna(axis=1, inplace=True)

    # Check if the dataframes in correct_dfs and test_dfs are equal 
    for csvname in correct_dfs:
        correct_df = correct_dfs[csvname]
        test_df = test_dfs[csvname]
        pd.testing.assert_frame_equal(test_df, correct_df)

    return 


def test_build_interpolation():
    df = extract_data(dirpath, filename)
    test_resampled = data_resample(df, sample_time='1T')
    test_df = test_resampled.copy()
    # gets the index location in integers where the NaNs are located
    get_nan_idx = np.where(test_df.isna())[0]
    idx_grp_nan = []
    # creates a list of consecutive index locations to determine the range of interpolation
    for k, g in groupby(enumerate(get_nan_idx), lambda ix: ix[0] - ix[1]):
        idx_grp_nan.append(list(map(itemgetter(1), g)))
    # performs interpolation for each consecutive NaN index location
    for idx, val in enumerate(idx_grp_nan):
        n_grp = len(val)
        # for each range of consecutive NaN locations, use data points of length equal to the number that NaNs in that
        # range before and after the NaN datapoints
        prev_idx = val[0] - n_grp
        next_idx = val[-1] + n_grp
        # This if-else clause handles edge cases
        # If - When the number of consecutive NaN points is larger than the number of available data points before it in
        # the dataframe.
        # Elif - When the number of consecutive NaN points is larger than the number of available data points after it
        # in the dataframe.
        if prev_idx < 0:
            prev_vals = test_df.iloc[0:val[0]]
            next_vals = test_df.iloc[val[0] + 1: next_idx + 1]
        elif next_idx > len(test_df):
            prev_vals = test_df.iloc[prev_idx:val[0]]
            next_vals = test_df.iloc[val[0] + 1: len(test_df)]
        else:
            prev_vals = test_df.iloc[prev_idx:val[0]]
            next_vals = test_df.iloc[val[0] + 1: next_idx + 1]
        y_values = prev_vals.append(next_vals)
    y_interp = build_interpolation(y_values, n_grp)
    # pdb.set_trace()
    # check that y_interp is has no NaN values
    assert (~np.isnan(y_interp).any()), "Interpolation function not fully replacing NaN with interpolation values"
    # check that y_interp is within reasonable range from y_values
    max_val = np.max(y_values) + np.std(y_values)
    min_val = np.min(y_values) - np.std(y_values)
    assert (y_interp.all() < max_val).all() or (y_interp.all() > min_val).all(), "Error in determining a function fit " \
                                                                                 "through interpolation"

    assert (y_interp.dtype == 'float64'), "The output from this function should be numpy array"
    return


def test_compute_interpolation():
    test_df = extract_data(dirpath, filename)
    if isinstance(test_df, dict):
        for meter in test_df:
            assert (isinstance(test_df[meter], pd.DataFrame)), "Object passed in is not a Dataframe"
            if test_df[meter].isnull().values.any():
                test_df[meter] = test_df[meter].apply(compute_interpolation)
                assert (test_df[meter].notnull().values.all()), "Data imputations in Series not functioning properly " \
                                                                "as data still contains NaN"
    else:
        assert (isinstance(test_df, pd.DataFrame)), "Object passed in is not a Dataframe"
        if test_df.isnull().values.any():
            test_df = test_df.apply(compute_interpolation)
            assert (test_df.notnull().values.all()), "Data imputations in Series not functioning properly as data " \
                                                     "still contains NaN"

    return


def test_long_missing_data_prep():
    dirpath_data = os.path.join(path, 'data/measurements/test_data')
    filename_data = 'PQube3_comb.csv'

    meter_mod_df = long_missing_data_prep(dirpath_data, filename_data)

    assert (filename_data[-4:] == '.csv'), "File passed in is not in a .csv format"
    assert (isinstance(meter_mod_df, pd.DataFrame)), "Object returned in is not a Dataframe"
    meter_df = pd.read_csv(os.path.join(dirpath_data, filename_data))
    assert (len(meter_mod_df) >= len(meter_df)), "Returned DataFrame should be greater than or equal to the data " \
                                                 "passed in"
    diff_test = np.diff(meter_mod_df.index)
    time_1T_ns = np.timedelta64(60000000000, 'ns')  # sample_time 1T in nanoseconds
    assert (np.all(np.equal(diff_test, time_1T_ns))), "DateTimeIndex intervals not properly computed in function"

    return

# Taken from https://stackoverflow.com/a/12813909/1328232
# To check the equality of two lists
def checkEqual(L1, L2):
    return len(L1) == len(L2) and sorted(L1) == sorted(L2)
