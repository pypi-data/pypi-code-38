# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
A module that contains the definition of TimeSeriesDataFrame class.

This class is catered to handle several time series within a single
multi-index dataframe.
"""
from typing import Any, DefaultDict, Dict, List, Optional, Union
from collections import defaultdict, Iterable
import json
from math import floor
from warnings import warn, catch_warnings, simplefilter

import numpy as np
import pandas as pd
from pandas.core.indexes.multi import MultiIndex
from pandas.tseries.frequencies import to_offset
from pandas.tseries import offsets

from automl.client.core.common import forecasting_verify as verify
from automl.client.core.common.forecasting_exception \
    import (DataFrameValueException, DataFrameTypeException, NotSupportedException, DataFrameMissingColumnException,
            DataFrameIncorrectFormatException, DataFrameFrequencyException)
from automl.client.core.common.forecasting_ts_utils import datetime_is_date
from automl.client.core.common.forecasting_utils import (grain_level_to_dict,
                                                         get_period_offsets_from_dates,
                                                         make_groupby_map)
from automl.client.core.common.forecasting_verify import (ALLOWED_TIME_COLUMN_TYPES,
                                                          is_datetime_like,
                                                          is_collection)


pd.set_option('display.float_format', lambda x: '%.2f' % x)
# Common reset_index warning message
RESET_TIME_INDEX_MSG = \
    'Cannot reset time index. Use reindex to change its values.'
FREQ_NONE_VALUE = None
FREQ_NONE_VALUE_STRING = 'None'


def _get_smallest_gap(input_array):
    """Get the smallest gap from array-like variable l."""
    if len(input_array) < 2:
        return None

    input_array = np.array(input_array)
    input_array = np.sort(input_array)
    return np.min(input_array[1:] - input_array[:-1])


def _check_single_grain_time_index_duplicate_entries(time_index_column):
    if time_index_column.duplicated(keep=False).any():
        return True
    else:
        return False


def _check_single_grain_time_index_na_entries(time_index_column):
    if time_index_column.isnull().any():
        return True
    else:
        return False


def _ts_single_grain_clean(time_index_column):
    if _check_single_grain_time_index_duplicate_entries(time_index_column):
        # if there are duplicate entries in the time index, drop the duplicates
        time_index_column = time_index_column.drop_duplicates()

    if _check_single_grain_time_index_na_entries(time_index_column):
        # if there are NAs in the time index, drop the NAs
        time_index_column = time_index_column.dropna()

    # sort the time_index_column first
    time_index_column = time_index_column.sort_values()

    return time_index_column


def _infer_freq_single_grain_special_cases(time_index_column):
    """
    Infer frequency for some special cases where pandas.infer_freq() fails.

    e.g the time index have only 2 values or the time
    index have some gaps in the data however under some scenarios the
    frequency can be properly inferred.

    Currently, the cases handled in this function are all with granularity
    larger than a day, e.g weekly, monthly, quarterly and yearly. If in future,
    more special cases are discovered, feel free to add those cases to this
    function here.
    """
    freq_none_value = FREQ_NONE_VALUE

    # only infer on time index with more than or equal to 2 entries
    if len(time_index_column) < 2:
        return freq_none_value

    if datetime_is_date(time_index_column):
        # if there is no hour, minute and second parts in any of the entries,
        # mean all the entries are at least at date granularity

        # yearly
        if time_index_column.is_year_end.all():
            n = _get_smallest_gap(time_index_column.year)
            return offsets.YearEnd(n=n, month=12)
        elif time_index_column.is_year_start.all():
            # YS is new in pandas 0.21.
            n = _get_smallest_gap(time_index_column.year)
            return offsets.YearBegin(n=n, month=1)
        elif len(time_index_column.month.unique()) == 1 \
                and len(time_index_column.day.unique()) == 1:
            n = _get_smallest_gap(time_index_column.year)
            return offsets.DateOffset(years=n)

        # quarterly
        elif time_index_column.is_quarter_end.all():
            n = _get_smallest_gap(time_index_column.year *
                                  4 + time_index_column.quarter)
            return offsets.QuarterEnd(n=n, startingMonth=12)
        elif time_index_column.is_quarter_start.all():
            n = _get_smallest_gap(time_index_column.year * 4 +
                                  time_index_column.quarter)
            return offsets.QuarterBegin(n=n, startingMonth=1)

        # monthly
        elif time_index_column.is_month_end.all():
            n = _get_smallest_gap(time_index_column.year * 12 +
                                  time_index_column.month)
            return offsets.MonthEnd(n=n)
        elif time_index_column.is_month_start.all():
            n = _get_smallest_gap(time_index_column.year * 12 +
                                  time_index_column.month)
            return offsets.MonthBegin(n=n)
        elif len(time_index_column.day.unique()) == 1:
            n = _get_smallest_gap(time_index_column.year * 12 +
                                  time_index_column.month)
            return offsets.DateOffset(months=n)

        # weekly
        elif len(time_index_column.weekday.unique()) == 1:
            weekday = time_index_column.weekday.unique()[0]
            n = floor(((time_index_column[1:] - time_index_column[:-1]) /
                       np.timedelta64(7, 'D')).min())
            return offsets.Week(weekday=weekday, n=n)

    return freq_none_value


def _infer_freq_single_grain(time_index_column, return_freq_string=False):
    """
    Infer the frequency from a time index column.

    :param time_index_column: pandas.DatetimeIndex
    :param return_freq_string: boolean
        Whether to return the frequency string instead of pandas.DateOffset.
    :return: pandas.DateOffset or string 'None' if no frequency is inferred.
    """
    time_index_column = _ts_single_grain_clean(time_index_column)

    freq_none_value = FREQ_NONE_VALUE

    if len(time_index_column) == 0:
        # if no input entries in the input time index, None will be returned.
        return freq_none_value

    if len(time_index_column) == 1:
        return freq_none_value
    elif len(time_index_column) == 2:
        freq = _infer_freq_single_grain_special_cases(time_index_column)
        if freq is freq_none_value:
            time_delta = time_index_column[1] - time_index_column[0]
            freq = to_offset(time_delta)
    else:
        # Note: pd.infer_freq can only infer frequency with time index having
        # length>=3.
        freq = pd.infer_freq(time_index_column)
        if freq is not freq_none_value:
            freq = to_offset(freq)
        else:
            freq = _infer_freq_single_grain_special_cases(time_index_column)
            if freq is freq_none_value:
                # infer with the shortest time gap
                time_gap = time_index_column[1:] - time_index_column[:-1]
                freq = to_offset(time_gap.min())

    if return_freq_string:
        return freq.freqstr
    else:
        return freq


def _check_single_grain_time_index_regular_freq(time_index_column, freq=None,
                                                turn_auto_infer_off=False):
    """
    Check single grain time index with regular frequency.

    :param time_index_column: pandas.DatetimeIndex
    :param freq: string or pandas offset object
        The default is None, where the frequency will be inferred.
    :param turn_auto_infer_off: boolean
        If True, there will be no frequency inferring when the freq is None.
    :return: boolean
        return True if the time index has regular frequency conforms to the
        frequency specified in the freq argument, which means that
        the time index does not have any datetime gap after duplicate
        and NA/empty entries are dropped.
    """
    time_index_column = _ts_single_grain_clean(time_index_column)

    if freq is None:
        if turn_auto_infer_off:
            return False
        # if freq is None, we try to infer the frequency first.
        freq = _infer_freq_single_grain(time_index_column)

        if freq is FREQ_NONE_VALUE:
            # if freq is still None after the infer
            # This is a irregular ts with frequency cannot be inferred.
            return False

    try:
        # if the time_index_column can pass the frequency check
        # in the DatetimeIndex initializer
        # we claim this is a time index with regular frequency
        time_index_column = pd.DatetimeIndex(time_index_column, freq=freq)
        return True
    except ValueError:
        return False

# fill the datetime gap for TimeSeriesDataFrame for a single slice_key


def _fill_datetime_gap_single_slice_key(df, grain_level, freq, origin=None,
                                        end=None):
    if origin is not None:
        min_time = origin
    else:
        # min_time = df[df.time_colname].min()
        min_time = df.time_index.min()

    if end is not None:
        max_time = end
    else:
        # max_time = df[df.time_colname].max()
        max_time = df.time_index.max()

    # df_time = df[df.time_colname].loc[
    #     (df[df.time_colname] >= min_time) & (df[df.time_colname] <= max_time)]
    df_time = df.time_index[(df.time_index >= min_time) &
                            (df.time_index <= max_time)]
    df_time = df_time.to_series()

    if isinstance(df_time.iloc[0], pd.Period):
        desired_time = pd.period_range(start=min_time, end=max_time, freq=freq)
    elif isinstance(df_time.iloc[0], pd.Timestamp):
        desired_time = pd.date_range(start=min_time, end=max_time, freq=freq)
    else:
        error_message = 'The time index is neither ' + \
            'pd.Timestamp/pd.DateTimeIndex nor pd.Period/pd.PeriodIndex'
        raise DataFrameValueException(error_message)

    time_not_desired = [i for i in df_time if i not in desired_time]

    if len(time_not_desired) > 0:
        error_message = 'in grain {}, '.format(grain_level) + \
            'the following dates {} '.format(time_not_desired) + \
            'do not align with the desired frequency {}'.format(freq)
        raise DataFrameFrequencyException(error_message)

    # Create a plain data frame with the filled datetimes (no gaps)
    # If there's a grain in the input, put in grain columns too
    df_filled = pd.DataFrame({df.time_colname: desired_time})
    if df.grain_colnames is not None:
        grain_assign_dict = grain_level_to_dict(
            df.slice_key_colnames, grain_level)
        df_filled = df_filled.assign(**grain_assign_dict)

    # Right merge the input with the filled data frame to get a filled tsdf
    result = df.merge(df_filled, how='right')

    return result


def _return_freq(freq, return_freq_string=False):
    """
    Return DateOffset object itself or DateOffset alias string.

    Based on the provided return_freq_string argument.

    :param freq: the input frequency
    :type freq: pandas.DateOffset
    :param return_freq_string:
        If True, return a frequency string; else return pandas.DateOffset.
    :type return_freq_string: boolean

    :return:
        If return_freq_string is True, return a frequency string; else return
        pandas.DateOffset.
    """
    if return_freq_string:
        return freq.freqstr
    else:
        return freq


class TimeSeriesDataFrame(pd.DataFrame):
    """
    A subclass of pandas.DataFrame with additional properties for time series analysis and forecasting.

    .. py:class:: TimeSeriesDataFrame
    A subclass of pandas.DataFrame with additional properties for time
    series analysis and forecasting.

    .. _pandas.DataFrame: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html
    .. _pandas.Types.Time: https://pandas.pydata.org/pandas-docs/stable/timeseries.html

    :param data: See pandas.DataFrame
    :param index: See pandas.DataFrame
    :param columns: See pandas.DataFrame
    :param copy: See pandas.DataFrame
    :param dtype: See pandas.DataFrame
    :param grain_colnames:
        Column labels identifying
        the grain columns.

        Grain columns are the columns that identify data
        belonging to the same grain in the real-world.

        Here are some simple examples -
        The following sales data contains two years
        of annual sales data for two stores. In this example,
        grain_colnames=['store'].

        >>>          year  store  sales
        ... 0  2016-01-01      1     56
        ... 1  2017-01-01      1     98
        ... 2  2016-01-01      2    104
        ... 3  2017-01-01      2    140

        Another sales data set contains two years of
        annual sales data for two products sold in two stores.
        Here, grain_colnames=['store', 'product'].

        >>>          year  store  product  sales
        ... 0  2016-01-01      1        1     56
        ... 1  2017-01-01      1        1     98
        ... 2  2016-01-01      2        1    104
        ... 3  2017-01-01      2        1    140
        ... 4  2016-01-01      1        2    100
        ... 5  2017-01-01      1        2    201
        ... 6  2016-01-01      2        2     65
        ... 7  2017-01-01      2        2     79
    :type grain_colnames: str, list or array-like

    :param time_colname:
        Column label identifying the time axis.
        The time column should be one of the following types:
        Timestamp, DatetimeIndex, Period, or PeriodIndex.
        See pandas.Types.Time
    :type time_colname: str

    :param ts_value_colname:
        Column label identifying the target column.
        The target is the primary quantity for forecasting.
    :type ts_value_colname: str

    :param group_colnames:
        Column labels identifying groups across multiple time series.
        :class:`ftk.models.regressionforecaster.RegressionForecaster` can learn
        a model on each of the groups defined by `group_colnames`.
    :type group_colnames: str, list, or array-like

    :param origin_time_colname:
        Column label identifying the origin date for the features
        of a given row.
    :type origin_time_colname: str

    Examples:
    >>> data1 = {'a': [1, 2, 3], 'b': [4, 5, 6], 'c': [15, 25, 30], 'd': [1, 1, 2],
    ...     'date': pd.to_datetime(['2017-01-01', '2017-01-02', '2017-01-03'])}
    >>> df1 = TimeSeriesDataFrame(data1, grain_colnames = ['a','b'], time_colname = 'date',
    ...                          ts_value_colname = 'c', group_colnames = 'd')
    >>> data2 = {'a': [1, 2, 3], 'b': [4, 5, 6], 'c': [15, 25, 30], 'd': [1, 1, 2],
    ...        'date': pd.date_range('2017-01-01', periods = 3, freq = 'D')}
    >>> df2 = TimeSeriesDataFrame(data2, grain_colnames = 'a', time_colname = 'date',
    ...                          ts_value_colname = 'a', group_colnames = ['b','c'])
    >>> data3 = {'a': [1, 2, 3], 'b': [4, 5, 6], 'c': [15, 25, 30], 'd': [1, 1, 2],
    ...        'month': pd.PeriodIndex(['2012-01', '2012-02', '2012-03'],
    ...                                dtype = 'period[M]', freq = 'M')}
    >>> df3 = TimeSeriesDataFrame(data3, grain_colnames = ['a', 'b'], time_colname = 'month',
    ...                          ts_value_colname = 'b')
    >>> data4 = {'a': [1,2,3], 'b': [4,5,6], 'c': [15, 25, 30], 'd': [1, 1, 2],
    ...        'month': [pd.Period('2012-01'), pd.Period('2012-02'), pd.Period('2012-03')]}
    >>> df4 = TimeSeriesDataFrame(data4, grain_colnames = 'a', time_colname = 'month',
    ...                           ts_value_colname = 'b', group_colnames =['c','d'])

    """

    @property
    def _constructor(self):
        return TimeSeriesDataFrame._internal_ctor

    _metadata = ['grain_colnames', 'time_colname',
                 'ts_value_colname', 'group_colnames',
                 'origin_time_colname']

    # this is the metadata fields that is used to generate the property slice_key_colnames
    _slice_key_metadata = ['grain_colnames', 'origin_time_colname']

    @classmethod
    def _internal_ctor(cls, *args, **kwargs):
        if 'time_colname' not in kwargs:
            kwargs['time_colname'] = None
        return cls(*args, **kwargs)

    @classmethod
    def identity_grain_level(cls):
        """Name when a TimeSeriesDataFrame doesn't have grain_colnames specified."""
        return '__identity_grain'

    def __init__(self, data, time_colname, index=None, columns=None, dtype=None,
                 copy=True, grain_colnames=None, origin_time_colname=None,
                 ts_value_colname=None, group_colnames=None):
        """Create a TimeSeriesDataFrame."""
        super(TimeSeriesDataFrame, self).__init__(data=data,
                                                  index=None,
                                                  columns=columns,
                                                  dtype=dtype,
                                                  copy=copy)

        # The TSDF time columns may be deserialized as int64, convert them to datetime safely.
        self._convert_int64_to_datetime([time_colname, origin_time_colname])
        self.grain_colnames = grain_colnames
        self.time_colname = time_colname
        self.origin_time_colname = origin_time_colname
        self.ts_value_colname = ts_value_colname
        self.group_colnames = group_colnames

        if self.time_colname is not None:

            # set the index of the TimeSeriesDataFrame
            # it also contains check for no duplicate entries for each index
            # combination.
            self._reset_tsindex()

        self._check_column_equal_across_origin()

    def __getstate__(self):
        """Get state."""
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        """Set state."""
        self.__dict__.update(state)

    @property
    def grain_colnames(self):
        """List of grain columns."""
        return self.__grain_colnames

    @grain_colnames.setter
    def grain_colnames(self, val):
        if val is None:
            # Pandas 0.23 prints warnings whenever a non-column property is
            #   assigned
            # i.e. Pandas base doesn't know we made grain, time, etc so it
            #  warns us about assignment since it thinks we might have created
            #  columns with names '__grain_colnames', '__time_colname', etc.
            #  These are not columns for us though, so just ignore these
            #    warnings.
            with catch_warnings():
                simplefilter('ignore')
                self.__grain_colnames = val
        else:
            if verify.is_iterable_but_not_string(val):
                for col in val:
                    if not isinstance(col, str):
                        raise NotSupportedException(
                            'grain_colnames must all be str.')
                    if col not in self.columns and col not in self.index.names:
                        raise DataFrameMissingColumnException('grain column %s is not found in dataframe.'
                                                              % col)
                with catch_warnings():
                    simplefilter('ignore')
                    self.__grain_colnames = list(val)
            elif isinstance(val, str):
                if val not in self.columns and val not in self.index.names:
                    raise DataFrameMissingColumnException('grain column %s is not found in dataframe.'
                                                          % val)
                with catch_warnings():
                    simplefilter('ignore')
                    self.__grain_colnames = list([val])
            elif (isinstance(val, list) and isinstance(val[0], int)) or isinstance(val, int):
                raise NotSupportedException(
                    'grain column must be specified by a str value')

    def _convert_int64_to_datetime(self, cols):
        """
        Convert columns to datetime[ns].

        If column is of type int64 assume that it contains time in
        milliseconds from the beginning of epoch.

        :param data: The data frame to set column value in.
        :type: data: DataFrame.
        :param cols: The names of a columns to be converted.
        :type cols: list.
        """
        for col in cols:
            if col is not None and col in list(self.columns.values) and \
                    not any(isinstance(self[col], time_col_type) for time_col_type in ALLOWED_TIME_COLUMN_TYPES):
                if self[col].dtype == 'int64':
                    self[col] = pd.to_datetime(self[col], unit='ms')
                else:
                    try:
                        self[col] = pd.to_datetime(self[col])
                    except TypeError:
                        # Unable to convert, giving up.
                        pass

    @property
    def time_colname(self):
        """Time axis column name."""
        return self.__time_colname

    @time_colname.setter
    def time_colname(self, val):
        if val is None:
            with catch_warnings():
                simplefilter('ignore')
                self.__time_colname = val
        else:
            if isinstance(val, str):
                if val not in self.columns and val not in self.index.names:
                    raise DataFrameMissingColumnException(
                        'time column %s is not found in dataframe.'
                        % val)
                self._check_time_column(val)

                with catch_warnings():
                    simplefilter('ignore')
                    self.__time_colname = val
            else:
                raise NotSupportedException(
                    'time column must be specified by a single str value')

    @property
    def time_index(self):
        """
        Time axis of the data frame as a pandas.DatatimeIndex.

        .. _pandas.DatatimeIndex: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DatetimeIndex.html
        """
        return self.index.get_level_values(self.time_colname) \
            if self.time_colname is not None else None

    @property
    def origin_time_colname(self):
        """
        Name of column that contains origin_time values.

        For every observation,
        origin time indicates the latest date from which actual values
        were used to construct features.
        """
        return self.__origin_time_colname

    @origin_time_colname.setter
    def origin_time_colname(self, val):
        if val is None:
            with catch_warnings():
                simplefilter('ignore')
                self.__origin_time_colname = val
        else:
            if isinstance(val, str):
                if val not in self.columns and val not in self.index.names:
                    raise DataFrameMissingColumnException(
                        'origin time column %s is not found in dataframe.'
                        % val)
                self._check_time_column(val)

                with catch_warnings():
                    simplefilter('ignore')
                    self.__origin_time_colname = val

            else:
                raise NotSupportedException(
                    'origin time column must be specified by a single str value')

    @property
    def origin_time_index(self):
        """
        Origin times from the data frame as a pandas.DatatimeIndex.

        .. _pandas.DatatimeIndex: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DatetimeIndex.html
        """
        return self.index.get_level_values(self.origin_time_colname) if \
            self.origin_time_colname is not None else None

    @property
    def slice_key_colnames(self):
        """
        List of columns which are sufficient to identify a unique time series.

        The slice key is currently grain_colnames + origin_time_colname.

        Subclasses of TimeSeriesDataFrame may need to implement their
        own versions of this property as needed.
        """
        slice_key_colnames = []     # type: List[str]
        for attr_name in self._slice_key_metadata:
            # check whether self has attr_name
            # this check is introduced because the following example:
            # In the MultiForecastDataFrame constructor, "Super(
            # MultiForecastDataFrame, self).__init__" gets called before the
            # metadata setters, here this check basically handles the
            # situation when there are non-set attributes.
            if hasattr(self, attr_name):
                attr = getattr(self, attr_name)
                if attr is None:
                    attr = []
                elif isinstance(attr, str):
                    attr = [attr]
                elif isinstance(attr, dict):
                    # if the value of the metadata field is dictionary, such as
                    # model_names in MultiForecastDataFrame, values of the
                    # dictionary will be extracted.
                    # The assumption is that: the value of the dictionary are the
                    #  column names in the data frame.
                    attr = [value for key, value in attr.items()]
                elif not verify.is_iterable_but_not_string(attr):
                    raise DataFrameValueException('The metadata field {0} has '
                                                  'value {1}, which is not '
                                                  'string, list, dictionary, or '
                                                  'None'.format(attr_name, attr))

                slice_key_colnames.extend(attr)

        if len(slice_key_colnames) == 0:
            return None

        return slice_key_colnames

    @property
    def time_and_grain_colnames(self):
        """List containing time_colname + grain_colnames."""
        time_colname = [self.time_colname]
        if self.grain_colnames is None:
            grain_colnames = []     # type: List[str]
        else:
            grain_colnames = self.grain_colnames
        return time_colname + grain_colnames

    @property
    def horizon(self):
        """
        Horizon for each row, defined by time_index - origin_time_index.

        If origin_time_colname is not set, horizon=None.
        This property has type pandas.TimedeltaIndex.

        .. _pandas.TimedeltaIndex: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.TimedeltaIndex.html
        """
        if self.origin_time_colname is not None:
            val = self.time_index - self.origin_time_index
            val.name = 'horizon'
        else:
            val = None
        return val

    @property
    def frequency(self):
        """
        Frequency of the TimeSeriesDataFrame, as inferred by pandas.infer_freq.

        If the data frame contains multiple grains with
        different inferred frequencies, the frequency with the most
        occurrences is used.
        """
        return self.infer_freq()

    def _get_index_by_names(self, index_names):
        """
        Return any requested subset of the TSDF index.

        :param index_names: names of index columns to return
        :type index_names: str or iterable of strings
        """
        if verify.is_iterable_but_not_string(index_names) and \
                len(index_names) > 1:
            index_indices = [self.index.get_level_values(
                col) for col in index_names]
            return pd.MultiIndex.from_arrays(index_indices)
        elif isinstance(index_names, str):
            return self.index.get_level_values(index_names)
        elif isinstance(index_names[0], str):
            return self.index.get_level_values(index_names[0])
        else:
            return None

    @property
    def grain_index(self):
        """
        Grain columns as an index.

        If there are multiple grain columns,
        this property is a pandas.MultiIndex.

         .. _pandas.MultiIndex: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.MultiIndex.html
        """
        return self._get_index_by_names(self.grain_colnames)

    @property
    def slice_key_index(self):
        """
        Slice key columns as a index.

        If there are multiple slice key columns,
        this property is a pandas.MultiIndex.

         .. _pandas.MultiIndex: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.MultiIndex.html
        """
        return self._get_index_by_names(self.slice_key_colnames)

    @property
    def ts_value_colname(self):
        """Column name of forecasting target value."""
        return self.__ts_value_colname

    @ts_value_colname.setter
    def ts_value_colname(self, val):
        if val is None:
            self.__ts_value_colname = val
        else:
            if isinstance(val, str):
                if val not in self.columns:
                    raise DataFrameMissingColumnException(
                        'value column %s is not found in dataframe.'
                        % val)
                if self.shape[0] > 0 and \
                        not all([isinstance(v, (int, float, np.number)) for v in self[val]]):
                    raise DataFrameTypeException(
                        'The value column must be a numeric type.')
                self.__ts_value_colname = val
            else:
                raise DataFrameTypeException(
                    'The ts_value_colname property must be a string.')

    @property
    def ts_value(self):
        """
        Target value of the data frame as a pandas.Series.

         .. _pandas.Series: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.html
        """
        if self.ts_value_colname is None:
            return None
        else:
            return self._extract_time_series()[self.ts_value_colname]

    @property
    def group_colnames(self):
        """List of group column names."""
        return self.__group_colnames

    @group_colnames.setter
    def group_colnames(self, val):
        my_group_colnames = None
        if val is None:
            if self.__grain_colnames is not None:
                my_group_colnames = self.__grain_colnames
        else:
            if isinstance(val, list) and isinstance(val[0], str):
                for col in val:
                    if col not in self.columns and col not in self.index.names:
                        raise DataFrameMissingColumnException(
                            'group column %s is not found in dataframe.'
                            % col)
                my_group_colnames = val
            elif isinstance(val, str):
                if val not in self.columns and val not in self.index.names:
                    raise DataFrameMissingColumnException(
                        'group column %s is not found in dataframe.'
                        % val)
                my_group_colnames = list([val])
            else:
                raise NotSupportedException(
                    'group column must be specified by a str value')

        with catch_warnings():
            simplefilter('ignore')
            self.__group_colnames = my_group_colnames

    @property
    def group(self):
        """
        Group columns for the data frame.

        .. Warning:: This accessor will fail if any columns in group
        are part of the index.
        Use with caution.
        """
        if len(verify.data_frame_properties_intersection(self.group_colnames,
                                                         self.slice_key_colnames)) > 0:
            raise DataFrameValueException(
                'Cannot return group column because some of the columns in '
                'group_colnames are part of the index.' +
                ' Not yet implemented.')

        return self[self.group_colnames] if self.group_colnames is not None else None

    def _extract_time_series(self, colnames=None):
        """
        Extract a time series.

        This function firstly checks whether the columns provided have the
        same value across different origin time given the same grain and time
        values.
        Then for each column, it will extract the unique value for that
        specific column for each grain and time values and return the result
        data frame.

        :param colnames: columns names to extract time series on
        :return:
            A dataframe containing the unique column values of
            each grain and time combination.
        :rtype: pandas.DataFrame
        """
        if verify.is_iterable_but_not_string(colnames):
            for col in colnames:
                if not isinstance(col, str):
                    raise ValueError('column must be of type {0}'.format(str))

        elif isinstance(colnames, str):
            colnames = [colnames]

        elif colnames is None:
            colnames = [self.ts_value_colname]

        else:
            raise DataFrameTypeException(
                'Unrecognized type: {0}'.format(type(colnames)))

        # check if columns are present in TSDF
        not_in_frame = [col for col in colnames
                        if col not in self.columns]
        if len(not_in_frame) > 0:
            error_message = ("Columns {} not found in the ".format(not_in_frame) +
                             "TimeSeriesDataFrame!")
            raise DataFrameValueException(error_message)

        # check if the columns satisfy extraction criteria
        for col in colnames:
            self._check_column_equal_across_origin(col)

        # Now that check is passed, extract the values
        # Cast to data frame since selection may not be a valid TSDF
        as_df = pd.DataFrame(self[colnames], copy=False)

        if self.origin_time_colname is None:
            # No origin times, so just copy selection
            series_df = as_df.copy()

        else:
            # Extract unique series from time/grain groups
            series_df = (as_df
                         .groupby(level=self.time_and_grain_colnames,
                                  group_keys=False)
                         .first())

        return series_df

    def _verify_datetime_like(self, data):
        return is_datetime_like(data)

    def _check_time_column(self, col):
        if col in self.index.names:
            if not self.index.get_level_values(col).dtype == 'datetime64[ns]':
                if not all(self._verify_datetime_like(d)
                           for d in self.index.get_level_values(col)):
                    raise (DataFrameTypeException(
                        'The type of time column must be one of the following:\n{0}'.
                        format('\n'.join(str(t) for t in ALLOWED_TIME_COLUMN_TYPES))))
        elif col in self.columns:
            if not self[col].dtype == 'datetime64[ns]':
                if not all(self._verify_datetime_like(d) for d in self[col]):
                    raise (DataFrameTypeException(
                        'The type of time column must be one of the following:\n{0}'.
                        format('\n'.join(str(t) for t in ALLOWED_TIME_COLUMN_TYPES))))
        else:
            raise DataFrameMissingColumnException(
                'time column %s is not found in dataframe.' % col)

    def _to_datetime_index_func(self, time_index, format=None, *args, **kwargs):
        """
        Turn the column/index named col_name into pd.DatetimeIndex.

        :param time_index: datetime-like array
            The time index array to be turned into pd.DatetimeIndex.
        :param format: string
            strftime to parse time, eg %d/%m/%Y,
            note that %f will parse all the way up to nanoseconds.
            See pandas.to_datetime for more information.
        :param *args: Positional arguments could be passed to pd.to_datetime.
        :param **kwargs: Keyword arguments could be passed to pd.to_datetime.
        """
        if isinstance(time_index, pd.DatetimeIndex):
            # if the column is already pd.DatetimeIndex, do nothing
            return time_index

        try:
            if isinstance(time_index.iloc[0], pd.Period):
                time_index = pd.DatetimeIndex(
                    time_index.apply(lambda x: x.to_timestamp()))
            else:
                time_index = pd.DatetimeIndex(
                    pd.to_datetime(time_index, format=format, *args,
                                   **kwargs))
            # set the value of the column to be the time_index
            return time_index

        except ValueError:
            raise DataFrameValueException('Cannot turn the input into type'
                                          'pd.DatetimeIndex. Please check the '
                                          'values in the column to '
                                          'make sure each entry is '
                                          'datetime-like data.')

    def _check_column_equal_across_origin(self, colname=None):
        """
        Check whether the column value is consistent across origin times when the grain and time_index are the same.

        :param colname:
            The colname to check the origin time duplicates on.
        :type colname: str
        """
        if colname is None:
            colname = self.ts_value_colname

        if colname is not None:

            # check if the colname is a string
            if not isinstance(colname, str):
                raise ValueError('colname must be of type {0}'.format(str))
            # check if column is present in TSDF
            if colname not in self.columns:
                error_message = ("Column {} not found in the ".format(colname) +
                                 "TimeSeriesDataFrame!")
                raise DataFrameMissingColumnException(error_message)

            # we only need to check when origin_time_colname is not None
            if self.time_colname is not None \
                    and self.origin_time_colname is not None:
                if all([(name in self.index.names) for name in
                        self.time_and_grain_colnames]):
                    # if all columns from time_and_grain_colnames are in the index
                    values = self[colname].copy()
                    # Resetting index reduces groupby.apply computation time by 50%
                    values = values.reset_index()
                    grouped = values.groupby(self.time_and_grain_colnames)
                    # Operating on X[colname].values instead of
                    # X[colname] reduces computation time by 70%
                    all_equal = grouped.apply(
                        lambda X: all(x == X[colname].values[0]
                                      for x in X[colname].values) or
                        all(pd.isnull(X[colname].values)))
                else:
                    # This part is needed because some intermediate steps drop
                    # all the indices and the code above fails because the
                    # values series doesn't have any index
                    if all([(name in self.columns) for name in
                            self.time_and_grain_colnames]):
                        # if all columns from time_and_grain_colnames are in the
                        # column
                        grouped = self.groupby(self.time_and_grain_colnames)[
                            colname]
                    else:
                        # if columns from time_and_grain_colnames are with some
                        # in the index and some in the column
                        # turn self into pd.DataFrame to do the check
                        self_pandas_df_copy = pd.DataFrame(self)
                        self_pandas_df_copy = self_pandas_df_copy.reset_index()
                        grouped = self_pandas_df_copy.groupby(
                            self.time_and_grain_colnames)[colname]
                    all_equal = grouped.apply(
                        lambda X: all(x == X.values[0] for x in X.values) or all(
                            pd.isnull(X.values)))

                # we expect that colname values will be the same across
                # origin_time_colname as long as the grain_colnames and time_colname
                #  are the same
                if not np.all(all_equal.values):
                    error_message = "At least for one subset of data " \
                                    "which shares the same {}(grain_colnames) " \
                                    "and {}(time_colname) value," \
                                    "the values of {} are not equal acorss " \
                                    "different {}(origin_time_colname)".format(
                                        self.grain_colnames,
                                        self.time_colname, colname,
                                        self.origin_time_colname)
                    raise DataFrameIncorrectFormatException(error_message)

    def _reset_tsindex(self):
        """
        Call to reassign the index of a TimeSeriesDataFrame so it conforms to the prescribed design.

        The index consists of:
        1) time_colnames
        2) every column in slice_key_colnames.
        """
        index_keys = [self.time_colname]
        if self.slice_key_colnames is not None:
            index_keys = index_keys + self.slice_key_colnames

        if self.index.names != index_keys:
            if not isinstance(self.index, pd.Int64Index) or \
                    self._verify_datetime_like(self.index):
                super().reset_index(inplace=True)
            if any(self.duplicated(index_keys)):
                error_message = "There is more than one value for a " + \
                    "`time_index` and `grain` combination."
                error_detail = "Repeated labels are:" + str(
                    self[index_keys][self.duplicated(index_keys)])
                raise DataFrameIncorrectFormatException(
                    error_message, error_detail=error_detail)

            # convert column time_colname to type pd.DatetimeIndex
            self[self.time_colname] = self._to_datetime_index_func(
                self[self.time_colname], format=None)

            if self.origin_time_colname is not None:
                # convert column origin_time_colname to type pd.DatetimeIndex
                self[self.origin_time_colname] = self._to_datetime_index_func(
                    self[self.origin_time_colname], format=None)

            super(TimeSeriesDataFrame, self).set_index(
                index_keys, inplace=True)

            # check whether there are NA entries in self.time_index
            time_colname_null = self.time_index.isnull()
            if time_colname_null.any():
                # if there are any entries with NA value on self.time_index,
                # throw warning and remove those entries.
                warn('There are {0} rows that contains NA/empty value on '
                     'time index {1}, these rows will be removed from the data'
                     '.'.format(pd.Series(time_colname_null).value_counts()[True],
                                self.time_colname))

                super(TimeSeriesDataFrame, self).drop(
                    self.time_index[time_colname_null],
                    level=self.time_colname, inplace=True)

        return self

    def reindex(self, *args, **kwargs):
        """
        Override of pandas.reindex that respects TimeSeriesDataFrame metadata.

        .. _pandas.reindex: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.reindex.html

        :param *args: Positional arguments passed to pandas.reindex.
        :param **kwargs: Keyword arguments passed to pandas.reindex.
        """
        if 'time_colname' in kwargs:
            time_colname = kwargs['time_colname']
            kwargs.pop('time_colname')
        else:
            time_colname = None
        if 'grain_colnames' in kwargs:
            grain_colnames = kwargs['grain_colnames']
            kwargs.pop('grain_colnames')
        else:
            grain_colnames = None

        self = super(TimeSeriesDataFrame, self).reindex(*args, **kwargs)
        self._check_and_reset_metadata(time_colname=time_colname,  # pylint: disable=no-member
                                       grain_colnames=grain_colnames)

        return self

    def _check_and_reset_metadata(self, time_colname=None, grain_colnames=None):
        if time_colname is not None and time_colname != self.time_colname:
            old_time_name = self.time_colname
            self.time_colname = time_colname
            if time_colname not in self.index.names:
                super(TimeSeriesDataFrame, self).set_index(
                    time_colname, append=True, inplace=True)
                super(TimeSeriesDataFrame, self).reset_index(
                    level=old_time_name, drop=True, inplace=True)
        if grain_colnames is not None and grain_colnames != self.grain_colnames:
            if isinstance(grain_colnames, str):
                grain_colnames = [grain_colnames]
            if self.grain_colnames is not None:
                old_grain_colnames = list(set(self.grain_colnames).
                                          intersection(set(self.index.names))
                                          .difference(set(grain_colnames)))     # type: Optional[List[str]]
                self.grain_colnames = grain_colnames
                new_grain_colnames = list(
                    set(grain_colnames).difference(set(self.index.names)))
            else:
                old_grain_colnames = None
                self.grain_colnames = grain_colnames
                new_grain_colnames = list(
                    set(grain_colnames).difference(set(self.index.names)))
            missing_columns = list(
                set(new_grain_colnames).difference(set(self.columns)))
            if len(missing_columns) > 0:
                raise DataFrameMissingColumnException(
                    "Grain column {0} not in DataFrame".
                    format([missing_columns]))
            super(TimeSeriesDataFrame, self).set_index(
                new_grain_colnames, append=True, inplace=True)
            if old_grain_colnames is not None:
                super(TimeSeriesDataFrame, self).reset_index(
                    old_grain_colnames, inplace=True)

        if self.time_colname not in self.index.names:
            new_time_index = []
            for i in self.index.names:
                if self._verify_datetime_like(self[i][0]):
                    new_time_index.append(i)
            if len(new_time_index) > 1:
                warn("Could not determine which index column was the "
                     "time_index; defaulting to {0}".
                     format(new_time_index[0]), UserWarning)
            if len(new_time_index) == 0:
                warn("`time_colname` no longer in DataFrame index, "
                     "returning pandas.DataFrame", UserWarning)
                self = pd.DataFrame(self)
            else:
                self.time_colname = new_time_index[0]

        elif self.grain_colnames is not None:
            missing_grain = \
                list(set(self.grain_colnames).difference(set(self.index.names)))
            if len(missing_grain) != 0:
                warn("`grain_colnames` {0} no longer in index. "
                     "Removing them from `grain_colnames`.".
                     format(missing_grain))
                common_grain = \
                    list(set(self.grain_colnames).intersection(
                        set(self.index.names)))
                if len(common_grain) == 0:
                    self.grain_colnames = None
                else:
                    self.grain_colnames = common_grain
        return self

    def reset_index(self, level=None, inplace=False, **kwargs):
        """
        Reset the requested level of the DataFrame index.

        This method overrides pandas.reset_index
        so that it respects TimeSeriesDataFrame metadata.

        .. _pandas.reset_index:
        https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.reset_index.html

        :param level:
            Index level to reset. For TimeSeriesDataFrames, level
            can be a list of level names or integer indices to reset.
            E.g. level=tsdf.grain_colnames.
            If the requested level drops part of the grain index,
            self.grain_colnames will be updated to reflect the change.
            The time index cannot be reset.

        :param inplace:
            If true, reset index in place. Otherwise return
            a new TimeSeriesDataFrame with a reset index.
        :type inplace: boolean

        :param **kwargs: keyword arguments passed on to pandas.reset_index.

        :return:
            Dataframe with reset index if inplace=False,
            None if inplace=True
        :rtype: TimeSeriesDataFrame, None
        """
        # Can't drop the time index; figure out its level number for later
        # checks. It could be duplicated (pandas group-by/apply bug), so save
        # the *last* level that corresponds with the time index
        time_col_levels = [i for i, name in enumerate(self.index.names)
                           if name == self.time_colname]
        final_time_col_level = time_col_levels[-1]

        # Create a list of levels to reset from the input
        # We have to do a lot of checks here to make sure
        # we don't drop the time index
        levels_to_reset = []    # type: List[Any]
        if isinstance(level, str):
            if level == self.time_colname:
                warn(RESET_TIME_INDEX_MSG, UserWarning)
                return self if not inplace else None
            levels_to_reset = [level]
        elif isinstance(level, int):
            if level == final_time_col_level:
                warn(RESET_TIME_INDEX_MSG, UserWarning)
                return self if not inplace else None
            levels_to_reset = [level]
        elif verify.is_iterable_but_not_string(level) and len(level) > 0:
            if all(isinstance(l, str) for l in level):
                levels_to_reset = [lv for lv in level
                                   if lv != self.time_colname]
                if self.time_colname in level:
                    warn(RESET_TIME_INDEX_MSG, UserWarning)
            elif all(isinstance(l, int) for l in level):
                levels_to_reset = [lv for lv in level
                                   if lv != final_time_col_level]
                if final_time_col_level in level:
                    warn(RESET_TIME_INDEX_MSG, UserWarning)
            else:
                error_message = 'Unsupported types given for level values. ' + \
                    'Must be all strings or all ints.'
                raise DataFrameTypeException(error_message)
        elif level is None:
            levels_to_reset = [lv for lv in range(self.index.nlevels)
                               if lv != final_time_col_level]
            warn(RESET_TIME_INDEX_MSG, UserWarning)
        else:
            raise DataFrameTypeException(('Unsupported type given for level: ' +
                                          '{0}').format(type(level)))

        # Use DataFrame.reset_index as the inner loop
        out_df = super().reset_index(level=levels_to_reset,
                                     inplace=inplace,
                                     **kwargs)
        reset_df = self if inplace else out_df

        # Get a list representation of grain colnames
        if isinstance(self.grain_colnames, str):
            grain_cols = [self.grain_colnames]
        elif verify.is_iterable_but_not_string(self.grain_colnames):
            grain_cols = self.grain_colnames
        else:
            grain_cols = []

        # Update the grain colnames in case we removed any index levels that
        #   were part of the grain
        new_grain = [colname for colname in grain_cols
                     if colname in reset_df.index.names]
        reset_df.grain_colnames = new_grain if len(
            new_grain) > 0 else None

        reset_df.origin_time_colname = self.origin_time_colname \
            if self.origin_time_colname in reset_df.index.names else None

        return reset_df if not inplace else None

    def deduplicate_index(self, inplace=False, **kwargs):
        """
        Remove duplicated grain columns in the TimeSeriesDataFrame index.

        Used if during data frame manipulation, the grain columns become
        duplicated.  This sometimes occurs when moving grain columns in and out
        of data frame index.

        :param inplace:
            If true, remove duplicated in place. Otherwise return
            a new TimeSeriesDataFrame with duplicates removed.
        :type inplace: boolean

        :param **kwargs: keyword arguments passed on to
            TimeSeriesDataFrame.reset_index().
        :returns:
            TimeSeriesDataFrame with only unique columns in grain_index.
        """
        # collect all indices and note how many times they occur
        index_frequency = defaultdict(list)     # type: DefaultDict[str, List[int]]
        for i, index_name in enumerate(self.index.names):
            index_frequency[index_name].append(i)
        # now iterate over the dict, and find each key for which there are
        # multiple indices, and store the extra indices only if the index
        # values differ
        duplicate_indices = []
        for index_name, occurrences in index_frequency.items():
            if len(occurrences) > 1:
                # compare index values for same index name
                first_i = occurrences[0]
                for i in occurrences[1:]:
                    if not self.index.get_level_values(i).equals(
                            self.index.get_level_values(first_i)):
                        warn('not deduplicating index {} because index values '
                             'do not match'.format(index_name), UserWarning)
                    else:
                        duplicate_indices.extend(occurrences[1:])
        # if no duplicates found, just a pass-through
        if not duplicate_indices:
            result = self
        else:
            # going from right to left, drop duplicates one by one
            # going from left to right is not an option, as dropping
            # low-index columns changes indices for all subsequent columns :(
            # for i in sorted(, reverse=True):
            result = self.reset_index(level=duplicate_indices,
                                      inplace=inplace, drop=True, **kwargs)
            result = self if inplace else result
            # easiest way to make sure column order is as expected:
            # time first, grain second.
            result._reset_tsindex()
        # finally, return result or nothing
        return result if not inplace else None

    def set_index(self, *args, **kwargs):
        """
        Set the DataFrame index.

        This method overrides pandas.set_index
        so that it respects TimeSeriesDataFrame metadata.

        .. _pandas.set_index: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.set_index.html


        :param *args: Positional arguments passed on to pandas.set_index.
        :param **kwargs: Keyword arguments passed on to pandas.set_index.
        """
        new_arg_list = list(args)
        keys_to_add = []
        if 'time_colname' in kwargs:
            time_colname = kwargs['time_colname']
            keys_to_add.append(time_colname)
            kwargs.pop('time_colname')
            self.time_colname = time_colname
        else:
            if 'append' not in kwargs or not kwargs['append']:
                if self.time_colname in self.index.names:
                    self = super(TimeSeriesDataFrame, self).reset_index(
                        level=self.time_colname)
                keys_to_add = [self.time_colname]
            time_colname = None
        if 'grain_colnames' in kwargs:
            grain_colnames = kwargs['grain_colnames']
            if isinstance(grain_colnames, str):
                keys_to_add.append(grain_colnames)
            else:
                keys_to_add.extend(grain_colnames)
            kwargs.pop('grain_colnames')
            self.grain_colnames = grain_colnames
        else:
            if 'append' not in kwargs or not kwargs['append']:
                reset_grains = []
                for g in self.grain_colnames:
                    if g in self.index.names:
                        reset_grains.append(g)
                self = super(TimeSeriesDataFrame, self).reset_index(
                    level=reset_grains)
                keys_to_add.extend(self.grain_colnames)
            grain_colnames = None

        if 'keys' in kwargs:
            kwargs['keys'].extend(keys_to_add)
        elif len(new_arg_list) > 0:
            if isinstance(new_arg_list[0], str):
                new_arg_list[0] = [new_arg_list[0]] + keys_to_add
            elif verify.is_iterable_but_not_string(new_arg_list[0]):
                new_arg_list[0].extend(keys_to_add)
        else:
            kwargs['keys'] = keys_to_add

        self = super(TimeSeriesDataFrame, self).set_index(*new_arg_list, **kwargs)
        self = self._check_and_reset_metadata(time_colname=time_colname,
                                              grain_colnames=grain_colnames)

        return self

    def groupby_index_names(self, index_names, group_keys=False, **kwargs):
        """
        Group-by a list of columns in the data frame index.

        :param index_names: Names in index to group by
        :type index_name: list-like

        :param group_keys: boolean
        :param **kwargs:
            Additional keyword parameters to pass to DataFrame.groupby
        :return:
            pandas.GroupBy object
        """
        if index_names is None:
            grouped = self.groupby(by=lambda axis_label:
                                   self.identity_grain_level(),
                                   group_keys=group_keys, **kwargs)
        else:
            grouped = self.groupby(level=index_names,
                                   group_keys=group_keys, **kwargs)

        return grouped

    def groupby_slice_key(self, group_keys=False, **kwargs):
        """
        Group the TimeSeriesDataFrame by slice key.

        .. _DataFrame.groupby: https://pandas.pydata.org/pandas-docs/stable/api.html#groupby

        Useful for operations on individual time series within the
        TimeSeriesDataFrame. Each group in the output should contain
        a single time series.
        If the grain is not set, the result is a single group containing
        the whole TimeSeriesDataFrame

        :param group_keys:
            If True, add group keys to the index on apply.
            Default is False since the grain is usually part of the
            TimeSeriesDataFrame index already.

        :type group_keys: Boolean

        :param **kwargs: Additional keyword parameters to pass to DataFrame.groupby

        :returns: GroupBy object
        """
        return self.groupby_index_names(self.slice_key_colnames,
                                        group_keys=group_keys, **kwargs)

    def groupby_grain(self, group_keys=False, **kwargs):
        """
        Group the TimeSeriesDataFrame by grain.

        Useful for operations on individual time series within the
        TimeSeriesDataFrame. Each group in the output should contain
        a single time series.
        If the grain is not set, the result is a single group containing
        the whole TimeSeriesDataFrame

        :param group_keys:
            If True, add group keys to the index on apply.
            Default is False since the grain is usually part of the
            TimeSeriesDataFrame index already.
        :type group_keys: Boolean
        :param **kwargs:
            Additional keyword parameters to pass to DataFrame.groupby.

        :returns: GroupBy object
        """
        return self.groupby_index_names(self.grain_colnames,
                                        group_keys=group_keys, **kwargs)

    def groupby_group(self, group_keys=False, **kwargs):
        """
        Group the TimeSeriesDataFrame by group.

        Group columns can be regular data frame columns, indices, or both.

        If group is None, the result is a single group containing
        the whole TimeSeriesDataFrame.

        :param group_keys:
            If True, add group keys to the index on apply.
            Default is False since we usually don't want to
            modify the index of TimeSeriesDataFrame in groupby-apply
            operations.

        :type group_keys: Boolean

        :param **kwargs: Additional keyword parameters to pass to DataFrame.groupby

        :returns: GroupBy object
        """
        mapper = make_groupby_map(self, self.group_colnames)
        return self.groupby(mapper, group_keys=group_keys, **kwargs)

    def groupby_group_and_horizon(self, horizon_colname='horizon',
                                  group_keys=False, **kwargs):
        """
        Group the TimeSeriesDataFrame by the columns in the `group_colnames` property and the `horizon_colname`.

        :param horizon_colname:
            Column name used as horizon column for grouping. If the column
            does not exist in the data frame columns or index, a new column
            is computed by computing the time difference between `time_index`
            and `origin_time_index`. The value of this column is integer
            and the unit is the `frequency` of the TimeSeriesDataFrame.
            Note: If the `origin_time_colname` property is not set,
            the horizon column can not be computed and grouping is only done
            by `group_colnames`.
        :type horizon_colname: 'str'

        :param group_keys:
            If True, add group keys to the index on apply.
            Default is False since the grain is usually part of the
            TimeSeriesDataFrame index already.
        :type group_keys: Boolean

        :param kwargs:
            Additional arguments passed to `pandas.DataFrame.groupby`

        :return:
        """
        if self.frequency is None:
            raise NotImplementedError('Groupby horizon on data with '
                                      'irregular frequency is not '
                                      'implemented yet. Please preprocess '
                                      'the data so that it has regular '
                                      'frequency.')
        group_colnames_safe = self.group_colnames \
            if self.group_colnames is not None \
            else []
        groupby_items = group_colnames_safe + [horizon_colname]
        if self.origin_time_colname is not None:
            if horizon_colname not in self.columns and \
                    horizon_colname not in self.index.names:

                # Compute horizons as period offsets
                horizons = \
                    get_period_offsets_from_dates(self.origin_time_index,
                                                  self.time_index,
                                                  freq=self.frequency,
                                                  misalignment_action='warn')
                mapper = make_groupby_map(
                    self.assign(**{horizon_colname: horizons}), groupby_items)

            else:
                warn('Existing horizon column, {0}, is used for '
                     'grouping.'.format(horizon_colname))
                mapper = make_groupby_map(self, groupby_items)

        else:
            warn('The `origin_time_colname` is not set, grouping by '
                 '`group_colnames` only.')
            mapper = make_groupby_map(self, self.group_colnames)

        return self.groupby(mapper, group_keys=group_keys, **kwargs)

    def infer_freq_by_grain(self, return_freq_string=False):
        """
        Infer frequency for each grain.

        :param return_freq_string:
            Return a frequency string, as opposed to a pandas.DateOffset.
        :type return_freq_string: boolean
        :return: Inferred frequencies by grain.
        :rtype: pandas.DataFrame
        """
        # Can't infer the frequency without a time_colname
        if self.time_colname is None:
            raise DataFrameValueException(
                'Cannot infer frequency without a time index.')

        freq_by_grain = self.groupby_grain().apply(
            lambda d: _infer_freq_single_grain(
                d.time_index, return_freq_string=return_freq_string)
        )
        return freq_by_grain

    def infer_freq(self, return_freq_string=False):
        """
        Infer the frequency of the TimeSeriesDataFrame.

        If there are multiple frequencies found, this method
        returns the most common frequency and prints a warning.

        .. _offset-alias: https://pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases

        :param return_freq_string:
            If True, return a frequency string; else return pandas.DateOffset.
        :type return_freq_string: boolean

        :return:
            None if no frequency is inferred. If frequency is
            inferred, return pandas.DateOffset by default.
            Will return an offset alias (frequency string)
            if return_freq_string=True.
        """
        freq_by_grain = self.infer_freq_by_grain(
            return_freq_string=return_freq_string)

        # Need to break out the case when FREQ_NONE_VALUE is `None`
        #  because `None` is not a comparable object. i.e. `None == None`
        #  evaluates to False
        if FREQ_NONE_VALUE is None:
            freq_by_grain = freq_by_grain[freq_by_grain.notnull()]
        else:
            freq_by_grain = freq_by_grain.loc[
                freq_by_grain != FREQ_NONE_VALUE]

        if len(freq_by_grain) == 0:
            warn(
                'there is no frequency inferred. ',
                UserWarning)
            freq = None
        elif len(freq_by_grain.unique()) > 1:
            freq = \
                freq_by_grain.value_counts().sort_values(
                    ascending=False).index[0]
            print(
                'expect 1 distinct datetime frequency from all {1}(s) in the '
                'data, with {0} distinct datetime frequencies ({2}) inferred.'.
                format(len(freq_by_grain.unique()), self.grain_colnames,
                       freq_by_grain.unique()))
            warn(
                'return \'{0}\' as frequency. '.format
                (freq), UserWarning)
        else:
            freq = freq_by_grain.unique()[0]

        return freq

    def infer_single_freq(self, return_freq_string=False):
        """
        Get frequency for TSDF where a single uniform frequency across all time series could be inferred.

        Otherwise, None will be returned.

        .. _offset-alias: https://pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases

        :param return_freq_string:
            If True, return a frequency string; else return pandas.DateOffset.
        :type return_freq_string: boolean

        :return:
            None if no single uniform frequency is inferred. If frequency is
            inferred, return pandas.DateOffset by default.
            Will return an offset alias (frequency string)
            if return_freq_string=True.
        """
        freq_by_grain = self.infer_freq_by_grain(
            return_freq_string=False)

        if len(freq_by_grain) == 1:
            return _return_freq(freq_by_grain.values[0],
                                return_freq_string=return_freq_string)

        # the grains that cannot be inferred frequency means the time series
        # have lenghth exactly 1, because for time series have unique time
        # stamps larger than 1, there will always be frequency inferred.
        # we will revisit these grains' data later.
        index_df = self.index.to_frame(index=False)

        index_df_with_freq = index_df.merge(freq_by_grain.reset_index(
            name='freq'), on=self.grain_colnames, how='left')
        if index_df_with_freq['freq'].isnull().any():
            data_from_grains_with_null_freq = self.loc[
                index_df_with_freq['freq'].isnull().values]

        freq_by_grain = freq_by_grain.loc[freq_by_grain.notnull()]

        if len(freq_by_grain.unique()) == 1:
            return _return_freq(freq_by_grain.unique()[0],
                                return_freq_string=return_freq_string)

        # the name attribute of DateOffset object can be viewed as the unit of
        #  the DateOffset object, e.g a DateOffSet object QuarterBegin(n=1,
        # startingMonth=2) and QuarterBegin(n=2, startingMonth=2), will both
        # have name attribute equal to 'QS-FEB'
        try:
            freq_name_by_grain = freq_by_grain.apply(lambda x: x.name)
            if len(freq_name_by_grain.unique()) != 1:
                # if the basic units are different, then no uniform single
                # frequency could be inferred
                return None
        except NotImplementedError:
            warn('For one of the time series frequency, '
                 'the name of the DateOffset obejct is '
                 'not implemented by Pandas. Single '
                 'frequency inference will be always return as None.')
            return None

        # the n attribute for DateOffset object indicates how many basic
        # units are contained in this object, this is usually also an input
        # argument when initializing the objects. e.g QuarterBegin(n=2,
        # startingMonth=2) will have a n equal to 2.
        freq_n_by_grain = freq_by_grain.apply(lambda x: x.n)
        freq_smallest_n = freq_n_by_grain.min()
        freq_n_mod_smallest_n = freq_n_by_grain.apply(
            lambda x: x % freq_smallest_n)

        # if the frequencies are not the multiples of the smallest frequency,
        #  then no single uniform frequency will be inferred.
        if len(freq_n_mod_smallest_n.unique()) > 1:
            return None

        data_size_by_grain = self.groupby_grain().apply(
            lambda x: len(x.time_index.unique()))
        size_freq_and_n = pd.concat(
            [data_size_by_grain, freq_by_grain, freq_n_by_grain], axis=1)
        size_freq_and_n.columns = ['size', 'freq', 'n']

        # the inferred freq is the frequency satisfies:
        # (1) it is the mode frequency
        # (2) it has smallest number of the basic time unit (n)
        inferred_freq = size_freq_and_n.loc[
            (size_freq_and_n['freq'].isin(
                size_freq_and_n['freq'].mode().values)) &
            (size_freq_and_n['n'] == size_freq_and_n['n'].min()),
            'freq'].unique()

        if len(inferred_freq) == 0:
            # this means no such frequency is found.
            return None

        inferred_freq = inferred_freq[0]

        # we infer the single uniform frequency only when:
        # if all the time series, with different frequency than the
        # inferred_freq, have data size less than 3.
        # if there is any time series with different frequency with
        # length large or equal than 3, then we kind of think there is a
        # pattern showing the time series is "regularly" different than
        # the inferred frequency, thus no uniform single frequency can be
        #  inferred.
        ts_size_with_different_freq = size_freq_and_n.loc[
            size_freq_and_n['freq'] != inferred_freq, 'size']

        if ts_size_with_different_freq.max() >= 3:
            return None

        # check whether the data from grains with None frequency inferred
        # conform with the inferred single uniform frequency
        if index_df_with_freq['freq'].isnull().any():
            if not data_from_grains_with_null_freq.check_regularity(
                    freq=inferred_freq):
                return None

        return _return_freq(inferred_freq,
                            return_freq_string=return_freq_string)

    def check_duplicates(self, cols):
        """
        Check for duplicated values in index and/or data frame columns.

        :param cols:
            The column names that is incorporated into the duplication checking.
            The column name could either be index name or data frame column
            name.
        :type cols: list of str
        :return: True if there are duplicated values in the input columns
        :rtype: boolean
        """
        cols_in_index = [col for col in cols if col in self.index.names]
        cols_in_column = [col for col in cols if col in self.columns]
        cols_for_check = cols_in_index + cols_in_column

        if len(cols_in_index) > 0:
            # reset the index and get the resetted copy
            resetted = super(TimeSeriesDataFrame, self).reset_index(
                level=cols_in_index)
            return resetted.duplicated(cols_for_check).any()

        return self.duplicated(cols_for_check).any()

    def _check_regularity_single_grain(self, freq):
        """
        Check the time index regularity for data from a single series grain.

        :param df: TimeSeriesDataFrame
            The data from a single series grain.
        :param freq: string or pandas offset object
            The default is None, where the frequency will be inferred.
        :return: dict
            {'regular': bool, 'problems': list}
            A time index is defined as regular for a single grain if this time
            index:
            (1) there is no duplicate entries
            (2) there is no NA/empty entries
            (3) there is no datetime gap
        """
        #  origin_time_colname will be replaced by forecast grain

        problems_list = []

        columns_to_check_duplicates = [self.time_colname]
        if self.slice_key_colnames != self.grain_colnames:
            if self.grain_colnames is not None:
                columns_to_check_duplicates = columns_to_check_duplicates + \
                    [g for g in self.slice_key_colnames if g not in
                     self.grain_colnames]
            else:
                columns_to_check_duplicates = columns_to_check_duplicates \
                    + self.slice_key_colnames

        if self.check_duplicates(columns_to_check_duplicates):
            problems_list.append('Duplicate datetime entries exist')

        time_index_column = self.time_index

        if _check_single_grain_time_index_na_entries(time_index_column):
            problems_list.append('NA datetime entries exist')

        if not _check_single_grain_time_index_regular_freq(time_index_column, freq=freq,
                                                           turn_auto_infer_off=True):
            problems_list.append('Irregular datetime gaps exist')
        if len(problems_list) == 0:
            regular = True
        else:
            regular = False

        return {'regular': regular, 'problems': problems_list}

    def check_regularity_by_grain(self, freq=None):
        """
        Check the regularity of each time series in the data frame.

        A time series is regular if the following conditions hold:
        1. There are no irregular gaps in the time index
        2. There are no duplicated times in the time index
        3. There are no missing values in the time index

        If there are forecast related grain columns such as origin_time,
        the check of regularity will be conducted as follows:
        1. Make sure there is no duplicate time index for each full grain
           group. Here full grain means all grain columns, including series
           grain columns and forecast relate grain columns.
        2. Duplicate time index will be removed in each series grain group.
           Then the regularity will be determined for each de-deuplicated
           time index on each series grain group.

        :param freq:
            The frequency of the time series in the data frame
            If freq=None, the frequency will be inferred.
        :type freq: str or pandas.DateOffset object

        :return:
            Data frame with regularity check results in two columns:
            1. A boolean column called 'regular'
            2. A string column called 'problems'
               giving details of irregularities.
            The grain columns comprise the index.
        :rtype: pandas.DataFrame
        """
        if freq is None:
            freq = self.infer_freq()

        tsdf_bygrain = self.groupby_grain()

        if len(tsdf_bygrain) > 1:
            reg_results_bygrain = tsdf_bygrain.apply(lambda x: pd.Series(
                x._check_regularity_single_grain(freq=freq)))

        else:
            grain_name, grain_df = [(name, group) for name, group in
                                    tsdf_bygrain][0]
            grain_df._check_regularity_single_grain(freq=freq)
            reg_results_bygrain = pd.DataFrame(
                [grain_df._check_regularity_single_grain(freq=freq)],
                index=[grain_name])

        return reg_results_bygrain

    def check_regularity(self, freq=None):
        """
        Check the regularity of the whole data frame.

        The data frame is regular if every series in the
        data frame is regular

        :param freq:
            The frequency of the time series in the data frame
            If freq=None, the frequency will be inferred.
        :type freq: str or pandas.DateOffset object

        :return:
            True if all series in the frame are regular.
        :rtype: boolean
        """
        reg_results_bygrain = \
            self.check_regularity_by_grain(freq=freq)
        if reg_results_bygrain['regular'].all():
            return True
        else:
            return False

    # fill the datetime gap for TimeSeriesDataFrame
    def fill_datetime_gap(self, freq=None, origin=None, end=None):
        """
        Fill the datetime gaps in the TimeSeriesDataFrame.

        The goal is to turn the TimeSeriesDataFrame into a
        regular TimeSeriesDataFrame.
        Refer to TimeSeriesDataFrame.check_regularity_by_grain
        for definition of regular TimeSeriesDataFrame.

        .. _offset-alias: https://pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases

        :param freq:
            If the frequency string is provided, the function will fill
            the datetime gaps according to the provided string.
            Otherwise, it will infer the frequency string and
            fill the time index accordingly.
            See offset-alias.
        :type freq: str or pandas.DateOffset object

        :param origin:
            If provided, the datetime will be filled back to origin for
            all grains.
        :type origin: str or datetime-like
        :param end:
            If provided, the datetime will be filled up to end for all grains.
        :type end: string or datetime-like

        :return:
            A TimeSeriesDataFrame with the datetime properly filled.
        :rtype: TimeSeriesDataFrame

        :example:
        >>> data1 = pd.DataFrame(
        ...   {'store': ['a', 'a', 'a', 'b', 'b'],
        ...    'brand': ['a', 'a', 'a', 'b', 'b'],
        ...    'date': pd.to_datetime(
        ...      ['2017-01-01', '2017-01-03', '2017-01-04',
        ...       '2017-01-01', '2017-01-02']),
        ...    'sales': [1, np.nan, 5, 2, np.nan],
        ...    'price': [np.nan, 2, 3, np.nan, 4]})
        >>> df1 = TimeSeriesDataFrame(data1, grain_colnames=['store', 'brand'],
        ...                           time_colname='date',
        ...                           ts_value_colname='sales')
        >>> df1
                                price  sales
        date       store brand
        2017-01-01 a     a        nan   1.00
        2017-01-03 a     a       2.00    nan
        2017-01-04 a     a       3.00   5.00
        2017-01-01 b     b        nan   2.00
        2017-01-02 b     b       4.00    nan
        >>> df1.fill_datetime_gap(freq='D')
          brand       date  price  sales store
        0     a 2017-01-01    NaN    1.0     a
        1     a 2017-01-02    NaN    NaN     a
        2     a 2017-01-03    2.0    NaN     a
        3     a 2017-01-04    3.0    5.0     a
        4     b 2017-01-01    NaN    2.0     b
        5     b 2017-01-02    4.0    NaN     b
        """
        if freq is None:
            freq = self.infer_freq()

        # Weird bug here -
        # See comment at _from_axes classmethod
        # For now, the cases must be treated separately
        if self.grain_colnames is None:
            tsdf_filled = _fill_datetime_gap_single_slice_key(
                self, '__identity_grain', freq=freq, origin=origin, end=end)
        else:
            tsdf_bygrain = self.groupby_slice_key()
            tsdf_filled = tsdf_bygrain.apply(
                lambda x: _fill_datetime_gap_single_slice_key(
                    x, x.name, freq=freq, origin=origin, end=end))

        return tsdf_filled

    # pylint: disable=no-self-argument
    def merge(left, right, how='inner', on=None, left_on=None, right_on=None,
              left_index=False, right_index=False, sort=True,
              suffixes=('_x', '_y'), copy=True, indicator=False):
        """
        Overwrite the pandas merge function.

        1. Have better defaults when using on two TimeSeriesDataFrames.
        2. Transfer the meta-data sensibly to the new object.
           For list-like meta-data present in both left and right frames,
           the ordering of the list items in the merged frame will be
           that of the left object.

        :param right: Left DataFrame object
        :type right: pandas.DataFrame

        :param right: Right DataFrame object
        :type right: pandas.DataFrame

        :param how:
            One of {'left', 'right', 'outer', 'inner'}. Defaults to 'inner'.
            * left: use only keys from left frame, similar to a SQL left outer join;
              preserve key order
            * right: use only keys from right frame, similar to a SQL right outer join;
              preserve key order
            * outer: use union of keys from both frames, similar to a SQL full outer
              join; sort keys lexicographically
            * inner: use intersection of keys from both frames, similar to a SQL inner
              join; preserve the order of the left keys
        :type how: str

        :param on:
            Field names to join on. Must be found in both DataFrames. If on is
            None and not merging on indexes, then it merges on the intersection of
            the columns by default.
        :type on: str or list of str

        :param left_on:
            Field names to join on in left DataFrame. Can be a vector or list of
            vectors of the length of the DataFrame to use a particular vector as
            the join key instead of columns
        :type left_on: label, list, or array-like

        :param right_on:
            Field names to join on in right DataFrame or vector/list of vectors per
            left_on parameter.
        :type right_on: label, list, or array-like

        :param left_index:
            Use the index from the left DataFrame as the join key(s). If it is a
            MultiIndex, the number of keys in the other DataFrame (either the index
            or a number of columns) must match the number of levels
        :type left_index: boolean, default False

        :param right_index:
            Use the index from the right DataFrame as the join key. Same caveats as
            left_index
        :type right_index: boolean, default False

        :param sort:
            Sort the join keys lexicographically in the result DataFrame. If False,
            the order of the join keys depends on the join type
            (see the 'how' parameter)
        :type sort: boolean, default True

        :param suffixes:
            Suffix to apply to overlapping column names in the left and right
            side, respectively
        :type suffixes: list-like of length 2

        :param copy:
            If False, do not copy data unnecessarily
        :type copy: boolean, default True

        :param indicator:
            If True, adds a column to output DataFrame called "_merge" with
            information on the source of each row.
            If string, column with information on source of each row will be added to
            output DataFrame, and column will be named value of string.
            Information column is Categorical-type and takes on a value of "left_only"
            for observations whose merge key only appears in 'left' DataFrame,
            "right_only" for observations whose merge key only appears in 'right'
            DataFrame, and "both" if the observation's merge key is found in both.
        :type indicator:  boolean or str, default False

        :return: Merged data frame
        :rtype: TimeSeriesDataFrame
        """
        # First check if user has supplied information on how to merge the
        # two objects
        left_is_set = False
        right_is_set = False
        left_on_temp = left_on
        right_on_temp = right_on
        if on is not None:
            left_is_set = True
            right_is_set = True
            left_on_temp = on
            right_on_temp = on
        else:
            if left_on is not None or left_index is True:
                left_is_set = True
                if left_index is True:
                    left_on_temp = left.index.names
            if right_on is not None or right_index is True:
                right_is_set = True
                if right_index is True:
                    right_on_temp = right.index.names

        # Next check if left and right are time series data frames.
        left_is_ts = False
        right_is_ts = False
        if isinstance(left, TimeSeriesDataFrame):
            left_is_ts = True
        if isinstance(right, TimeSeriesDataFrame):
            right_is_ts = True

        # If both left_index and right_index are true, and the two DataFrames have multiple overlap indices,
        # drop all indices, set left_on and right_on to the overlapping keys. This avoids running into a
        # pandas NotImplementedError about multiple overlapping indices.
        if left_index and right_index:
            if isinstance(left.index, MultiIndex) and isinstance(right.index, MultiIndex):
                left_index_names = [
                    n for n in left.index.names if n is not None]
                right_index_names = [
                    n for n in right.index.names if n is not None]
                overlap = list(set(left_index_names) & set(right_index_names))

                if len(overlap) > 1:
                    left_is_set = True
                    right_is_set = True

                    left_on = right_on = overlap

                    left_index = False
                    right_index = False
                    if isinstance(left, TimeSeriesDataFrame):
                        left = super(TimeSeriesDataFrame, left).reset_index()
                    else:
                        left = left.reset_index()
                    if isinstance(right, TimeSeriesDataFrame):
                        right = super(TimeSeriesDataFrame, right).reset_index()
                    else:
                        right = right.reset_index()
        else:
            # If the merge is not based on the index values, reset the index
            # because pandas gets rid of the index in a merge call.
            if isinstance(left, TimeSeriesDataFrame):
                if not left_index and (not isinstance(left.index, pd.Int64Index) or
                                       left._verify_datetime_like(left.index)):
                    left = super(TimeSeriesDataFrame, left).reset_index()
            if isinstance(right, TimeSeriesDataFrame):
                if not right_index and (not isinstance(right.index, pd.Int64Index) or
                                        right._verify_datetime_like(right.index)):
                    right = super(TimeSeriesDataFrame, right).reset_index()

        def get_post_merge_names(names_left, names_right, merge_index_left,
                                 merge_index_right, suffixes):
            if names_left is None and names_right is None:
                return(None)
            if names_left is None:
                names_left = []
            elif isinstance(names_left, str):
                names_left = [names_left]
            if names_right is None:
                names_right = []
            elif isinstance(names_right, str):
                names_right = [names_right]
            if merge_index_left is None:
                merge_index_left = []
            elif isinstance(merge_index_left, str):
                merge_index_left = [merge_index_left]
            if merge_index_right is None:
                merge_index_right = []
            elif isinstance(merge_index_right, str):
                merge_index_right = [merge_index_right]

            # Let m be an item of metadata.
            # Need to add a suffix to m in the following conditions:
            # 1) m is in intersection(names_left, names_right)
            # AND
            # 2) m is NOT in intersection(merge_index_left, merge_index_right)
            #
            # The next code section finds disjoint sets
            #  `will_change` and `wont_change`.
            # The metadata in `will_change` require a suffix.
            # Together, these two sets form a partition of
            #  union(names_left, names_right).
            names_left_set = set(names_left)
            names_right_set = set(names_right)
            wont_change = names_left_set.symmetric_difference(names_right_set)
            might_change = names_left_set.intersection(names_right_set)
            merge_index_left = set(merge_index_left)
            merge_index_right = set(merge_index_right)
            wont_change_index = merge_index_left.intersection(
                merge_index_right)
            wont_change = wont_change.union(
                might_change.intersection(wont_change_index))
            will_change = might_change.difference(wont_change_index)

            # Add suffixes to the "will_change" metadata
            # These loops cover all metadata cases since
            #  will_change and wont_change form a partition
            new_names_left = [nm + suffixes[0] if nm in will_change else nm
                              for nm in names_left]
            new_names_right = [nm + suffixes[1] if nm in will_change else nm
                               for nm in names_right]

            # Get a list of right frame metadata that isn't already
            #  in the left frame metadata
            right_minus_left_ordered = [nm for nm in new_names_right
                                        if nm not in new_names_left]

            # Return the ordered union of new_names_left and new_names_right
            return (new_names_left + right_minus_left_ordered)

        # If both series are time series and no merge indexes are set, create
        # time series appropiate defaults.
        if left_is_ts and right_is_ts:
            new_time_colname = left.time_colname
            if not left_is_set and not right_is_set and left_is_ts and right_is_ts:
                left_on = [left.time_colname]
                right_on = [right.time_colname]

                if left.grain_colnames is not None and right.grain_colnames is not None:
                    common_grain_colnames = list(
                        set(left.grain_colnames).intersection(set(right.grain_colnames)))
                    if len(common_grain_colnames) >= 1:
                        left_on.extend(common_grain_colnames)
                        right_on.extend(common_grain_colnames)

                if left.origin_time_colname is not None and right.origin_time_colname is not None:
                    left_on.append(left.origin_time_colname)
                    right_on.append(right.origin_time_colname)
                left_on_temp = left_on
                right_on_temp = right_on
            new_grain_colnames = get_post_merge_names(
                left.grain_colnames, right.grain_colnames,
                left_on_temp, right_on_temp, suffixes)
            left_ts_value = left.actual if hasattr(
                left, 'actual') else left.ts_value_colname
            right_ts_value = right.actual if hasattr(
                right, 'actual') else right.ts_value_colname
            new_ts_value_colname = get_post_merge_names(
                left_ts_value, right_ts_value, left_on_temp, right_on_temp, suffixes)
            if isinstance(new_ts_value_colname, list):
                if len(new_ts_value_colname) == 1:
                    new_ts_value_colname = new_ts_value_colname[0]
                else:
                    new_ts_value_colname = \
                        [n for n in new_ts_value_colname if
                            n.startswith(left_ts_value)][0]
            new_group_colnames = get_post_merge_names(
                left.group_colnames, right.group_colnames, left_on_temp, right_on_temp, suffixes)
            new_origin_time_colname = get_post_merge_names(
                left.origin_time_colname, right.origin_time_colname,
                left_on_temp, right_on_temp, suffixes)
            if isinstance(new_origin_time_colname, list):
                if len(new_origin_time_colname) == 1:
                    new_origin_time_colname = new_origin_time_colname[0]
                else:
                    new_origin_time_colname = \
                        [n for n in new_origin_time_colname if
                            n.startswith(left.origin_time_colname)][0]
        elif left_is_ts:
            new_time_colname = left.time_colname
            new_grain_colnames = left.grain_colnames
            new_ts_value_colname = left.ts_value_colname
            new_group_colnames = left.group_colnames
            new_origin_time_colname = left.origin_time_colname
        else:
            new_time_colname = right.time_colname
            new_grain_colnames = right.grain_colnames
            new_ts_value_colname = right.ts_value_colname
            new_group_colnames = right.group_colnames
            new_origin_time_colname = right.origin_time_colname

        # Do the merge
        if left_is_ts:
            merged = super(TimeSeriesDataFrame, left).merge(right=right, how=how, on=on,
                                                            left_on=left_on,
                                                            right_on=right_on, left_index=left_index,
                                                            right_index=right_index, sort=sort, suffixes=suffixes,
                                                            copy=copy, indicator=indicator)
        elif right_is_ts:
            merged = super(TimeSeriesDataFrame, right).merge(left=left, how=how, on=on,
                                                             left_on=left_on,
                                                             right_on=right_on, left_index=left_index,
                                                             right_index=right_index, sort=sort, suffixes=suffixes,
                                                             copy=copy, indicator=indicator)

        # Set time series parameters
        merged.time_colname = new_time_colname
        merged.grain_colnames = new_grain_colnames
        if hasattr(merged, 'ts_value_colname'):
            merged.ts_value_colname = new_ts_value_colname
        else:
            merged.actual = new_ts_value_colname
        merged.group_colnames = new_group_colnames
        merged.origin_time_colname = new_origin_time_colname
        merged._reset_tsindex()
        return(merged)

    # Check this method in pandas 0.22.
    # It seems to be related to an error in groupby/apply
    # for tsdf.groupby(by=lambda label: '__identity_group').apply(...),
    # as is done when the grain isn't set.
    # This function gets called in 'apply' and the result
    # is a dataframe filled with NAs/zeros.
    # Not sure why it gets called at all in that case.
    @classmethod
    def _from_axes(cls, data, axes, **kwargs):
        new_data = pd.DataFrame._from_axes(data, axes, **kwargs)
        final = cls._internal_ctor(new_data)
        return final

    def __finalize__(self, other, method=None, **kwargs):
        """Propagate metadata from other to self."""
        # merge operation: using metadata of the left object
        if method == 'merge':
            if isinstance(other.left, TimeSeriesDataFrame) and isinstance(other.right, TimeSeriesDataFrame):
                metadata_to_reset = list(set(self._metadata).difference(
                    set(["time_colname", "grain_colnames", "ts_value_colname", "group_colnames", "origin_time"])))
                for name in metadata_to_reset:
                    if hasattr(other.right, name) and getattr(other.left, name) != getattr(other.right, name):
                        warn('The left and right objects may have different {0} values, result using the {0} of the'
                             ' left object'.format(name))

                    attr_val = getattr(other.left, name, None)
                    attr_val_final = self._finalize_attr_val(name, attr_val)
                    object.__setattr__(self, name, attr_val_final)
            else:
                for name in self._metadata:
                    attr_val = getattr(other.left, name, None)
                    attr_val_final = self._finalize_attr_val(name, attr_val)
                    object.__setattr__(self, name, attr_val_final)

        # concat operation: using metadata of the first object
        elif method == 'concat':
            if all(isinstance(x, TimeSeriesDataFrame) for x in other.objs):
                indexes = {tuple(o.grain_colnames)
                           if o.grain_colnames is not None else tuple([])
                           for o in other.objs}
                if len(indexes) > 1:
                    raise DataFrameIncorrectFormatException(
                        "index values for data_frames do not match.")
                for name in self._metadata:
                    name_values_all = []
                    for o in other.objs:
                        if hasattr(o, name):
                            name_value = getattr(o, name)
                            if isinstance(name_value, list):
                                name_value = tuple(name_value)
                            elif isinstance(name_value, dict):
                                name_value = frozenset(name_value.items())
                            else:
                                name_value = (name_value,)
                            name_values_all.append(name_value)
                    name_values_unique = set(name_values_all)
                    if len(name_values_unique) > 1:
                        warn(('The concatenated objects may have different {0} ' +
                              'values, result using the {0} of the'
                              ' first object').format(name))
                    if len(name_values_unique) > 0:
                        attr_val = getattr(other.objs[0], name, None)
                        attr_val_final = self._finalize_attr_val(name, attr_val)
                        object.__setattr__(self, name, attr_val_final)

            else:
                indexes = {tuple(o.index.names) for o in other.objs}
                if len(indexes) > 1:
                    raise DataFrameIncorrectFormatException(
                        "index values for data_frames do not match.")
                warn('Not all concatenated objects are TimeSeriesDataFrame, ' +
                     'result using the meta data of the first object')
                for name in self._metadata:
                    attr_val = getattr(other.objs[0], name, None)
                    attr_val_final = self._finalize_attr_val(name, attr_val)
                    object.__setattr__(self, name, attr_val_final)

        else:
            for name in self._metadata:
                attr_val = getattr(other, name, None)
                attr_val_final = self._finalize_attr_val(name, attr_val)
                object.__setattr__(self, name, attr_val_final)

        if any(self.index.duplicated()):
            raise DataFrameIncorrectFormatException(
                "There is more than one value for a `time_colname` and " +
                "'`grain_colnames` combination.",
                error_detail="Repeated labels are: " +
                str(self.index[self.index.duplicated()].unique()))

        return self

    def _finalize_attr_val(self, name, attr_val):
        # This function prevents the column not found exception when some
        # original _metadata columns are not selected to produce the
        # new TimeSeriesDataFrame.
        # No warning message is printed, because the warning messages
        # are meaningless and confusing when the
        # __finalize__ function is called in some intermediate steps.
        attr_val_final = None   # type: Optional[Union[List[str], Dict[str, str], str]]
        if isinstance(attr_val, list):
            attr_val_final = []
            for col in attr_val:
                if col in self.columns or col in self.index.names:
                    attr_val_final.append(col)
            if len(attr_val_final) == 0:
                attr_val_final = None
        elif isinstance(attr_val, dict):
            attr_val_final = {}
            for key, col in attr_val.items():
                if col in self.columns or col in self.index.names:
                    attr_val_final[key] = col
            if len(attr_val_final) == 0:
                attr_val_final = None
        else:
            if attr_val in self.columns or attr_val in self.index.names or attr_val is None:
                attr_val_final = attr_val
            else:
                attr_val_final = None
        return attr_val_final

    def count_ts(self):
        """
        Count the number of unique time series in the data.

        :return: Number of unique time series in the data.
        :rtype: int
        """
        if self.grain_colnames:
            ts_count = len(self.grain_index.unique())
        else:
            ts_count = 1
            warn('The grain_colnames property of the TimeSeriesDataFrame ' +
                 'is not set. Assuming a single time series.')
        return ts_count

    def compute_ts_value_summary(self):
        """
        Compute summary statistics of the target column.

        i.e. column specified by ts_value_colname. Statistics computed include
        percentage of missing values, percentage of zero values,
        coefficients of variation of time series.

        :return: A summary of target column statistics.
        :rtype: dict
        """
        ts_value_summary_dict = {}
        ts_count = self.count_ts()
        print(
            '-----------------------------  Value Column Summary  '
            '-----------------------------')
        # Percentage of missing/zero values in the target column
        if self.ts_value_colname:
            value_missing_percent = self[self.ts_value_colname].isnull(
            ).sum() / len(self)
            value_zero_percent = len(
                self[self[self.ts_value_colname] == 0]) / len(self)
            print('Value column                        {0}'.format(
                self.ts_value_colname))
            print('Percentage of missing values        {0:.2f}'.format(
                value_missing_percent))
            print('Percentage of zero values           {0:.2f}'.format(
                value_zero_percent))
            ts_value_summary_dict['value_missing_percent'] = \
                value_missing_percent
            ts_value_summary_dict['value_zero_percent'] = value_zero_percent

            # Coefficient of variation of the target column
            def cv(x):
                return np.var(x) / np.mean(x)

            if ts_count > 1:
                # Distribution of coefficient of variation
                cv_by_grain = self[[self.ts_value_colname]].groupby(
                    level=self.grain_colnames).apply(lambda g: cv(g.ts_value))
                cv_min = cv_by_grain.min()
                cv_min_idx = cv_by_grain.idxmin()
                cv_max = cv_by_grain.max()
                cv_max_idx = cv_by_grain.idxmax()
                cv_mean = cv_by_grain.mean()
                cv_median = cv_by_grain.median()
                print(
                    'Mean coefficient of variation       {0:.2f}'.format(
                        cv_mean))
                print(
                    'Median coefficient of variation     {0:.2f}'.format(
                        cv_median))
                print(
                    'Minimum coefficient of variation    {0} {1}: {2:.2f}'
                    .format(self.grain_colnames, cv_min_idx, cv_min))
                print(
                    'Maximum coefficient of variation    {0} {1}: {2:.2f}'
                    .format(self.grain_colnames, cv_max_idx, cv_max))
                ts_value_summary_dict['cv_min'] = cv_min
                ts_value_summary_dict['cv_min_idx'] = cv_min_idx
                ts_value_summary_dict['cv_max'] = cv_max
                ts_value_summary_dict['cv_max_idx'] = cv_max_idx
                ts_value_summary_dict['cv_mean'] = cv_mean
                ts_value_summary_dict['cv_median'] = cv_median
            else:
                cv_ts = cv(self[self.ts_value_colname])
                print(
                    'Coefficient of variation            {0:.2f}'
                    .format(cv_ts))
                ts_value_summary_dict['cv_ts'] = cv_ts
        else:
            warn(
                'The ts_value_colname property of the TimeSeriesDataFrame is '
                'not set.')
        return ts_value_summary_dict

    def _label_bar_percentage(self, ax, total):
        for p in ax.patches:
            height = p.get_height()
            if height / total < 0.005:
                percentage = round(height / total * 100, 2)
            else:
                percentage = int(round(height / total * 100))
            ax.text(p.get_x() + p.get_width() / 2,
                    height * 1.005,
                    '{0}%'.format(percentage),
                    ha="center")

    def to_json(self):
        """
        Serialize the TimeSeriesDataFrame as a JSON string.

        :return: JSON representation of the TimeSeriesDataFrame
        :rtype: str
        """
        json_dict = {}

        # add metadata attributes to json_dict
        for attribute in TimeSeriesDataFrame._metadata:
            json_dict[attribute] = getattr(self, attribute)

        # get the names of columns that contains datetime type data
        datetime_colnames_all = list(super(TimeSeriesDataFrame, self).reset_index(
        ).select_dtypes(include=[np.datetime64]).columns.values)
        json_dict['datetime_colnames_all'] = datetime_colnames_all

        # add the serialized data
        json_dict['data'] = super(TimeSeriesDataFrame, super(
            TimeSeriesDataFrame, self).reset_index()).to_json(orient='split')

        json_str = json.dumps(json_dict)
        return json_str

    @classmethod
    def construct_from_json(cls, json_str):
        """
        Construct TimeSeriesDataFrame from a JSON string.

        The input string should conform with the serialization format
        used in TimeSeriesDataFrame.to_json().

        :param json_str: Input json string.
        :type json_str: str

        :return: Constructed data frame
        :rtype: TimeSeriesDataFrame
        """
        json_dict = json.loads(json_str)

        if isinstance(json_dict, str):
            # this is to handle the result string coming from
            # operationalization web service call, which needs two json.loads
            json_dict = json.loads(json_dict)
            if not isinstance(json_dict, dict):
                raise Exception('Input of type {} can not be converted from json dictionary'.format(type(json_str)))
        json_dict['data'] = pd.read_json(
            json_dict['data'], orient='split', convert_dates=json_dict['datetime_colnames_all'])

        # delete the datetime_colnames_all attribute, which is not needed for the constructor
        json_dict.pop('datetime_colnames_all')

        tsdf = cls(**json_dict)
        return tsdf

    def _get_numeric_columns(self):
        """Get the list of columns contains numeric values."""
        dtype_series = self.dtypes
        numeric_columns = dtype_series.loc[dtype_series.apply(
            lambda x: np.issubdtype(x, np.number))].index.tolist()
        return numeric_columns

    def equals(self, other):
        """
        Check whether two TimeSeriesDataFrame are equal.

        This is designed to be used in unit tests.

        :param other: The TimeSeriesDataFrame to compare against.
        :type other: TimeSeriesDataFrame

        :return: True if the frame is equal to 'other'
        :rtype: bool
        """
        # unit tests to be added.
        # This could be far from perfect.
        # The behavior of pd.to_json() and pd.read_json()
        #   need more investigation.
        # check whether column are equal
        self_copy = self.copy()
        other_copy = other.copy()

        if not sorted(self.columns.tolist()) == sorted(other.columns.tolist()):
            return False

        # try to convert all column that could possibly be turned into numeric to numeric.
        for column in self_copy.columns:
            try:
                self_copy[column] = self_copy[column].astype('float64')
            except Exception:
                pass

            try:
                other_copy[column] = other_copy[column].astype('float64')
            except Exception:
                pass

        # check using the pd.DataFrame.equals, which check whether the _data
        # is equal.
        # we sort the index before the comparison so that the comparison is
        # proper.
        if not pd.DataFrame(self_copy).sort_index().equals(
                pd.DataFrame(other_copy).sort_index()):
            return False

        # check the equality of metadata
        for attribute_name in TimeSeriesDataFrame._metadata:
            if not getattr(self, attribute_name) == getattr(other, attribute_name):
                return False

        return True

    def _check_freq(self, freq=None):
        if freq is None:
            freq = self.infer_freq()
            if freq is None:
                raise DataFrameValueException(
                    'The frequency of the TimeSeriesDataFrame cannot be '
                    'inferred. Please provide it in the freq argument.')

        return to_offset(freq)

    def _get_floor_freq(self):
        """Get first non-all-zero time part will be inferred as the floor frequency."""
        if not all(self.time_index.microsecond == 0):
            floor_freq = offsets.Micro()
        else:
            if not all(self.time_index.second == 0):
                floor_freq = offsets.Second()
            else:
                if not all(self.time_index.minute == 0):
                    floor_freq = offsets.Minute()
                else:
                    if not all(self.time_index.hour == 0):
                        floor_freq = offsets.Hour()
                    else:
                        # with all time unit with granularity of larger
                        # than Day, using Day()
                        floor_freq = offsets.Day()
        return floor_freq

    def get_period_start_time_index(self, is_start_of_period=True, freq=None,
                                    floor_freq=None):
        """
        Get period start time.

        A time stamp in a time series often actually represents a period of time.
        For example, '2017-01-01' can
        represent a period from '2017-01-01' to '2017-01-31' when
        the frequency is monthly, or '2017-01-01' to '2017-12-31' with
        a yearly frequency.

        This method infers the period start time implied by
        data frame timestamps given information about the time series frequency.

        :param is_start_of_period:
            Whether the time index in the column 'time_colname' of the
            TimeSeriesDataFrame represents the start or the end of the period.
        :type is_start_of_period: boolean

        :param freq:
            The frequency of the time series in the data frame
            If freq=None, the frequency will be inferred.
        :type freq: str or pandas.DateOffset object

        :param floor_freq:
            The calculated time index in precision of micro seconds will be
            floored according to the specified frequency here.
            The default is None, when the used floor freq will be obtained
            based on time index of the input data.
        :type floor_freq: str or pandas.DateOffset object

        :return: Period start times for each data frame row
        :rtype: pandas.DatetimeIndex
        """
        # Extra comments that are a bit out-of-scope for a
        # a method docstring.
        # This method
        # is useful when you want to get full information about the period
        # represented behind the time index value in the time_colname in the
        # TimeSeriesDataFrame.

        # One related scenario could be that you want to join two data sets,
        # however one is using the last day of the year in the time index to
        # represents a year, and another is using the first day of the year.
        # Here you can use either get_period_start_time_index or
        # get_period_end_time_index to both data sets, so the meaning of the
        # time stamp in the two data sets are uniformed (both start of the
        # year, or both end of the year), and you can now more easily join the
        # two data sets based on the uniformed time stamp.

        # In both get_period_start_time_index or get_period_end_time_index,
        # The start time index is firstly calculated at precision of
        # microseconds, and then the results are ceiled accordingly.
        freq = self._check_freq(freq=freq)

        if floor_freq is None:
            floor_freq = self._get_floor_freq()
        else:
            floor_freq = to_offset(floor_freq)

        if is_start_of_period:
            period_start_time_index = self.time_index
        else:
            period_start_time_index = self.time_index - freq + floor_freq

        return period_start_time_index.floor(freq=floor_freq)

    def get_period_end_time_index(self, is_start_of_period=True, freq=None,
                                  floor_freq=None):
        """
        Infer the period end time implied by timestamps given information about the time series frequency.

        See get_period_start_time_index for more information.

        :param is_start_of_period:
            Whether the time index in the column 'time_colname' of the
            TimeSeriesDataFrame represents the start or the end of the period.
        :type is_start_of_period: boolean

        :param freq:
            The frequency of the time series in the data frame
            If freq=None, the frequency will be inferred.
        :type freq: str or pandas.DateOffset object


        :param floor_freq:
            The calculated time index in precision of micro seconds will be
            floored according to the specified frequency here.
            The default is None, when the used floor freq will be obtained
            based on time index of the input data.
        :type floor_freq: str or pandas.DateOffset object

        :return: Period end times for each data frame row
        :rtype: pandas.DatetimeIndex
        """
        freq = self._check_freq(freq=freq)

        if floor_freq is None:
            floor_freq = self._get_floor_freq()
        else:
            floor_freq = to_offset(floor_freq)

        if not is_start_of_period:
            period_end_time_index = self.time_index
        else:
            period_end_time_index = self.time_index + freq - floor_freq

        return period_end_time_index.floor(freq=floor_freq)

    def _get_metadata_dict(self):
        """
        Get the dictionary of {metadata: value of metadata}.

        :return: The dictionary that contains metadata information
        :rtype: dict
        """
        return {metadata_name: getattr(self, metadata_name) for
                metadata_name in self._metadata}

    def subset_by_grains(self, grains):
        """
        Get a subset of data specified by "grains".

        This function is useful when you need to select one or a list of
        arbitrary grains. If you need data from a range of grain indices,
        pandas.IndexSlice is recommended.

        :param grains:
            Data for which grains to return. If the grain_colnnames only contains
            one column name, this can be string or an iterable of strings. If
            the grain_colnames contains multiple column names, this can be an
            iterable of tuples/lists, where each tuple/list specifies one grain.
            The elements in each tuple/list must follow the same order as the
            grain_colnames.
        :type grains: str, iterable

        :return: A subset of data specified by grains.
        :rtype: TimeSeriesDataFrame
        """
        # When user provides a single grain with multiple grain_colnames,
        # e.g. (2, 'dominicks'), [2, 'dominicks']
        if (verify.is_iterable_but_not_string(grains) and
                len(self.grain_colnames) > 1 and
                not isinstance(grains[0], Iterable))\
                or isinstance(grains, str):
            grains = [grains]

        self_subset = self.loc[self.grain_index.isin(grains)]

        return self_subset

    def _get_metadata(self):
        """Private method to retrieve all metadata as a dict."""
        return {k: getattr(self, k) for k in self._metadata}

    def subset_by_origin_time(self, origin_time=None):
        """
        Get a subset that corresponds to a certain value of `origin_time` or a range of origin times.

        Primary use case is to get the "latest" slice of the predicted data in a
        multi-step forecasting environment.

        :param origin_time:
            Date or subset of dates to which the values of `origin_time_index`
            should be limited in the output. Defaults to the earliest origin
            date for the latest value of time index. E.g. in a
            three-steps-ahead forecasting scenario, calling
            `subset_by_origin_time()` will return:
                * one-step-ahead prediction at horizon 1
                * two-steps-ahead prediction at horizon 2, and
                * three-steps-ahead prediction at horizon 3.
            If `origin_time_colname` is not set, this method returns back
            the entire TimeSeriesDataFrame and prints a warning.
        :type grains: datetime-like or an iterable thereof

        :return: A subset of data specified by `origin_time`.
        :rtype: TimeSeriesDataFrame
        """
        if self.origin_time_colname is None:
            origin_not_set_msg = ("`origin_time_colname` is not set in this " +
                                  "data frame, returning itself.")
            warn(origin_not_set_msg, UserWarning)
            return self
        if origin_time is None:
            last_index = self.loc[self.time_index == max(self.time_index)]
            origin_time = min(last_index.origin_time_index)
        is_datetime_like(origin_time)
        if not is_collection(origin_time):
            origin_time = [origin_time]
        self_subset = self.loc[self.origin_time_index.isin(origin_time)]

        return self_subset
