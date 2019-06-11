#! /usr/bin/env python
# encoding: utf-8
from __future__ import absolute_import, division, print_function

import numpy as np

from ._utils import check_range


def _rand_in_range(range_):
    min_, max_ = range_
    return np.random.random() * (max_ - min_) + min_


class Parameters(object):
    """
    Collection of used parameters incl. names and ranges.
    """

    def __init__(self):
        self.limits = {}
        self.start_values = {}
        self.names = []

    def add(self, name, range_, start_value=None):
        """
        Adds a parameter with given `name` and value `range_` to the collection.

        :param name: Name of type ``str``.
        :param range_: Allowed range as ``tuple`` or ``list`` of two ``float``
                       values. First value must be smaller than the second.
        :param start_value: optional value to start sampling from, reduces burn-in
                            phase if estimation for parameter exists.
        """

        check_range(range_)

        if name in self.names:
            raise ValueError("parameter named {!r} already added".format(name))

        self.limits[name] = range_
        self.start_values[name] = start_value
        self.names.append(name)

    def _is_in_bounds(self, name, value):
        min_, max_ = self.limits[name]
        return min_ <= value <= max_

    def _range_length(self, name):
        min_, max_ = self.limits[name]
        return max_ - min_

    def __len__(self):
        return len(self.names)

    def start_value(self, name):
        assert name in self.start_values, (name, self.start_values)
        given_start_value = self.start_values[name]
        if given_start_value is not None:
            return given_start_value
        return _rand_in_range(self.limits[name])
