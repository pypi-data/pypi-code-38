# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Time data and its related operations."""

from ..environ import SparkEnv, PandasEnv
from .customer_data import CustomerData
from .public_data import PublicData

from .._utils.random_utils import random_tag
from datetime import datetime
from time import mktime, struct_time

import numpy as np
from dateutil import parser
from multimethods import multimethod
from pandas import DataFrame as PdDataFrame
from pyspark.sql.dataframe import DataFrame as SparkDataFrame
from pyspark.sql.functions import col, max, min, udf
from pyspark.sql.types import TimestampType


@multimethod(SparkDataFrame, str)
def find_min_max_date(dataset, time_col_name):
    """Find min and max date from a SPARK dataframe."""
    min_date = dataset.select(min(time_col_name)).collect()[0][0]
    max_date = dataset.select(max(time_col_name)).collect()[0][0]
    return (min_date, max_date)


@multimethod(PdDataFrame, str)
def find_min_max_date(dataset, time_col_name):
    """Find min and max date from a SPARK dataframe."""
    return dataset[time_col_name].min().tz_localize(None).to_pydatetime(),\
        dataset[time_col_name].max().tz_localize(None).to_pydatetime()


@multimethod(SparkDataFrame, str, object)
def add_datetime_col(dataset, time_col_name, time_udf):
    """Add rounded datetime column."""
    datetime_col = 'datetime' + random_tag()
    dataset = dataset.withColumn(datetime_col, time_udf(time_col_name))
    return (datetime_col, dataset, [datetime_col])


@multimethod(PdDataFrame, str, object)
def add_datetime_col(dataset, time_col_name, time_func):
    """Add a datetime column."""
    datetime_col = 'datetime' + random_tag()
    dataset[datetime_col] = dataset[time_col_name].apply(time_func)
    return (datetime_col, dataset, [datetime_col])


def spark_parse_time(time_string):
    """Parse time string and catch exception."""
    try:
        time = parser.parse(time_string)
    except ValueError:
        time = None
    return time


def pd_parse_time(time_string):
    """Parse time string and catch exception."""
    try:
        time = parser.parse(time_string)
        time = time.replace(tzinfo=None)
    except (TypeError, ValueError):
        time = np.nan
    return time


@multimethod(SparkDataFrame, str, str)
def extend_time_column(dataset, time_col_name, timeVal):
    """Extend time column for string type."""
    time_udf = udf(lambda x: spark_parse_time(x), TimestampType())
    return add_datetime_col(dataset, time_col_name, time_udf)


@multimethod(SparkDataFrame, str, float)
def extend_time_column(dataset, time_col_name, timeVal):
    """Extend time column for float type."""
    time_udf = udf(lambda x: datetime.fromtimestamp(float(x)), TimestampType())
    return add_datetime_col(dataset, time_col_name, time_udf)


@multimethod(SparkDataFrame, str, struct_time)
def extend_time_column(dataset, time_col_name, timeVal):
    """Extend time column for struct_time type."""
    time_udf = udf(lambda x: datetime.fromtimestamp(mktime(x)), TimestampType())
    return add_datetime_col(dataset, time_col_name, time_udf)


@multimethod(PdDataFrame, str, str)
def extend_time_column(dataset, time_col_name, timeVal):
    """Extend time column for string type."""
    return add_datetime_col(dataset, time_col_name, pd_parse_time)


@multimethod(PdDataFrame, str, float)
def extend_time_column(dataset, time_col_name, timeVal):
    """Extend time column for float type."""
    return add_datetime_col(dataset, time_col_name, datetime.fromtimestamp)


@multimethod(PdDataFrame, str, struct_time)
def extend_time_column(dataset, time_col_name, timeVal):
    """Extend time column for struct_time type."""
    (new_time_col_name, dataset, to_be_cleaned_up_columns) = add_datetime_col(dataset, time_col_name, mktime)
    return new_time_col_name, dataset[new_time_col_name].apply(datetime.fromtimestamp), to_be_cleaned_up_columns


