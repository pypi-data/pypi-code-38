# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
#  This code is licensed under MIT license (see license.txt for details)

import pandas as pd
from datetime import datetime
from pandas._libs.tslibs.strptime import array_strptime
from pandas._libs import tslib
from pandas.core.dtypes.generic import ABCIndexClass, ABCSeries
from pandas.core.dtypes.common import is_list_like
from pandas import Series, DatetimeIndex

"""
Provides extended datetime functionality for pandas dataframes
to handle epoch times using the format %s for seconds since the epoch
"""


def is_numeric(series_or_string):
    """
    Returns whether the series or string isnumeric
    """
    if isinstance(series_or_string, pd.Series):
        return pd.np.isreal(series_or_string).all()
    else:
        try:
            float(series_or_string)
            return True
        except ValueError:
            return False


def string_to_datetime(series_or_string, format, errors="raise"):
    """
    Converts a series (or string) to a timestamp according
    to the passed format string.
    """
    if format == "%s":
        if errors == "raise" and not is_numeric(series_or_string):
            raise ValueError()
        else:
            return pd.to_datetime(series_or_string, unit='s', errors=errors)
    else:
        # hard coded subset of pd.to_datetime to prevent automatic recognition of ISO8601 format
        if isinstance(series_or_string, tslib.Timestamp):
            return DatetimeIndex(series_or_string)
        elif isinstance(series_or_string, ABCSeries):
            values = array_strptime(series_or_string._values, format, exact=True, errors=errors)
            return Series(DatetimeIndex(values), index=series_or_string.index, name=series_or_string.name)
        elif isinstance(series_or_string, ABCIndexClass):
            return DatetimeIndex(array_strptime(series_or_string._values, format, exact=True, errors=errors))
        elif is_list_like(series_or_string):
            return DatetimeIndex(array_strptime(series_or_string._values, format, exact=True, errors=errors))
        else:
            return DatetimeIndex(array_strptime(pd.Series([series_or_string]).values, format, exact=True, errors=errors))[0]


def _datetime_to_string(timestamp, format):
    try:
        if format == "%s":
            return "{0:.0f}".format((timestamp - datetime(1970, 1, 1)).total_seconds())
        else:
            return timestamp.strftime(format)
    except ValueError:
        return None


def datetime_to_string(timestamp, format):
    """
    Takes an individual timestamp and returns a string according to
    the passed format
    """
    if type(timestamp) is pd.Series:
        return timestamp.apply(lambda x: _datetime_to_string(x, format))
    else:
        return _datetime_to_string(timestamp, format)


def format_string_is_valid(format):
    """
    Checks a format string to see whether it returns anything date like
    """
    date1 = datetime(1, 2, 3, 4, 5, 6, 7)
    date2 = datetime(8, 9, 10, 11, 12, 13, 14)
    if _datetime_to_string(date1, format) == _datetime_to_string(date2, format):
        return False

    return True
