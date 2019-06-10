# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""base class of all customer data."""

from .._utils.spark_utils import has_column
from ..environ import SparkEnv, PandasEnv, get_environ
from multimethods import multimethod
from pyspark.sql.functions import monotonically_increasing_id
from typing import List, Optional


class CustomerData:
    """Base class of customer data."""

    def __init__(self, _data):
        """Initialize with customer data frame.

        :param _data: data frame
        """
        self.env = get_environ(_data)
        self.__data = _data
        self.__to_be_cleaned_up_column_names = []

    @property
    def to_be_cleaned_up_column_names(self) -> List[str]:
        """Get column names to be cleaned up.

        :return: a list of columns to be cleaned up
        """
        return self.__to_be_cleaned_up_column_names

    @to_be_cleaned_up_column_names.setter
    def to_be_cleaned_up_column_names(self, value: List[str]):
        """Set column names to be cleaned up.

        :param value: a list of column names
        """
        self.__to_be_cleaned_up_column_names = value

    @property
    def data(self) -> Optional[object]:
        """Get dataframe.

        :return: data frame
        """
        return self.__data

    @data.setter
    def data(self, value: object):
        """Set dataframe.

        :param value: a list of column names
        """
        self.__data = value

    @multimethod(SparkEnv)
    def add_row_id(self, env):
        """Add row id to customer data, in order to distinguish after join."""
        if not has_column(self.__data, CustomerData.row_id_col_name()):
            self.__data = self.__data.withColumn(CustomerData.row_id_col_name(), monotonically_increasing_id())

    @multimethod(PandasEnv)
    def add_row_id(self, env):
        """Add row id to customer data, in order to distinguish after join."""
        # pandas has index which is_monotonic_increasing == True
        pass

    @staticmethod
    def row_id_col_name() -> str:
        """Get row id column name.

        :return: row id column name
        """
        return 'row_id'