@multimethod(object, str, datetime)
def extend_time_column(dataset, time_col_name, timeVal):
    """Do nothing for datetime type."""
    return (time_col_name, dataset, [])


class TimeData:
    """Time data class."""

    @property
    def time_column_name(self):
        """Get time column name."""
        return self.__time_column_name

    @time_column_name.setter
    def time_column_name(self, value):
        """Set time column name."""
        self.__time_column_name = value

    @property
    def min_date(self):
        """Get min date."""
        return self.__min_date

    @min_date.setter
    def min_date(self, value):
        """Set min date."""
        self.__min_date = value

    @property
    def max_date(self):
        """Get max date."""
        return self.__max_date

    @max_date.setter
    def max_date(self, value):
        """Set max date."""
        self.__max_date = value


class TimePublicData(PublicData, TimeData):
    """Public data with time."""

    @multimethod(SparkDataFrame)
    def _get_time_val(self, dataset):
        return dataset.select(col(self.time_column_name))\
            .where(col(self.time_column_name).isNotNull()).limit(1)\
            .collect()[0][0]

    @multimethod(PdDataFrame)
    def _get_time_val(self, dataset):
        return dataset[self.time_column_name][dataset[self.time_column_name] != np.nan].head(1)

    def extend_time_column(self):
        """Extend time column into datetime format if necessary."""
        dataset = self.data
        timeVal = self._get_time_val(dataset)
        (self.time_column_name, self.data, _) = extend_time_column(dataset, self.time_column_name, timeVal)

    @multimethod(SparkEnv, datetime, datetime)
    def filter(self, env, min_date, max_date):
        """Filter datetime."""
        (self.min_date, self.max_date) = (min_date, max_date)
        return self.data.filter(self.data[self.time_column_name] >= self.min_date)\
            .filter(self.data[self.time_column_name] <= self.max_date)

    @multimethod(PandasEnv, datetime, datetime)
    def filter(self, env, min_date, max_date):
        """Filter datetime."""
        (self.min_date, self.max_date) = (min_date, max_date)
        return self.data[(self.data[self.time_column_name] >= self.min_date) & (
            self.data[self.time_column_name] <= self.max_date)]


class TimeCustomerData(CustomerData, TimeData):
    """Customer data with time."""

    @multimethod(SparkEnv)
    def extend_time_column(self, env):
        """Extend time column into datetime format if necessary."""
        dataset = self.data
        timeVal = dataset.select(col(self.time_column_name))\
            .where(col(self.time_column_name).isNotNull()).limit(1).collect()[0][0]
        (self.time_column_name, self.data, to_be_cleaned_up_columns) = extend_time_column(
            dataset, self.time_column_name, timeVal)
        self.to_be_cleaned_up_column_names += to_be_cleaned_up_columns
        (self.min_date, self.max_date) = find_min_max_date(dataset, self.time_column_name)
        self.data = dataset

    @multimethod(PandasEnv)
    def extend_time_column(self, env):
        """Extend time column into datetime format if necessary."""
        dataset = self.data
        timeVal = dataset[dataset[self.time_column_name].notnull()].loc[0, self.time_column_name]
        (self.time_column_name, self.data, to_be_cleaned_up_columns) = extend_time_column(
            dataset, self.time_column_name, timeVal)
        self.to_be_cleaned_up_column_names += to_be_cleaned_up_columns
        (self.min_date, self.max_date) = find_min_max_date(dataset, self.time_column_name)
        self.data = dataset

    @multimethod(SparkEnv, datetime, datetime)
    def filter(self, env, min_date, max_date):
        """Filter datetime."""
        (self.min_date, self.max_date) = (min_date, max_date)
        return self.data.filter(self.data[self.time_column_name] >= self.min_date)\
            .filter(self.data[self.time_column_name] <= self.max_date)

    @multimethod(PandasEnv, datetime, datetime)
    def filter(self, env, min_date, max_date):
        """Filter datetime."""
        (self.min_date, self.max_date) = (min_date, max_date)
        return self.data[(self.data[self.time_column_name] >= self.min_date) & (
            self.data[self.time_column_name] <= self.max_date)]
