# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Public data with location and time columns can be wrapped with this class."""

from .location_data import LocationData
from .public_data import PublicData
from .time_data import TimePublicData

from typing import List, Optional


class LocationTimePublicData(LocationData, TimePublicData):
    """A class wrapper public_data which contains both location column and time column."""

    def __init__(self, cols: Optional[List[str]], enable_telemetry: bool = True):
        """
        Initialize with columns.

        :param cols: the column name list which the user wants to enrich from public data
        :param enable_telemetry: whether to send telemetry
        """
        PublicData.__init__(self, cols, enable_telemetry=enable_telemetry)
