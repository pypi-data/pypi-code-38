"""
This module contains code for the demand_acep. More documentation to come.

This is a test docstring for the whole module

"""

# %% Imports
import os
import pandas as pd
import numpy as np
import pdb
import xarray as xr
# import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.interpolate import UnivariateSpline
from itertools import groupby
from operator import itemgetter
# %%


def extract_data(dirpath, filename):
    """
        This function reads and extracts the NetCDF format data of the given meter channel using a package called xarray.

        Parameters
        ----------
        dirpath :
            `dirpath` is the directory path location of the NetCDF file to be read
        filename :
            `filename` is the NetCDF format meter channel file to be read.

        Returns
        -------
        Dataframe
            Sample-time indexed pandas dataframe containing measurement values from the given file.
        """
    # Extracts NetCDF files using xarray module
    netcdf_data = xr.open_dataset(os.path.join(dirpath, filename))
    netcdf_df = netcdf_data.to_dataframe()
    # Converts the time index to datetime format
    netcdf_df.set_index(pd.to_datetime(netcdf_df.index.values), inplace=True)

    return netcdf_df


def extract_ppty(filename, meter_name):
    """
        This function parses out the given filename as a string to determine the meter name and the measurement
        channel/type contained in the file

        Parameters
        ----------
        filename :
            `filename` is the NetCDF format meter channel file whose name contains information such as location, date,
            meter type, measurement channel/type and sampling frequency. An example filename is:
            'PokerFlatResearchRange-PokerFlat-PkFltM1AntEaDel@2018-07-02T081007Z@PT23H@PT146F.nc'
        meter_name :
            `meter_name` is a list containing the names of each of the meters at pokerflats

        Returns
        -------
        meter : string
            `meter` is the meter name of the NetCDF format file given.
        channel : string
            `channel` is the measurement type contained in the NetCDF format file given
        """
    # Example filename - 'PokerFlatResearchRange-PokerFlat-PkFltM1AntEaDel@2018-07-02T081007Z@PT23H@PT146F.nc'
    filename_split_1 = filename.split('@')
    filename_split_2 = filename_split_1[0].split('-')
    meter_channel = filename_split_2[-1]
    for name in meter_name:
        if meter_channel.startswith(name):
            n_name = len(name)
            # Example meter from example filename above - PkFltM1Ant
            meter = meter_channel[:n_name]
            # Example channel from example filename above - EaDel (Energy delivered to Phase A)
            channel = meter_channel[n_name:]

    return meter, channel


def data_resample(df, sample_time='1T'):
    """
        This function downsamples a sample-time indexed pandas dataframe containing measurement channel values based
        on the sample time supplied. It uses the mean of the values within the resolution interval. It uses the pandas
        dataframe module `df.resample`

        Parameters
        ----------
        df :
            `df` is a sample-time indexed pandas dataframe containing measurement values from the different channels of
            each meter.
        sample_time :
            `sample_time` determines the desired resolution of the downsampled data. For 1 minute - 1T, 1 hour - 1H,
            1 month - 1M, 1 Day - 1D etc. The default chosen here is 1 minute.

        Returns
        -------
        Dataframe
            Resampled-time indexed pandas dataframe containing downsampled measurement values from the given dataframe.
        """
    # Data is downsampled using the mean of the values within the interval of the sample time provided.
    # The mean is used because it provided the average/expected value of the measurement within that time range.
    df_resampled = df.resample(sample_time, closed="left", label="right").mean()

    return df_resampled


def build_interpolation(y_values, n_val):
    """
        This function takes performs the actual 1-d interpolation. If the number of consecutive missing points is less
        than 3, a linear interpolation is used, else, a cubic interpolation is used.

        Parameters
        ----------
        y_values :
            `y_values` are the values on which the function interpolation is built, that is, y_values = f(x).
        n_val :
            `n_val` is the number of consecutive missing points that needs to be filled.

        Returns
        -------
        y_interp
            Array of interpolated values equal in length to the missing supplied length (n_val) of missing data points..
        """
    # removes the NaN values so as not to skew the performance of the scipy interp1d function.
    y_values = y_values.dropna()
    x = np.linspace(1, len(y_values), num=len(y_values))
    # x = np.reshape(x, y_values.shape)
    y_values = np.asarray(y_values).squeeze()
    # pdb.set_trace()
    # if-else uses a linear interpolation when the number of consecutive missing data points is less than 3.
    #  The number of points to be interpolated has to be greater than 3 points to use the spline/Cubic interpolation
    if len(y_values) <= 3:
        f = interp1d(x, y_values, kind='linear')
    else:
        f = interp1d(x, y_values, kind='cubic')

    x_interp = np.linspace(1, len(y_values), num=n_val)
    y_interp = f(x_interp)

    return y_interp


def compute_interpolation(df):
    """
        This function imputes missing measurement data (Nan) in a series using 1-d interpolation.

        Parameters
        ----------
        df :
            `df` is a series containing missing measurements values.

        Returns
        -------
        Series
            Filled pandas series with no missing values.
        """
    # creates a deep copy of the Series received
    test_df = df.copy()
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
        # range before and after the NaN data points
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
        test_df.iloc[val] = y_interp

    return test_df


def data_impute(impute_df):
    """
        This function imputes missing measurement in a dataframe using a 1-d interpolation. If the number of consecutive
        missing points is less than 3, a linear interpolation is used, else, a cubic interpolation is used.

        Parameters
        ----------
        impute_df :
            `impute_df` can either be a dataframe of a dictionary of dataframes containing missing measurements values.

        Returns
        -------
        Dataframe
            Filled pandas dataframe with no missing values.
        """
    # if-else checks if the input is a dataframe or list of dataframes.
    if isinstance(impute_df, dict):
        for meter in impute_df:
            if impute_df[meter].isnull().values.any():
                impute_df[meter] = impute_df[meter].apply(compute_interpolation)
    else:
        if impute_df.isnull().values.any():
            impute_df = impute_df.apply(compute_interpolation)

    return impute_df


def long_missing_data_prep(dirpath, filename):
    """
        This function prepares a dataset in a `csv` format with missing days, months or years for interpolation
        using the `data_impute` function. It fills in the missing time as a 'DateTimeIndex' and assigns a value
        of NaN to the missing data points.

        Parameters
        ----------
        dirpath :
            `dirpath` is the directory path location of the csv file containing the missing data points in already
            down-sampled to a 1-Minute interval.
        filename :
            `filename` is the csv file containing the missing data points to be read.

        Returns
        -------
        Dataframe
            pandas dataframe with 'DateTimeIndex' and value of NaN assigned to the missing data points.
        """
    # Reads dataset into a Pandas Dataframe
    meter_df = pd.read_csv(os.path.join(dirpath, filename))
    # Converts the time column to a DateTimeIndex format
    meter_df.set_index(pd.to_datetime(meter_df['time']), inplace=True)
    st_time = meter_df['time'].iloc[0]
    sp_time = meter_df['time'].iloc[-1]
    # Generates a date time range at an interval of 1 minute from the start and end date of the dataset.
    date_idx = pd.date_range(start=st_time, end=sp_time, freq='1T')
    meter_df.drop(columns=['time'], inplace=True)
    # Reindex the dataframe to include the DateTimeIndex for the missing days and NaN values for missing points
    meter_mod_df = meter_df.reindex(date_idx)

    return meter_mod_df



