# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Granularity definitions.

location_granularity
    location_closest_granularity
time_granularity
    hour_granularity
    day_granularity
    month_granularity
"""


class Granularity:
    """Granularity base class."""

    def get_log_property(self):
        """Get log property tuple, None if no property."""
        return None


class LocationGranularity(Granularity):
    """Location granularity."""

    def get_log_property(self):
        """Get log property tuple, None if no property."""
        return None


class LocationClosestGranularity(LocationGranularity):
    """Location closest granularity."""

    def __init__(
            self,
            _cord_limit=5,
            _lower_fuzzy_boundary=2,
            _upper_fuzzy_boundary=5,
            _closest_top_n=1):
        """
        Initialize with various configs.

        cord_count is the count of customer_data after dropDuplicates(), if it's
        bigger than _cord_limit, we'll use _lower_fuzzy_boundary to do the rough
        filtering, otherwise, use _upper_fuzzy_boundary.
        all possible locations will be ranked by spherical distance of two
        locations, we'll select _closest_top_n to do further join.

        :param _cord_limit: default is 5
        :param _lower_fuzzy_boundary: default is 2
        :param _upper_fuzzy_boundary: default is 5
        :param _closest_top_n: default is 1, the bigger, the more time cost.
        """
        self.cord_limit = _cord_limit
        self.lower_fuzzy_boundary = _lower_fuzzy_boundary
        self.upper_fuzzy_boundary = _upper_fuzzy_boundary
        self.closest_top_n = _closest_top_n

    def get_log_property(self):
        """Get log property tuple, None if no property."""
        return ('ClosestN', self.closest_top_n)


class TimeGranularity(Granularity):
    """Time granularity."""

    def get_log_property(self):
        """Get log property tuple, None if no property."""
        return None


class HourGranularity(TimeGranularity):
    """Hour granularity."""

    def get_log_property(self):
        """Get log property tuple, None if no property."""
        return ('TimeGran', 'hour')


class DayGranularity(TimeGranularity):
    """Day granularity."""

    def get_log_property(self):
        """Get log property tuple, None if no property."""
        return ('TimeGran', 'day')


class MonthGranularity(TimeGranularity):
    """Month granularity."""

    def get_log_property(self):
        """Get log property tuple, None if no property."""
        return ('TimeGran', 'month')
