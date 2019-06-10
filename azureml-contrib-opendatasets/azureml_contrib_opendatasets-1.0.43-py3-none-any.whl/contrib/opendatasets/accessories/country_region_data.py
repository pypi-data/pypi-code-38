# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Location data, with supported column classes."""

from typing import Optional
from enum import Enum


class CORAvailableType(Enum):
    """
    a class defins country or region related property type below.

        CountryCode
        CountryOrRegionName
    """

    Unknown = 0
    CountryCode = 1
    CountryOrRegionName = 2
    All = CountryCode | CountryOrRegionName


class CountryOrRegionColumn:
    """
    a class defins country or region related properties below.

        countrycode_column_name
        country_or_region_column_name
    """

    def __init__(self, countrycode_name: Optional[str] = None, country_or_region_name: Optional[str] = None):
        """Initialize countrycode and country_or_region column names."""
        self.__countrycode_column_name = countrycode_name
        self.__country_or_region_column_name = country_or_region_name
        i = 0
        if self.__countrycode_column_name is not None:
            i |= CORAvailableType.CountryCode.value
        if self.__country_or_region_column_name is not None:
            i |= CORAvailableType.CountryOrRegionName.value
        self.__available_column_type = CORAvailableType(i)

    @property
    def countrycode_column_name(self):
        """Get countrycode column name."""
        return self.__countrycode_column_name

    @property
    def country_or_region_column_name(self) -> str:
        """Get country_or_region column name."""
        return self.__country_or_region_column_name

    @property
    def available_column_type(self) -> Optional[CORAvailableType]:
        """Get available column type, CountryCode, CountryOrRegionName or both of them."""
        return self.__available_column_type


class CountryOrRegionData:
    """
    A class defines location two related properties below.

    countrycode_column_name
    country_or_region_column_name
    """

    @property
    def countrycode_column_name(self):
        """Get latitude column name."""
        return self.__countrycode_column_name

    @countrycode_column_name.setter
    def countrycode_column_name(self, value: str):
        """Set latitude column name."""
        self.__countrycode_column_name = value

    @property
    def country_or_region_column_name(self) -> str:
        """Get longitude column name."""
        return self.__country_or_region_column_name

    @country_or_region_column_name.setter
    def country_or_region_column_name(self, value: str):
        """Set longitude column name."""
        self.__country_or_region_column_name = value

    @property
    def available_column_type(self) -> CORAvailableType:
        """Get longitude column name."""
        return self.__available_column_type

    @available_column_type.setter
    def available_column_type(self, value: CORAvailableType):
        """Set longitude column name."""
        self.__available_column_type = value
