# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
EnricherSelector is the root class of LocationClosestSelector and TimeNearestSelector.

Two subclass:
    EnricherLocationSelector: provides some basic calculations of spherical distance
    EnricherTimeSelector: provides round_to wrapper functions
"""

from ..aggregators.aggregator import Aggregator
from ..granularities.granularity import (
    Granularity, DayGranularity,
    HourGranularity, MonthGranularity)
from ..accessories.time_data import TimeData

from dateutil.relativedelta import relativedelta
from math import atan2, cos, radians, sin, sqrt
from multimethods import multimethod
from typing import List, Tuple


class EnricherSelector:
    """Root class of all enricher selectors."""

    @property
    def granularity(self) -> Granularity:
        """Get granularity."""
        return self.__granularity

    @granularity.setter
    def granularity(self, value: Granularity):
        """Set granularity."""
        self.__granularity = value

    def process(
            self,
            customer_data: TimeData,
            public_data: TimeData,
            aggregator: Aggregator,
            join_keys: List[Tuple[str, str]] = [],
            debug: bool = False):
        """Process method."""
        pass


class EnricherLocationSelector(EnricherSelector):
    """Location related fundamental calculations are static member functions."""

    # get distance between two lat long pairs
    @staticmethod
    def get_distance(lon1, lat1, lon2, lat2) -> float:
        """
        Calculate the spherical distance between two points (latitude, longitude).

        :param lon1: longitude of point 1
        :param lat1: latitude of ooint 1
        :param lon2: longitude of point 2
        :param lat2: latitude of ooint 2

        :return: the spherical distance
        """
        # Constants
        R = 6373.0

        if (lon1 is None or lat1 is None or lon2 is None or lat2 is None):
            return R

        lat1 = radians(float(lat1))
        lon1 = radians(float(lon1))
        lat2 = radians(float(lat2))
        lon2 = radians(float(lon2))

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return distance

    # find if 2 latlong pair is within 10 lat/long of each other
    @staticmethod
    def close_to(lon1, lat1, lon2, lat2) -> bool:
        """
        Check whether given two points are close enough.

        Say, the differences of latitude and longitude are both less than 10 degree.

        :param lon1: longitude of point 1
        :param lat1: latitude of ooint 1
        :param lon2: longitude of point 2
        :param lat2: latitude of ooint 2

        :return: True if they're close
        """
        if (lon1 is None or lat1 is None or lon2 is None or lat2 is None):
            return False

        lat1 = float(lat1)
        lon1 = float(lon1)
        lat2 = float(lat2)
        lon2 = float(lon2)

        if abs(lat2 - lat1) > 10:
            return False

        if 10 < abs(lon1 - lon2) < 350:
            return False

        return True


class EnricherTimeSelector(EnricherSelector):
    """Time related fundamental calculations, all are static member functions."""

    # round datetime to nearest hour
    @multimethod(HourGranularity)
    def round_to(self, g):
        """Round to hour."""
        def round_to_hour(time):
            try:
                t = time + relativedelta(minutes=30)
                return t.replace(second=0, microsecond=0, minute=0)
            except Exception:
                return time
        return round_to_hour

    @multimethod(DayGranularity)
    def round_to(self, g):
        """Round to day."""
        def round_to_day(time):
            try:
                return time.replace(second=0, microsecond=0, minute=0, hour=0)
            except Exception:
                return time
        return round_to_day

    @multimethod(MonthGranularity)
    def round_to(self, g):
        """Round to month."""
        def round_to_month(time):
            try:
                return time.replace(second=0, microsecond=0, minute=0, hour=0, day=1)
            except Exception:
                return time
        return round_to_month
