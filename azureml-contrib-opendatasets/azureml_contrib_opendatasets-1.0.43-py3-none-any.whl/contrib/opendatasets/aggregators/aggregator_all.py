# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Aggregator all class, a.k.a. no aggregation."""

from .aggregator import Aggregator


class AggregatorAll(Aggregator):
    """Simply return all columns."""

    def __init__(self):
        """Initialize with should_direct_join as False."""
        self.should_direct_join = False

    def get_log_property(self):
        """Get log property tuple, None if no property."""
        return ('Aggregator', 'all')
