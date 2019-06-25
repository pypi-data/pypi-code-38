# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Location data, with supported column classes."""

from .._utils.random_utils import random_tag
from .._utils.zipcode_mapping import load_zipcode_mapping
from .customer_data import CustomerData
from ..environ import SparkEnv, PandasEnv
from multimethods import multimethod
from pandas import DataFrame as PdDataFrame
from pyspark.sql.dataframe import DataFrame as SparkDataFrame
from pyspark.sql.functions import col, min, max
import pandas as pd


@multimethod(SparkDataFrame, str)
def _find_min_max_zipcode(dataset, zipcode_column_name):
    """
    Find the min/max zipcode in dataset.

    :param dataset: input (customer) dataset
    :param zipcode_column_name: zipcode column name in dataset
    :return: a tuple of minimnum and maximum zipcode
    """
    min_zipcode = dataset.select(min(zipcode_column_name)).collect()[0][0]
    max_zipcode = dataset.select(max(zipcode_column_name)).collect()[0][0]
    return (min_zipcode, max_zipcode)


@multimethod(PdDataFrame, str)
def _find_min_max_zipcode(dataset, zipcode_column_name):
    """
    Find the min/max zipcode in dataset.

    :param dataset: input (customer) dataset
    :param zipcode_column_name: zipcode column name in dataset
    :return: a tuple of minimnum and maximum zipcode
    """
    min_zipcode = dataset[zipcode_column_name].min()
    max_zipcode = dataset[zipcode_column_name].max()
    return (min_zipcode, max_zipcode)


class LatLongColumn:
    """A wrapper class of latitude and longitude."""

    def __init__(self, lat_name: str, long_name: str):
        """Initialize latitude and longitude column names."""
        self.__lat_name = lat_name
        self.__long_name = long_name

    @property
    def lat_name(self) -> str:
        """Get latitude column name."""
        return self.__lat_name

    @property
    def long_name(self) -> str:
        """Get longitude column name."""
        return self.__long_name


class ZipCodeColumn:
    """A wrapper class of zipcode."""

    def __init__(self, column_name: str):
        """Initialize with a zip code column name."""
        self.__name = column_name

    @property
    def name(self) -> str:
        """Get zip code column name."""
        return self.__name


class LocationData:
    """
    A class defines location two related properties below.

    latitude_column_name
    longitude_column_name
    """

    @property
    def latitude_column_name(self):
        """Get latitude column name."""
        return self.__latitude_column_name

    @latitude_column_name.setter
    def latitude_column_name(self, value: str):
        """Set latitude column name."""
        self.__latitude_column_name = value

    @property
    def longitude_column_name(self) -> str:
        """Get longitude column name."""
        return self.__longitude_column_name

    @longitude_column_name.setter
    def longitude_column_name(self, value: str):
        """Set longitude column name."""
        self.__longitude_column_name = value


class LocationCustomerData(CustomerData, LocationData):
    """
    A class inheriting from customer_data + location_data.

    It extends zip column in customer_data to latitude and longitude.
    """

    @multimethod(SparkEnv, str)
    def extend_zip_column(self, env, zipcode_column_name):
        """
        Extend the given zipcode column to latitude and longitude columns.

        :param _zipcode_column_name: zipcode column name in the customer_data
        """
        zipcode_mapping_ds = load_zipcode_mapping(env)
        customer_ds = self.data

        (min_zipcode, max_zipcode) = _find_min_max_zipcode(customer_ds, zipcode_column_name)

        self.latitude_column_name = 'lat_' + random_tag()
        self.longitude_column_name = 'lng_' + random_tag()
        self.to_be_cleaned_up_column_names = [self.latitude_column_name, self.longitude_column_name]
        zipcode_mapping_ren = zipcode_mapping_ds.withColumnRenamed(
            "LAT", self.latitude_column_name).withColumnRenamed(
                "LNG", self.longitude_column_name).filter(
                    (zipcode_mapping_ds.ZIP >= min_zipcode) & (zipcode_mapping_ds.ZIP <= max_zipcode))

        self.data = customer_ds.alias('a').join(
            zipcode_mapping_ren.alias('b'),
            customer_ds[zipcode_column_name] == zipcode_mapping_ren.ZIP, "left_outer").select(
                [col("a.*")] + [
                    col("b." + self.latitude_column_name),
                    col("b." + self.longitude_column_name)])

        self.data.cache()

    @multimethod(PandasEnv, str)
    def extend_zip_column(self, env, zipcode_column_name):
        """
        Extend the given zipcode column to latitude column and longitude column.

        :param zipcode_column_name: zipcode column name in the customer_data
        """
        zipcode_mapping_ds = load_zipcode_mapping(env)
        customer_ds = self.data

        (min_zipcode, max_zipcode) = _find_min_max_zipcode(customer_ds, zipcode_column_name)

        self.latitude_column_name = 'lat_' + random_tag()
        self.longitude_column_name = 'lng_' + random_tag()
        self.to_be_cleaned_up_column_names = [self.latitude_column_name, self.longitude_column_name]
        zipcode_mapping_ren = zipcode_mapping_ds[
            (zipcode_mapping_ds.ZIP >= min_zipcode) & (zipcode_mapping_ds.ZIP <= max_zipcode)].rename(
                index=str,
                columns={
                    "LAT": self.latitude_column_name,
                    "LNG": self.longitude_column_name})

        extended_dataset = pd.merge(
            customer_ds,
            zipcode_mapping_ren,
            left_on=[zipcode_column_name],
            right_on=['ZIP'],
            how='left').loc[
                :,
                list(customer_ds.columns) + [
                    self.latitude_column_name,
                    self.longitude_column_name]]

        self.data = extended_dataset
