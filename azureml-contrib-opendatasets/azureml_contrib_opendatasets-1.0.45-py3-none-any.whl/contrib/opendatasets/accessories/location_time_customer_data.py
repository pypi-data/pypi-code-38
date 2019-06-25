# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Customer data with location and time columns should be wrapped using this class."""

from .customer_data import CustomerData
from .location_data import LatLongColumn, ZipCodeColumn, LocationCustomerData
from .time_data import TimeCustomerData

from multimethods import multimethod


class LocationTimeCustomerData (LocationCustomerData, TimeCustomerData):
    """A customer_data class which contains location column and time column."""

    @multimethod(object, LatLongColumn, str)
    def __init__(self, data, _latlong_column, _time_column_name):
        """
        Initialize the class using latlong_column class instance.

        :param data: object of customer data
        :param _latlong_column: an isinstance of latlong_column
        :param _time_column_name: datetime column name
        """
        self.time_column_name = _time_column_name
        (self.latitude_column_name, self.longitude_column_name) = [_latlong_column.lat_name, _latlong_column.long_name]
        CustomerData.__init__(self, data)
        self.extend_time_column(self.env)

    @multimethod(object, ZipCodeColumn, str)
    def __init__(self, data, _zipcode_column, _time_column_name):
        """
        Initialize the class using zipcode_column class instance.

        :param data: object of customer data
        :param _latlong_column: an isinstance of zipcode_column
        :param _time_column_name: datetime column name
        """
        self.time_column_name = _time_column_name
        CustomerData.__init__(self, data)
        self.extend_zip_column(self.env, _zipcode_column.name)
        self.extend_time_column(self.env)
