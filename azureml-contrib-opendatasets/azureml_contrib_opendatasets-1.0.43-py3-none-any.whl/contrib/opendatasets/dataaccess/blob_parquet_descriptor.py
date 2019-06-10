# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Define a descriptor of blob parquet."""

from .base_blob_info import BaseBlobInfo
from .._utils.blob_pandas_helper import read_parquet_files
from ..environ import SparkEnv, PandasEnv
from azure.storage.blob import BlockBlobService
from multimethods import multimethod
from pyspark.sql import SparkSession
from pyspark.sql.functions import col


class BlobParquetDescriptor:
    """Public data accessor."""

    __data_name = '__data'
    __env_name = 'env'

    def __init__(self, blobInfo: BaseBlobInfo):
        """Initialize blob parquet descriptor."""
        self.__blobInfo = blobInfo

    def __get__(self, inst, cls):
        """Get inst.__data."""
        if (getattr(inst, self.__env_name, None) is None):
            print("There is no data loaded until %s.env is set as SparkEnv() or PandasEnv()." % inst.__class__)
            return None

        if (getattr(inst, self.__data_name, None) is None):
            setattr(inst, self.__data_name, self._load_data(inst, inst.env))

        return getattr(inst, self.__data_name)

    def __set__(self, inst, value):
        """Set inst.__data."""
        setattr(inst, self.__data_name, value)

    @multimethod(object, SparkEnv)
    def _load_data(self, inst, env):
        return self.get_spark_dataframe(inst)

    @multimethod(object, PandasEnv)
    def _load_data(self, inst, env):
        return self.get_pandas_dataframe(inst)

    def get_spark_dataframe(self, inst):
        """
        Get spark dataframe.

        :return: Spark dataframe based on its own filters.
        :rtype: .SparkDataFrame
        """
        path = self.__blobInfo.get_data_wasbs_path()
        spark = SparkSession.builder.getOrCreate()

        spark.conf.set(
            'fs.azure.sas.%s.%s.blob.core.windows.net' %
            (self.__blobInfo.blob_container_name, self.__blobInfo.blob_account_name), self.__blobInfo.blob_sas_token)

        df = spark.read.parquet(path).select(inst.selected_columns)
        # in case of inst.selected_columns == ['*']
        inst.selected_columns = df.columns
        return df.where((col(inst.time_column_name) >= inst.start_date) & (
            col(inst.time_column_name) <= inst.end_date))

    def get_pandas_dataframe(self, inst):
        """
        Get pandas dataframe.

        :return: Pandas dataframe based on its own filters.
        :rtype: pandas.DataFrame
        """
        success, blob_account_name, blob_container_name, blob_relative_path, blob_sas_token = \
            self.__blobInfo.get_blob_metadata()
        if success:
            self.__blobInfo.blob_account_name = blob_account_name
            self.__blobInfo.blob_container_name = blob_container_name
            self.__blobInfo.blob_relative_path = blob_relative_path
            self.__blobInfo.blob_sas_token = blob_sas_token

        blob_service = BlockBlobService(
            account_name=self.__blobInfo.blob_account_name,
            sas_token=self.__blobInfo.blob_sas_token.lstrip('?'))
        target_paths = inst.get_pandas_limit().get_target_blob_paths(
            blob_service=blob_service,
            blob_container_name=self.__blobInfo.blob_container_name,
            blob_relative_path=self.__blobInfo.blob_relative_path)

        if not target_paths:
            raise ValueError(
                'Cannot find target blob paths for given input datetime range:\n\tstart date: %s\n\tend date: %s' % (
                    inst.start_date, inst.end_date))

        if inst.cols is not None:
            all_columns = inst.selected_columns
            all_df = read_parquet_files(
                target_paths=target_paths,
                blob_container_name=self.__blobInfo.blob_container_name,
                blob_service=blob_service,
                cols=all_columns)
            filter_mask = (all_df[inst.time_column_name] >= inst.start_date) & (
                all_df[inst.time_column_name] <= inst.end_date)
            filtered_df = all_df.loc[filter_mask]
            filtered_df = filtered_df[all_columns]
        else:
            all_df = read_parquet_files(
                target_paths=target_paths,
                blob_container_name=self.__blobInfo.blob_container_name,
                blob_service=blob_service,
                cols=None)
            filter_mask = (all_df[inst.time_column_name] >= inst.start_date) & (
                all_df[inst.time_column_name] <= inst.end_date)
            filtered_df = all_df.loc[filter_mask]
            # in case of inst.selected_columns == ['*']
            inst.selected_columns = list(filtered_df.columns)

        print('Done.')
        return filtered_df
