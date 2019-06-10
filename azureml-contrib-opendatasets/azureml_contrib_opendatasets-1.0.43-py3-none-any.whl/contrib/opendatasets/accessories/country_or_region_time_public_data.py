# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Public data with country_or_region and time columns can be wrapped with this class."""

from .country_region_data import CountryOrRegionData
from .public_data import PublicData
from .time_data import TimePublicData

from typing import List, Optional


class CountryOrRegionTimePublicData(CountryOrRegionData, TimePublicData):
    """A class wrapper public_data which contains both country or region column and time column."""

    def __init__(self, cols: Optional[List[str]], enable_telemetry: bool = True):
        """
        Initialize the class with optional list of column names.

        :param cols: the column name list which the user wants to enrich from public data
        :param enable_telemetry: whether to send telemetry
        """
        PublicData.__init__(self, cols, enable_telemetry=enable_telemetry)
