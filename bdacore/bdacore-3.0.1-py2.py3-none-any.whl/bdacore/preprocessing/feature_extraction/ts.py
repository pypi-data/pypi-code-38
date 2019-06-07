import pandas as pd

__author__ = "VLE"
__copyright__ = "Copyright 2018, OCTO Technology"
__version__ = "0.1"
__email__ = "vlevorato@octo.com"


def transform_datetxt2int(X, col_date, format='%Y-%m-%d'):
    """
    Inplace transformation of a string date column into an integer format date column.
    
    Parameters
    ----------
    X: dataframe
    
    col_date: str
        Column name to transform
        
    format: str
        Pandas date str format

    """

    X[col_date] = pd.to_datetime(X[col_date], format=format)
    X[col_date] = X[col_date].map(lambda x: (x.year * 10 ** 4) + (x.month * 10 ** 2) + x.day)
    X[col_date] = X[col_date].astype('int')


def create_diff_shift_features(df_shift, cols=[], prefix='diff_'):
    """
    Create diff values between time series columns with have been shifted.
    
    Parameters
    ----------
    df_shift: dataframe
        Dataset with columns to make apply diff.
    cols: list
        Columns names, in order, to apply diff.
    prefix: str
        Prefix used to name diff columns.

    """
    for i in range(0, len(cols) - 1):
        df_shift[prefix + cols[i + 1] + '_' + cols[i]] = df_shift[cols[i + 1]] - df_shift[cols[i]]
