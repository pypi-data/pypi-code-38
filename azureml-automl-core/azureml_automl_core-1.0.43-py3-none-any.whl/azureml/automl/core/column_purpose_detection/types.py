# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Convenience names for long types."""
from typing import Tuple

from ..stats_computation import RawFeatureStats

# Stats and column purposes type
StatsAndColumnPurposeType = Tuple[RawFeatureStats, str, str]
