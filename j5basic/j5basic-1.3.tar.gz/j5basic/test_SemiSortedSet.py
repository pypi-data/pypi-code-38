#!/usr/bin/env python

"""Tests the SemiSortedSet code"""

from j5basic import SemiSortedSet
from j5test import Utils
import copy
import datetime
import random

ORWELL = datetime.date(1984,1,1)
SPACE = datetime.date(2001,1,1)
_SHUFFLE_DAYS = list(range(0, 365))
random.shuffle(_SHUFFLE_DAYS)
SPACE_YEAR = [datetime.datetime(2001,1,1) + datetime.timedelta(days=n) for n in _SHUFFLE_DAYS]

BASE_SET_CLASS = set

class TestSemiSortedSet(object):
    @classmethod
    def setup_class(cls):
        cls.empty = SemiSortedSet.SemiSortedSet()
        cls.single_item = SemiSortedSet.SemiSortedSet([1])
        cls.hundred = SemiSortedSet.SemiSortedSet(list(range(50,101))+list(range(1,50)))
        cls.date = SemiSortedSet.SemiSortedSet([ORWELL, SPACE])
        cls.space_year = SemiSortedSet.SemiSortedSet(SPACE_YEAR)

    def test_class_inheritance(self):
        assert isinstance(self.empty, BASE_SET_CLASS)
        assert isinstance(self.single_item, SemiSortedSet.SemiSortedSet)

    def test_bool(self):
        assert not self.empty
        assert self.single_item
        assert self.date

    def test_contains(self):
        assert 1 not in self.empty
        assert 1 in self.single_item
        assert 2 not in self.single_item
        assert 50 in self.hundred
        assert ORWELL in self.date
        assert SPACE in self.date

    def test_min_max(self):
        assert Utils.raises(ValueError, min, self.empty)
        assert Utils.raises(ValueError, max, self.empty)
        assert self.single_item.min() == self.single_item.max() == 1
        assert self.hundred.min() == 1
        assert self.hundred.max() == 100
        assert self.date.min() == ORWELL
        assert self.date.max() == SPACE
        assert self.space_year.min() == datetime.datetime(2001, 1, 1)
        assert self.space_year.max() == datetime.datetime(2001, 12, 31)
        # test altering operations
        hundred = self.hundred.copy()
        assert hundred.min() == 1
        assert hundred.max() == 100
        hundred.add(1000)
        assert hundred.max() == 1000
        hundred.discard(1)
        assert hundred.min() == 2
        hundred.remove(2)
        assert hundred.min() == 3
        hundred |= self.single_item
        assert hundred.min() == 1
        hundred &= self.hundred
        assert hundred.max() == 100
        # TODO: test ^= -= and method versions - difference_update, intersection_update, symettric_difference_update, update

    def test_slice(self):
        empty = self.empty.copy()
        empty.remove_lt(None)
        assert not empty
        single_item = self.single_item.copy()
        single_item.remove_lt(1)
        assert len(single_item) == 1
        single_item.remove_lt(2)
        assert len(single_item) == 0
        fifty = self.hundred.copy()
        fifty.remove_gt(50)
        assert len(fifty) == 50
        assert fifty.min() == 1
        assert fifty.max() == 50
        space_year = self.space_year.copy()
        space_year.remove_gt(datetime.datetime(2001, 1, 5, 12, 30, 32))
        assert len(space_year) == 5
        assert space_year.max() == datetime.datetime(2001, 1, 5)

