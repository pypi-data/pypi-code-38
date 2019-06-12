# -*- coding: utf-8 -*-

"""Test module for Ranges"""

from j5basic import Ranges
from j5basic import DictUtils

def run_ranges_tst(ranges, expected_tagmap, expected_axislist):
    if isinstance(ranges, list):
        ranges = dict([("tag%d" % n, tagrange) for n, tagrange in enumerate(ranges)])
    tagmap = Ranges.calculateaxes(ranges)
    DictUtils.assert_dicts_equal(tagmap, expected_tagmap)
    axismap = Ranges.tagmaptoaxismap(tagmap)
    axislist = Ranges.sortaxes(axismap)
    assert axislist == expected_axislist

def test_basic():
    ranges = [(0,10), (0, 20), (10, 60), (0, 100), (-100, 100)]
    tagmap = {"tag0": (0, (0, 20)), "tag1": (0, (0, 20)), "tag2": (0, (-100, 100)), "tag3": (0, (-100, 100)), "tag4": (0, (-100, 100))}
    run_ranges_tst(ranges, tagmap, [(0, 20), (-100, 100)])

def test_sparse():
    ranges = [(-1677.71, 1815.36), (-176.91, 672.66), (-12610.91, 45265.69), (-3.05, 13.10), (-36.48, 128.97), (-5.58, 27.89), (-26.56, 138.48)]
    tagmap = {'tag0': (0, (-1678, 1816)), 'tag1': (0, (-177, 673)), 'tag2': (0, (-12611, 45266)), 'tag3': (0, (-6, 28)), 'tag4': (0, (-37, 139)), 'tag5': (0, (-6, 28)), 'tag6': (0, (-37, 139))}
    run_ranges_tst(ranges, tagmap, [(-6, 28), (-37, 139), (-177, 673), (-1678, 1816), (-12611, 45266)])

def test_labelled():
    ranges = {'ramp3': (1564.0, 8021.0), 'ramp2': (1555.0, 8005.0), 'ramp1': (1512.0, 7963.0)}
    tagmap = {'ramp3': (0, (1512, 8021)), 'ramp2': (0, (1512, 8021)), 'ramp1': (0, (1512, 8021))}
    run_ranges_tst(ranges, tagmap, [(1512, 8021)])

