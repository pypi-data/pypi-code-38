# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
from logging import getLogger

DEFAULT_PERF_LEVEL = 0  # 0: disabled; 1: enabled
DEFAULT_PERF_PERIOD = 60
DEFAULT_PERF_BASE = 2.0
DEFAULT_PERF_UNIT = 0.1  # ms
DEFAULT_PERF_PCT_BASE = 1.3
DEFAULT_PERF_PCT_UNIT = 1.0  # %

LOGGER = getLogger(__name__)


class PerformanceMetricsSettings:
    """ Performance metrics are stored here for passing them
        to the extension. Binned metrics are not currently implemented
        in the Python agent
    """

    SETTINGS_FIELD_MAP = {
        'perf_level': 'level',
        'performance_metrics_period': 'period',
        'perf_base': 'base',
        'perf_unit': 'unit',
        'perf_pct_base': 'pct_base',
        'perf_pct_unit': 'pct_unit',
    }

    def __init__(self, level=DEFAULT_PERF_LEVEL,
                 period=DEFAULT_PERF_PERIOD,
                 base=DEFAULT_PERF_BASE,
                 unit=DEFAULT_PERF_UNIT,
                 pct_base=DEFAULT_PERF_PCT_BASE,
                 pct_unit=DEFAULT_PERF_PCT_UNIT):
        self.level = level
        self.period = period
        self.base = base
        self.unit = unit
        self.pct_base = pct_base
        self.pct_unit = pct_unit
        if self.enabled() and self.period == 0:
            LOGGER.warning("Setting performance period to default %d",
                           DEFAULT_PERF_PERIOD)
            self.period = DEFAULT_PERF_PERIOD

    @staticmethod
    def from_features(features):
        level = features.get('perf_level', DEFAULT_PERF_LEVEL)
        # old name, in Ruby not used for binned metrics:
        period = features.get('performance_metrics_period', DEFAULT_PERF_PERIOD)
        base = features.get('perf_base', DEFAULT_PERF_BASE)
        unit = features.get('perf_unit', DEFAULT_PERF_UNIT)
        pct_base = features.get('perf_pct_base', DEFAULT_PERF_PCT_BASE)
        pct_unit = features.get('perf_pct_unit', DEFAULT_PERF_PCT_UNIT)

        return PerformanceMetricsSettings(level=level, period=period,
                                          base=base, unit=unit,
                                          pct_base=pct_base, pct_unit=pct_unit)

    def as_features(self):
        return {k: getattr(self, v) for k, v in self.SETTINGS_FIELD_MAP.items()}

    # Not checked, if the extension sends data we always aggregate and fw it
    def enabled(self):
        return self.level > 0
