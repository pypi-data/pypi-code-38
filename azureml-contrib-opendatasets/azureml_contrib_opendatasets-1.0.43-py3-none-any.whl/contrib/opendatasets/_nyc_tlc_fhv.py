# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""NYC Taxi FHV trip data."""

from datetime import datetime
from dateutil import parser
from typing import Optional, List

from ._nyc_tlc_fhv_blob_info import NycTlcFhvBlobInfo
from .accessories.time_data import TimePublicData
from .dataaccess.blob_parquet_descriptor import BlobParquetDescriptor
from .environ import SparkEnv, PandasEnv
from .dataaccess.pandas_data_load_limit import PandasDataLoadLimitToMonth
from multimethods import multimethod


class NycTlcFhv(TimePublicData):
    """NYC TLC FHV data class."""

    _default_start_date = parser.parse('2015-01-01')
    _default_end_date = datetime.today()

    __blobInfo = NycTlcFhvBlobInfo()

    data = BlobParquetDescriptor(__blobInfo)

    def _prepare_cols(self):
        """Prepare columns that can be used to join with other data."""
        self.time_column_name = 'pickupDateTime'

    def __init__(
            self,
            start_date: datetime = _default_start_date,
            end_date: datetime = _default_end_date,
            cols: Optional[List[str]] = None,
            enable_telemetry: bool = True):
        """
        Initialize filtering fields.

        :param start_date: start date you'd like to query inclusively.
        :type start_date: datetime
        :param end_date: end date you'd like to query inclusively.
        :type end_date: datetime
        :param cols: a list of column names you'd like to retrieve. None will get all columns.
        :type cols: Optional[List[str]]
        :param enable_telemetry: whether to send telemetry
        :type enable_telemetry: bool
        """
        self._registry_id = self.__blobInfo.registry_id
        self.path = self.__blobInfo.get_data_wasbs_path()
        self._prepare_cols()
        self.start_date = start_date\
            if (self._default_start_date < start_date)\
            else self._default_start_date
        self.end_date = end_date\
            if (self._default_end_date > end_date)\
            else self._default_end_date
        super(NycTlcFhv, self).__init__(cols=cols, enable_telemetry=enable_telemetry)
        if enable_telemetry:
            self.log_properties['StartDate'] = self.start_date
            self.log_properties['EndDate'] = self.end_date
            self.log_properties['Path'] = self.path

    @multimethod(SparkEnv, datetime, datetime)
    def filter(self, env, min_date, max_date):
        """Filter time.

        :param min_date: min date
        :param max_date: max date

        :return: filtered data frame.
        """
        self.data = self.data.na.drop(how='all', subset=self.cols).na.drop(how='any', subset=[self.time_column_name])

        ds = super(NycTlcFhv, self).filter(env, min_date, max_date)
        return ds.select(*self.selected_columns)

    @multimethod(PandasEnv, datetime, datetime)
    def filter(self, env, min_date, max_date):
        """Filter time.

        :param min_date: min date
        :param max_date: max date

        :return: filtered data frame.
        """
        ds = super(NycTlcFhv, self).filter(env, min_date, max_date)
        ds = ds.dropna(how='all', axis=0, subset=self.cols).dropna(
            how='any', axis=0, subset=[self.time_column_name])

        return ds[self.selected_columns]

    def _get_mandatory_columns(self):
        """
        Get mandatory columns to select.

        :return: a list of column names.
        :rtype: list
        """
        return [self.time_column_name]

    def get_pandas_limit(self):
        """Get instance of pandas data load limit class."""
        return PandasDataLoadLimitToMonth(self.start_date, self.end_date, path_pattern='/puYear=%d/puMonth=%d/')

    def _to_spark_dataframe(self, activity_logger):
        """To spark dataframe.

        :param activity_logger: activity logger

        :return: SPARK dataframe
        """
        descriptor = BlobParquetDescriptor(self.__blobInfo)
        return descriptor.get_spark_dataframe(self)

    def _to_pandas_dataframe(self, activity_logger):
        """
        Get pandas dataframe.

        :param activity_logger: activity logger

        :return: Pandas dataframe based on its own filters.
        :rtype: pandas.DataFrame
        """
        descriptor = BlobParquetDescriptor(self.__blobInfo)
        return descriptor.get_pandas_dataframe(self)
