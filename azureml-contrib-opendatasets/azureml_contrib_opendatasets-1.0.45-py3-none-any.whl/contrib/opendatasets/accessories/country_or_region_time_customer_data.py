# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Customer data with location and time columns should be wrapped using this class."""

from .customer_data import CustomerData
from .country_region_data import CountryOrRegionColumn, CountryOrRegionData
from .time_data import TimeCustomerData


class CountryOrRegionTimeCustomerData (CountryOrRegionData, TimeCustomerData):
    """A customer_data class which contains location column and time column."""

    def __init__(self, data: object, _countryorregion_column: CountryOrRegionColumn, _time_column_name: str):
        """
        Initialize the class using CountryOrRegionColumn class instance.

        :param data: object of customer data
        :param _countryorregion_column: an isinstance of CountryOrRegionColumn
        :param _time_column_name: datetime column name
        """
        self.time_column_name = _time_column_name
        self.countrycode_column_name = _countryorregion_column.countrycode_column_name
        self.country_or_region_column_name = _countryorregion_column.country_or_region_column_name
        self.available_column_type = _countryorregion_column.available_column_type
        CustomerData.__init__(self, data)
        self.extend_time_column(self.env)
