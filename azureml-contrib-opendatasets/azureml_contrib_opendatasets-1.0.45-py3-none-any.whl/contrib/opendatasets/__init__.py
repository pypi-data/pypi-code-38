# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Enable consuming Azure open datasets into dataframes and enrich customer data."""

from ._boston_reported_crime import BostonReportedCrime
from ._boston_safety import BostonSafety
from ._chicago_reported_crime import ChicagoReportedCrime
from ._chicago_safety import ChicagoSafety
from ._noaa_gfs_weather import NoaaGfsWeather
from ._noaa_isd_weather import NoaaIsdWeather
from ._nyc_reported_crime import NycReportedCrime
from ._nyc_safety import NycSafety
from ._nyc_tlc_fhv import NycTlcFhv
from ._nyc_tlc_green import NycTlcGreen
from ._nyc_tlc_yellow import NycTlcYellow
from ._public_holidays import PublicHolidays
from ._sanfrancisco_reported_crime import SanFranciscoReportedCrime
from ._sanfrancisco_safety import SanFranciscoSafety
from ._seattle_reported_crime import SeattleReportedCrime
from ._seattle_safety import SeattleSafety

__all__ = [
    'BostonReportedCrime',
    'BostonSafety',
    'ChicagoReportedCrime',
    'ChicagoSafety',
    'NoaaGfsWeather',
    'NoaaIsdWeather',
    'NycReportedCrime',
    'NycSafety',
    'NycTlcFhv',
    'NycTlcGreen',
    'NycTlcYellow',
    'PublicHolidays',
    'SanFranciscoReportedCrime',
    'SanFranciscoSafety',
    'SeattleReportedCrime',
    'SeattleSafety'
]
