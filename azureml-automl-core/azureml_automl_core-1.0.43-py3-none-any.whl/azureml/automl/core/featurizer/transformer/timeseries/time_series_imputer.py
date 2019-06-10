# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Impute missing data in time-series specific ways, such as interpolation."""
from typing import cast, List
from warnings import warn

import pandas as pd
import numpy as np

from automl.client.core.common.forecasting_exception import (NotTimeSeriesDataFrameException,
                                                             TransformValueException)
from automl.client.core.common.forecasting_utils import get_period_offsets_from_dates
from automl.client.core.common.forecasting_verify import Messages
from automl.client.core.common.logging_utilities import function_debug_log_wrapped
from automl.client.core.common.time_series_data_frame import TimeSeriesDataFrame
from .forecasting_base_estimator import AzureMLForecastTransformerBase
from .forecasting_constants import HORIZON_COLNAME


class TimeSeriesImputer(AzureMLForecastTransformerBase):
    """
    Imputation transformer for imputing the missing values of data frame columns.

    .. py:class:: TimeSeriesImputer

    .. _pandas.Series.interpolate: https://pandas.pydata.org/pandas-docs/
                                stable/generated/pandas.Series.interpolate.html
    .. _pandas.Series.fillna: https://pandas.pydata.org/pandas-docs/stable/
                                generated/pandas.Series.fillna.html
    .. _pandas.DateOffset: https://pandas.pydata.org/pandas-docs/stable/timeseries.html#dateoffset-objects

    :param input_column:
        The name(s) of the column(s) need(s) to be imputed.
    :type input_column: str, list of str.

    :param option:
        One of {'interpolate', 'fillna'}.
        The 'interpolate' and 'fillna' options have additional
        parameters that specify their operation.
    :type option: str

    :param method:
        Can be used for option 'interpolate' or 'fillna', see
        pandas.Series.interpolate or pandas.Series.fillna respectively
        for more information.
    :type method: str

    :param limit:
        Can be used for option 'interpolate' or 'fillna', see
        pandas.Series.interpolate or pandas.Series.fillna respectively
        for more information.
    :type limit: str

    :param value:
        Can be used for option 'fillna', see pandas.Series.fillna
        for more information.

    :param limit_direction:
        can be used for option 'interpolate', see pandas.Series.interpolate
        for more information.
    :type limit_direction: str

    :param order:
        can be used for option 'interpolate', see pandas.Series.interpolate
        for more information.
    :type order: str

    :param freq:
        Time series frequency.
        If the freq is string, this string needs to be a pandas Offset Alias.
        See pandas.DateOffset for more information.
    :type freq: str or pandas.DateOffset object

    :param origin:
        If provided, the datetime will be filled back to origin for
        all grains.
    :type origin: str or datetime-like
    :param end:
        If provided, the datetime will be filled up to end for all grains.
    :type end: string or datetime-like

    :param impute_by_horizon:
        See documentation for TimeSeriesImputer.transform() for more
        information.
    :type impute_by_horizon: bool

    Examples:
    Construct a sample dataframe: df1
    Notice that df1 is not a regular time series, because for store 'a',
    the row for date '2017-01-03' is missing.

    >>> data1 = pd.DataFrame(
    ...  {'store': ['a', 'a', 'b', 'b', 'c', 'c', 'c', 'd',
    ...            'd', 'd', 'd', 'd', 'd', 'd', 'd'],
    ...   'date': pd.to_datetime(
    ...      ['2017-01-02', '2017-01-04', '2017-01-01', '2017-01-02',
    ...       '2017-01-01', '2017-01-02', '2017-01-03', '2017-01-01',
    ...       '2017-01-02', '2017-01-03', '2017-01-04', '2017-01-05',
    ...       '2017-01-06', '2017-01-07', '2017-01-08']),
    ...   'sales': [1, np.nan, 2, np.nan, 6, 7, np.nan, 10, 11, 15, 13, 14,
    ...             np.nan, np.nan, 15],
    ...   'price': [np.nan, 3, np.nan, 4, 3, 6, np.nan, 2, 6, 3, 5, 5,
    ...             np.nan, np.nan, 6]})
    >>> df1 = TimeSeriesDataFrame(data1, grain_colnames=['store'],
    ...                           time_colname='date', ts_value_colname='sales')
    >>> df1
    >>>                price  sales
    >>> date       store
    2017-01-02 a        nan   1.00
    2017-01-04 a       3.00    nan
    2017-01-01 b        nan   2.00
    2017-01-02 b       4.00    nan
    2017-01-01 c       3.00   6.00
    2017-01-02 c       6.00   7.00
    2017-01-03 c        nan    nan
    2017-01-01 d       2.00  10.00
    2017-01-02 d       6.00  11.00
    2017-01-03 d       3.00  15.00
    2017-01-04 d       5.00  13.00
    2017-01-05 d       5.00  14.00
    2017-01-06 d        nan    nan
    2017-01-07 d        nan    nan
    2017-01-08 d       6.00  15.00

    If you run infer_freq, the 'regular_ts' attribute is False,
    with inferred frequency 'D'.

    >>> df1.infer_freq() # doctest: +SKIP
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
    {'regular_ts': False, 'freq': 'D'}

    >>> sorted(df1.infer_freq().items())
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
    [('freq', 'D'), ('regular_ts', False)]

    Impute df1 for single column 'sales' with option 'default'
    Notice here, for store 'a', the missing row for date '2017-01-03'
    is added and imputed as well.
    Also by default, the freq that is used to fill in the missing date
    is the inferred frequency from df1.infer_freq(), in this case: 'D'

    >>> imputer1 = TimeSeriesImputer(input_column='sales', option='default')
    >>> imputer1.transform(df1)
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.


    >>>      date  price      sales store
    0  2017-01-02    NaN   1.000000     a
    1  2017-01-03    NaN   1.000000     a
    2  2017-01-04    3.0   1.000000     a
    3  2017-01-01    NaN   2.000000     b
    4  2017-01-02    4.0   2.000000     b
    5  2017-01-01    3.0   6.000000     c
    6  2017-01-02    6.0   7.000000     c
    7  2017-01-03    NaN   7.000000     c
    8  2017-01-01    2.0  10.000000     d
    9  2017-01-02    6.0  11.000000     d
    10 2017-01-03    3.0  15.000000     d
    11 2017-01-04    5.0  13.000000     d
    12 2017-01-05    5.0  14.000000     d
    13 2017-01-06    NaN  14.333333     d
    14 2017-01-07    NaN  14.666667     d
    15 2017-01-08    6.0  15.000000     d

    If you want to specify the freq explicitly, you can also use the
    'freq' key argument to pass the freq, since in some cases the inferred
    frequency might not be exact, such as no frequency is inferred from
    any time series, or there are multiple frequencies inferred and the
    one chosen is not the one you want.

    >>> imputer2 = TimeSeriesImputer(input_column='sales', option='default',
    ...                              freq='D')
    >>> imputer2.transform(df1)
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.

    >>>      date  price      sales store
    0  2017-01-02    NaN   1.000000     a
    1  2017-01-03    NaN   1.000000     a
    2  2017-01-04    3.0   1.000000     a
    3  2017-01-01    NaN   2.000000     b
    4  2017-01-02    4.0   2.000000     b
    5  2017-01-01    3.0   6.000000     c
    6  2017-01-02    6.0   7.000000     c
    7  2017-01-03    NaN   7.000000     c
    8  2017-01-01    2.0  10.000000     d
    9  2017-01-02    6.0  11.000000     d
    10 2017-01-03    3.0  15.000000     d
    11 2017-01-04    5.0  13.000000     d
    12 2017-01-05    5.0  14.000000     d
    13 2017-01-06    NaN  14.333333     d
    14 2017-01-07    NaN  14.666667     d
    15 2017-01-08    6.0  15.000000     d

    The default option is just the same as set option='interpolate',
    method='linear' and limit_direction='both'

    >>> imputer3 = TimeSeriesImputer(input_column='sales',
    ...                              option='interpolate', method='linear',
    ...                              limit_direction='both')
    >>> imputer3.transform(df1)
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.

    >>>      date  price  sales store
    0  2017-01-02    NaN   1.000000     a
    1  2017-01-03    NaN   1.000000     a
    2  2017-01-04    3.0   1.000000     a
    3  2017-01-01    NaN   2.000000     b
    4  2017-01-02    4.0   2.000000     b
    5  2017-01-01    3.0   6.000000     c
    6  2017-01-02    6.0   7.000000     c
    7  2017-01-03    NaN   7.000000     c
    8  2017-01-01    2.0  10.000000     d
    9  2017-01-02    6.0  11.000000     d
    10 2017-01-03    3.0  15.000000     d
    11 2017-01-04    5.0  13.000000     d
    12 2017-01-05    5.0  14.000000     d
    13 2017-01-06    NaN  14.333333     d
    14 2017-01-07    NaN  14.666667     d
    15 2017-01-08    6.0  15.000000     d

    You can also impute for list of columns. Here, impute df1 for both
    'sales' and 'price' columns.

    >>> imputer4 = TimeSeriesImputer(input_column=['sales', 'price'],
    ...                              option='default')
    >>> imputer4.transform(df1)
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.

    >>>      date  price  sales store
    0  2017-01-02  3.000000   1.000000     a
    1  2017-01-03  3.000000   1.000000     a
    2  2017-01-04  3.000000   1.000000     a
    3  2017-01-01  4.000000   2.000000     b
    4  2017-01-02  4.000000   2.000000     b
    5  2017-01-01  3.000000   6.000000     c
    6  2017-01-02  6.000000   7.000000     c
    7  2017-01-03  6.000000   7.000000     c
    8  2017-01-01  2.000000  10.000000     d
    9  2017-01-02  6.000000  11.000000     d
    10 2017-01-03  3.000000  15.000000     d
    11 2017-01-04  5.000000  13.000000     d
    12 2017-01-05  5.000000  14.000000     d
    13 2017-01-06  5.333333  14.333333     d
    14 2017-01-07  5.666667  14.666667     d
    15 2017-01-08  6.000000  15.000000     d

    You can also set options to 'interpolate' and use key arguments such as
    'method', 'limit', 'limit_direction' and 'order'
    from pandas.Series.interpolate
    Note if the specific method used does not apply to some of the grains,
    the default linear interpolation is used for those grains.

    >>> imputer5 = TimeSeriesImputer(input_column=['sales'],
    ...                              option='interpolate', method='barycentric')
    >>> imputer5.transform(df1)
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.

    >>>      date  price  sales store
    0  2017-01-02    NaN   1.000000     a
    1  2017-01-03    NaN   1.000000     a
    2  2017-01-04    3.0   1.000000     a
    3  2017-01-01    NaN   2.000000     b
    4  2017-01-02    4.0   2.000000     b
    5  2017-01-01    3.0   6.000000     c
    6  2017-01-02    6.0   7.000000     c
    7  2017-01-03    NaN   8.000000     c
    8  2017-01-01    2.0  10.000000     d
    9  2017-01-02    6.0  11.000000     d
    10 2017-01-03    3.0  15.000000     d
    11 2017-01-04    5.0  13.000000     d
    12 2017-01-05    5.0  14.000000     d
    13 2017-01-06    NaN  26.904762     d
    14 2017-01-07    NaN  42.428571     d
    15 2017-01-08    6.0  15.000000     d

    You can also set options to 'fillna' and use use key arguments such as
    'method', 'value' and 'limit'methods from pandas.Series.fillna

    >>> imputer6 = TimeSeriesImputer(input_column=['sales'], option='fillna', method='ffill')
    >>> imputer6.transform(df1)
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.

    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.

    >>>      date  price  sales store
    0  2017-01-02    NaN    1.0     a
    1  2017-01-03    NaN    1.0     a
    2  2017-01-04    3.0    1.0     a
    3  2017-01-01    NaN    2.0     b
    4  2017-01-02    4.0    2.0     b
    5  2017-01-01    3.0    6.0     c
    6  2017-01-02    6.0    7.0     c
    7  2017-01-03    NaN    7.0     c
    8  2017-01-01    2.0   10.0     d
    9  2017-01-02    6.0   11.0     d
    10 2017-01-03    3.0   15.0     d
    11 2017-01-04    5.0   13.0     d
    12 2017-01-05    5.0   14.0     d
    13 2017-01-06    NaN   14.0     d
    14 2017-01-07    NaN   14.0     d
    15 2017-01-08    6.0   15.0     d

    >>> imputer7 = TimeSeriesImputer(input_column=['sales'], option='fillna',
    ...                              value=0)
    >>> imputer7.transform(df1)
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.

    >>>      date  price  sales store
    0  2017-01-02    NaN    1.0     a
    1  2017-01-03    NaN    0.0     a
    2  2017-01-04    3.0    0.0     a
    3  2017-01-01    NaN    2.0     b
    4  2017-01-02    4.0    0.0     b
    5  2017-01-01    3.0    6.0     c
    6  2017-01-02    6.0    7.0     c
    7  2017-01-03    NaN    0.0     c
    8  2017-01-01    2.0   10.0     d
    9  2017-01-02    6.0   11.0     d
    10 2017-01-03    3.0   15.0     d
    11 2017-01-04    5.0   13.0     d
    12 2017-01-05    5.0   14.0     d
    13 2017-01-06    NaN    0.0     d
    14 2017-01-07    NaN    0.0     d
    15 2017-01-08    6.0   15.0     d

    Sometime, you might want to fill values up to some eariler date or down
    to some later date, you can use the origin and end property
    for the purpose.

    >>> imputer8 = TimeSeriesImputer(input_column=['sales'], option='fillna',
    ...                              value=0, origin='2016-12-28')
    >>> imputer8.transform(df1)
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.

    >>>      date  price  sales store
    0  2016-12-28    NaN    0.0     a
    1  2016-12-29    NaN    0.0     a
    2  2016-12-30    NaN    0.0     a
    3  2016-12-31    NaN    0.0     a
    4  2017-01-01    NaN    0.0     a
    5  2017-01-02    NaN    1.0     a
    6  2017-01-03    NaN    0.0     a
    7  2017-01-04    3.0    0.0     a
    8  2016-12-28    NaN    0.0     b
    9  2016-12-29    NaN    0.0     b
    10 2016-12-30    NaN    0.0     b
    11 2016-12-31    NaN    0.0     b
    12 2017-01-01    NaN    2.0     b
    13 2017-01-02    4.0    0.0     b
    14 2016-12-28    NaN    0.0     c
    15 2016-12-29    NaN    0.0     c
    16 2016-12-30    NaN    0.0     c
    17 2016-12-31    NaN    0.0     c
    18 2017-01-01    3.0    6.0     c
    19 2017-01-02    6.0    7.0     c
    20 2017-01-03    NaN    0.0     c
    21 2016-12-28    NaN    0.0     d
    22 2016-12-29    NaN    0.0     d
    23 2016-12-30    NaN    0.0     d
    24 2016-12-31    NaN    0.0     d
    25 2017-01-01    2.0   10.0     d
    26 2017-01-02    6.0   11.0     d
    27 2017-01-03    3.0   15.0     d
    28 2017-01-04    5.0   13.0     d
    29 2017-01-05    5.0   14.0     d
    30 2017-01-06    NaN    0.0     d
    31 2017-01-07    NaN    0.0     d
    32 2017-01-08    6.0   15.0     d

    >>> imputer9 = TimeSeriesImputer(input_column=['sales'], option='fillna',
    ...                              value=0, end='2017-01-10')
    >>> imputer9.transform(df1)
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
    expect 1 distinct datetime frequency from all ['store'](s) in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.

    >>>      date  price  sales store
    0  2017-01-02    NaN    1.0     a
    1  2017-01-03    NaN    0.0     a
    2  2017-01-04    3.0    0.0     a
    3  2017-01-05    NaN    0.0     a
    4  2017-01-06    NaN    0.0     a
    5  2017-01-07    NaN    0.0     a
    6  2017-01-08    NaN    0.0     a
    7  2017-01-09    NaN    0.0     a
    8  2017-01-10    NaN    0.0     a
    9  2017-01-01    NaN    2.0     b
    10 2017-01-02    4.0    0.0     b
    11 2017-01-03    NaN    0.0     b
    12 2017-01-04    NaN    0.0     b
    13 2017-01-05    NaN    0.0     b
    14 2017-01-06    NaN    0.0     b
    15 2017-01-07    NaN    0.0     b
    16 2017-01-08    NaN    0.0     b
    17 2017-01-09    NaN    0.0     b
    18 2017-01-10    NaN    0.0     b
    19 2017-01-01    3.0    6.0     c
    20 2017-01-02    6.0    7.0     c
    21 2017-01-03    NaN    0.0     c
    22 2017-01-04    NaN    0.0     c
    23 2017-01-05    NaN    0.0     c
    24 2017-01-06    NaN    0.0     c
    25 2017-01-07    NaN    0.0     c
    26 2017-01-08    NaN    0.0     c
    27 2017-01-09    NaN    0.0     c
    28 2017-01-10    NaN    0.0     c
    29 2017-01-01    2.0   10.0     d
    30 2017-01-02    6.0   11.0     d
    31 2017-01-03    3.0   15.0     d
    32 2017-01-04    5.0   13.0     d
    33 2017-01-05    5.0   14.0     d
    34 2017-01-06    NaN    0.0     d
    35 2017-01-07    NaN    0.0     d
    36 2017-01-08    6.0   15.0     d
    37 2017-01-09    NaN    0.0     d
    38 2017-01-10    NaN    0.0     d

    The imputer works not only for TimeSeriesDataFrame with time_index
    column of type DatetimeIndex, but also TimeSeriesDataFrame with
    time_index column of PeriodIndex as well.

    >>> data2 = pd.DataFrame(
    ...   {'store': ['a', 'a', 'a', 'b', 'b'],
    ...    'brand': ['a', 'a', 'a', 'b', 'b'],
    ...    'date': pd.PeriodIndex(
    ...      ['2011-12', '2012-02', '2012-03', '2012-02', '2012-03'],
    ...      dtype = 'period[M]', freq = 'M'),
    ...    'sales': [1, np.nan, 5, 2, np.nan],
    ...    'price': [np.nan, 2, 3, np.nan, 4]})
    >>> df2 = TimeSeriesDataFrame(data2, grain_colnames=['store', 'brand'],
    ...                          time_colname='date', ts_value_colname='sales')
    >>> df2
      brand    date  price  sales store
    0     a 2011-12    NaN    1.0     a
    1     a 2012-02    2.0    NaN     a
    2     a 2012-03    3.0    5.0     a
    3     b 2012-02    NaN    2.0     b
    4     b 2012-03    4.0    NaN     b
    >>> imputer10 = TimeSeriesImputer(input_column=['sales'],
    ...                               option='fillna', value=0)
    >>> imputer10.transform(df2)
      brand    date  price  sales store
    0     a 2011-12    NaN    1.0     a
    1     a 2012-01    NaN    0.0     a
    2     a 2012-02    2.0    0.0     a
    3     a 2012-03    3.0    5.0     a
    4     b 2012-02    NaN    2.0     b
    5     b 2012-03    4.0    0.0     b

    """

    def __init__(self, input_column,
                 option='fillna', method=None, value=None, limit=None,
                 limit_direction='forward', order=None, freq=None,
                 origin=None, end=None, impute_by_horizon=False, logger=None):
        """Create a TimeSeriesImputer."""
        self.input_column = input_column
        self.option = option
        self.method = method
        self.value = value
        self.limit = limit
        self.limit_direction = limit_direction
        self.order = order
        self.freq = freq
        self.origin = origin
        self.end = end
        self.impute_by_horizon = impute_by_horizon

        self._init_logger(logger)

    @classmethod
    def _impute_with_interpolation_single_group(cls, single_group_data,
                                                **kwargs):
        """
        Impute missing values for all columns which contains single group data.

        Uses pandas.DataFrame.interpolate.
        """
        # Need to reset the index for pd.DataFrame.interpolate
        # since only method=linear works when the Series has a multi-index
        interpolation_df = pd.DataFrame(single_group_data).reset_index(
            drop=True)
        interpolation_df = interpolation_df.interpolate(**kwargs)

        # get the index back
        interpolation_df.index = single_group_data.index

        return interpolation_df

    @classmethod
    def _impute_with_fillna_single_group(cls, single_group_data, **kwargs):
        """
        Impute missing values for all columns which contains single group data.

        Uses pandas.DataFrame.fillna.
        """
        return single_group_data.fillna(**kwargs)

    @classmethod
    def _impute_missing_value_by_cols(
            cls, input_df, input_column, sort_index_by_col, by_cols=None,
            option='interpolate', freq=None, origin=None, end=None, **kwargs):
        """Impute missing value within each group, where groups are defined by by_cols."""
        if not input_df.check_regularity(freq=freq):
            input_df_filled = input_df.fill_datetime_gap(
                freq=freq, origin=origin, end=end)
            if not input_df_filled.check_regularity(freq=freq):
                raise TransformValueException('The TimeSeriesDataFrame does '
                                              'not have time index with '
                                              'regular datetime gaps even '
                                              'after fill_datetime_gaps.')
            # sort by time
            input_df_filled = input_df_filled.sort_index(
                level=sort_index_by_col)
        else:
            # sort by time
            input_df_filled = input_df.sort_index(
                level=sort_index_by_col)

        if option == 'interpolate':
            if by_cols is None:
                input_df_filled[input_column] = \
                    cls._impute_with_interpolation_single_group(
                        input_df_filled[input_column], **kwargs)
            else:
                input_df_filled[input_column] = input_df_filled.groupby(
                    by=by_cols, group_keys=False)[input_column].apply(
                    lambda x: cls._impute_with_interpolation_single_group(
                        x, **kwargs))
        elif option == 'fillna':
            if by_cols is None:
                input_df_filled[input_column] = \
                    cls._impute_with_fillna_single_group(
                        input_df_filled[input_column], **kwargs)
            else:
                input_df_filled[input_column] = input_df_filled.groupby(
                    by=by_cols, group_keys=False)[input_column].apply(
                    lambda x: cls._impute_with_fillna_single_group(x, **kwargs))
        else:
            raise TransformValueException(
                'please provide the supported option arguments.')
        return input_df_filled

    @classmethod
    def _check_value_same_by_column(cls, input_df, value_col, by_cols):
        """Check whether the value_col have same value given by_cols."""
        whether_unique = input_df.groupby(by=by_cols).apply(
            lambda x: (len(np.unique(x[value_col].values)) == 1) or np.isnan(
                x[value_col].values).all())
        return whether_unique.values.all()

    @classmethod
    def _condense_values_by_column(cls, input_df, value_cols, by_cols):
        """Condense the value_cols by by_cols."""
        return input_df.groupby(by=by_cols)[value_cols].first()

    @classmethod
    def _join_df_with_multiindex(cls, df, multi_index):
        """
        Get an output data frame with index equal to multi_index and values joined from the df.

        This helper function is created for scenario when you have a df with
        pandas.MultiIndex which are a subset of indexes in multi_index,
        you want to get a output data frame with index equal to multi_index
        and values joined from the df.
        """
        output_df = pd.DataFrame(df)
        on_cols = df.index.names
        output_df = output_df.reset_index()
        index_df = multi_index.to_frame(index=False)
        output_df = index_df.merge(output_df, on=on_cols, how='left')
        output_df = output_df.set_index(multi_index.names)
        return output_df

    @function_debug_log_wrapped
    def fit(self, X, y=None):
        """
        Fit is empty for this transform.

        This method is just a pass-through.

        :param X: Ignored.

        :param y: Ignored.

        :return: self
        :rtype: TimeSeriesImputer
        """
        return self

    @function_debug_log_wrapped
    def transform(self, X: TimeSeriesDataFrame) -> TimeSeriesDataFrame:
        """
        Perform imputation on requested data frame columns.

        Here is a brief summary how the TimeSeriesImputer works:
            1. When the input TimeSeriesDataFrame has no property `origin_time`:
                The time series values will be imputed within each time series
                from single `grain_colnames`.
            2. When the input TimeSeriesDataFrame has property `origin_time`:
                a) If time series from the same `grain_colnames have the same value
                as long as the values of `time_colname` are the same, the time
                series will be condensed to have no `origin_time_colname`,
                and get imputed in the condensed data frame. And the imputed
                values will be joined back to the original data by
                `grain_colnames` and `time_colname`.
                b) If time series from the same `grain_colnames` have the same
                value as long as the values of `origin_time_colname` are the
                same, the time series will be condensed to have no
                `time_colname`, and get imputed in the condensed data frame. And
                the imputed values will be joined back to the original data by
                `grain_colnames` and `origin_time_colname`.
                c) For time series not falling into either a) or b), they will be
                imputed within sub-time-series from single combination of
                `grain_colnames` and `origin_time_colname` if impute_by_horizon
                is True. Otherwise, it will be imputed within sub-time-series from
                single combination of `grain_colnames` and `horizon`.

        :param X: Data frame to transform
        :type X: :class:`ftk.dateframets.TimeSeriesDataFrame`

        :return: A data frame with imputed column(s)
        :rtype: :class:`ftk.dateframets.TimeSeriesDataFrame`
        """
        if not isinstance(X, TimeSeriesDataFrame):
            raise NotTimeSeriesDataFrameException(
                Messages.INVALID_TIMESERIESDATAFRAME,
                "Type of the input data frame is {0}".format(type(X)))

        if self.option == 'interpolate':
            kwargs = {'method': self.method, 'limit': self.limit,
                      'limit_direction': self.limit_direction,
                      'order': self.order}
        elif self.option == 'fillna':
            kwargs = {'method': self.method, 'value': self.value,
                      'limit': self.limit}
        else:
            raise TransformValueException(('The option {} is not '
                                           'supported.').format(self.option))

        if self.freq is None:
            freq = X.infer_freq()
            if freq is None:
                raise TransformValueException('The freq cannot be inferred. '
                                              'Please provide freq argument.')
        else:
            freq = self.freq

        if isinstance(self.input_column, str):
            self.input_column = [self.input_column]

        for col in self.input_column:
            if col not in X.columns:
                raise TransformValueException(
                    ('Column {} does not exist in the '
                     'input data.').format(col))

        if X.origin_time_colname is None:
            # TODO: Fill in the type annotations for this function and remove the cast
            return cast(TimeSeriesDataFrame, self._impute_missing_value_by_cols(
                input_df=X, input_column=self.input_column,
                sort_index_by_col=X.time_colname,
                by_cols=X.grain_colnames, option=self.option, freq=freq,
                origin=self.origin, end=self.end, **kwargs))
        else:
            X_copy = cast(TimeSeriesDataFrame, X.copy())
            # To shorten the variable name, in the following code:
            # `got` means grain_and_origin_time
            # `gt` means grain_and_time
            # `ot` means origin_time
            # `t` means time
            cols_same_given_got = []    # type: List[str]
            cols_same_given_gt = []     # type: List[str]
            other_cols = []             # type: List[str]
            for col in self.input_column:
                # check if the column have same value given grain + time
                if self._check_value_same_by_column(
                        input_df=X, value_col=col,
                        by_cols=X.time_and_grain_colnames):
                    cols_same_given_gt += [col]
                # check if the column have same value given grain + origin_time
                elif self._check_value_same_by_column(
                        input_df=X, value_col=col,
                        by_cols=X.slice_key_colnames):
                    cols_same_given_got += [col]
                else:
                    other_cols += [col]

            if len(cols_same_given_gt) > 0:
                # get the condensed data frame which only have grain + time
                gt_condensed_df = self._condense_values_by_column(
                    input_df=X[cols_same_given_gt],
                    value_cols=cols_same_given_gt,
                    by_cols=X.time_and_grain_colnames)
                gt_condensed_df = TimeSeriesDataFrame(
                    gt_condensed_df, time_colname=X.time_colname,
                    grain_colnames=X.grain_colnames)
                # impute missing value
                gt_condensed_df = self._impute_missing_value_by_cols(
                    input_df=gt_condensed_df,
                    input_column=cols_same_given_gt,
                    sort_index_by_col=X.time_colname,
                    by_cols=X.grain_colnames, option=self.option,
                    freq=freq, origin=self.origin, end=self.end, **kwargs)
                # join the condensed data frame back
                X_copy[cols_same_given_gt] = self._join_df_with_multiindex(
                    gt_condensed_df, X.index)

            if len(cols_same_given_got) > 0:
                # get the condensed data frame which only have grain +
                # origin_time
                got_condensed_df = self._condense_values_by_column(
                    input_df=X[cols_same_given_got],
                    value_cols=cols_same_given_got,
                    by_cols=X.slice_key_colnames)
                got_condensed_df = TimeSeriesDataFrame(
                    got_condensed_df, time_colname=X.origin_time_colname,
                    grain_colnames=X.grain_colnames)
                # impute missing value
                got_condensed_df = self._impute_missing_value_by_cols(
                    input_df=got_condensed_df,
                    input_column=cols_same_given_got,
                    sort_index_by_col=X.origin_time_colname,
                    by_cols=X.grain_colnames, option=self.option,
                    freq=freq, origin=self.origin, end=self.end, **kwargs)
                # join the condensed data frame back
                X_copy[cols_same_given_got] = self._join_df_with_multiindex(
                    got_condensed_df, X.index)

            if len(other_cols) > 0:
                if not self.impute_by_horizon:
                    # impute by slice_key_colnames
                    X_copy[other_cols] = self._impute_missing_value_by_cols(
                        input_df=X_copy[other_cols], input_column=other_cols,
                        sort_index_by_col=X.time_colname,
                        by_cols=X.slice_key_colnames, option=self.option,
                        freq=freq, origin=self.origin, end=self.end,
                        **kwargs)
                else:
                    if HORIZON_COLNAME in X_copy.columns:
                        warn(('The column {} will be overwritted to store the '
                              'integer forecasting horizon.').format(
                            HORIZON_COLNAME))
                    X_copy[HORIZON_COLNAME] = get_period_offsets_from_dates(
                        X_copy.index.get_level_values(X_copy.origin_time_colname),
                        X_copy.index.get_level_values(X_copy.time_colname),
                        freq=freq)
                    # impute by grain + horizon
                    if X_copy.grain_colnames is None:
                        grain_and_horizon_colnames = [HORIZON_COLNAME]
                    else:
                        grain_and_horizon_colnames = X_copy.grain_colnames + [
                            HORIZON_COLNAME]

                    X_copy[other_cols] = self._impute_missing_value_by_cols(
                        input_df=X_copy, input_column=other_cols,
                        sort_index_by_col=X.time_colname,
                        by_cols=grain_and_horizon_colnames, option=self.option,
                        freq=freq, origin=self.origin, end=self.end,
                        **kwargs)[other_cols]

            return X_copy
