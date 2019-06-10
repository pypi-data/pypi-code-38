"""
Functions to deal with Dow Jones Financial Data.

The Dow Jones Financial Data data contains quarterly time series of revenue as reported on the Income
Statements for 30 publicly traded companies that comprise the Dow Jones
Industrial Average Index as of July 2015.
All numbers are in millions of US dollars.
The source of the data is the MSN Money API.

The source file has three columns, delimited by tabs:

  1) quarter_start - date that signifies beginning of a quarter, in
     YYYY-MM-DD format.
     Each company has data from 2000-01-01 to 2015-04-01, inclusive,
     with the exception of the Visa corporation, whose data starts on
     2006-04-01.

  2) company_ticker - the NYSE ticker for each of the companies.
     The following companies are present in the file:
       AAPL : Apple
       AXP  : American Express
       BA   : Boeing
       CAT  : Caterpillar
       CSCO : Cisco Systems
       CVX  : Chevron
       DD   : DowDuPont (since then renamed to DWDP)
       DIS  : Walt Disney
       GE   : General Electric
       GS   : Goldman Sachs
       HD   : The Home Depot
       IBM  : IBM
       INTC : Intel
       JNJ  : Johnson & Johnson
       JPM  : JPMorgan Chase
       KO   : Coca-Cola
       MCD  : McDonald's
       MMM  : 3M
       MRK  : Merck
       MSFT : Microsoft
       NKE  : Nike
       PFE  : Pfizer
       PG   : Procter & Gamble
       TRV  : Travelers
       UNH  : UnitedHealth Group
       UTX  : United Technologies
       V    : Visa
       VZ   : Verizon
       WMT  : Walmart
       XOM  : ExxonMobil

  3) revenue - quarterly revenue for the company in millions of US dollars
"""
import os
import inspect

import numpy as np
import pandas as pd

from automl.client.core.common.time_series_data_frame import TimeSeriesDataFrame

DOW_JONES_FILE_NAME = 'dow_jones_data.tsv'
DOW_JONES_DATA_PATH = os.path.dirname(os.path.abspath(inspect.getfile
                                                      (inspect.currentframe())))


def load_dow_jones_dataset(path_to_file=DOW_JONES_DATA_PATH, test_size=4):
    """
    Load Dow Jones Data from .tsv file into TimeSeriesDataFrame.

    .. _pandas.read_table: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_table.html

    :param path_to_file:
        Full path of the file containing Dow Jones data.
    :type path_to_file:
        string.
    :param test_size:
        The number of data points 'per grain' that are set aside for test data.
    :type test_size:
        int.
    :return:
        A 2-tuple of TimeSeriesDataFrame objects, first element is training data
        and second element is test data

    """
    # checking inputs
    if test_size < 0:
        raise ValueError("Expected 'test_size' > 0, got {}".format(test_size))
    assert os.path.exists(path_to_file)
    # start working
    df = pd.read_table(os.path.join(path_to_file, DOW_JONES_FILE_NAME),
                       low_memory=False)
    df['quarter_start'] = pd.to_datetime(df['quarter_start'])
    tsdf = TimeSeriesDataFrame(df, time_colname='quarter_start',
                               grain_colnames=['company_ticker'],
                               ts_value_colname='revenue')
    grouped_data = tsdf.groupby(level=tsdf.grain_colnames)
    # check if test_size is too small
    min_rows_per_grain = np.min(grouped_data.count().values)
    if (test_size > min_rows_per_grain - 1):
        raise ValueError(
            "With 'test_size' of {}, some grains won't have enough data!".format(
                test_size))
    # continue with the split
    train_data = grouped_data.apply(lambda x: x[:(len(x) - test_size)])
    train_data.deduplicate_index(inplace=True)
    test_data = grouped_data.apply(lambda x: x[(len(x) - test_size):])
    test_data.deduplicate_index(inplace=True)
    return train_data, test_data


if __name__ == "__main__":
    train, test = load_dow_jones_dataset()
    print(train.head())
    print(train.info())
    print(train.shape, test.shape)
