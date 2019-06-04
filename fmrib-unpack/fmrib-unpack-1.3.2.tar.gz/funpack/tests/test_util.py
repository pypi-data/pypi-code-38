#!/usr/bin/env python
#
# test_util.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import pytest

import funpack.util as util


def test_parseMatlabRange():
    tests = [
        ('1',      [1]),
        ('1:10',   list(range(1, 11))),
        ('1:2:10', [1, 3, 5, 7, 9]),
        ('10:-1:1', list(range(10, 0, -1))),
        ('10:-2:0', [10, 8, 6, 4, 2, 0]),
    ]

    for rng, exp in tests:
        assert util.parseMatlabRange(rng) == exp

    with pytest.raises(ValueError): util.parseMatlabRange('1:')
    with pytest.raises(ValueError): util.parseMatlabRange('1:1:')
    with pytest.raises(ValueError): util.parseMatlabRange('1:1:1:')
    with pytest.raises(ValueError): util.parseMatlabRange('1:1:1:1')
    with pytest.raises(ValueError): util.parseMatlabRange('abcde')
    with pytest.raises(ValueError): util.parseMatlabRange('a:b')
    with pytest.raises(ValueError): util.parseMatlabRange('a:b:c')


def test_parseColumnName():

    tests = [

        ('0-0.0',     ( 0,   0,  0)),
        ('1-1.1',     ( 1,   1,  1)),
        ('10-10.10',  (10,  10, 10)),
        ('1--1.1',    ( 1,  -1,  1)),
        ('10--10.10', (10, -10, 10)),
        ('f.1.1.1',     ( 1,   1,  1)),
        ('f.10.10.10',  (10,  10, 10)),
        ('f.1..1.1',    ( 1,  -1,  1)),
        ('f.10..10.10', (10, -10, 10)),
    ]

    for col, exp in tests:
        assert util.parseColumnName(col) == exp

    with pytest.raises(ValueError): util.parseColumnName('eid')
    with pytest.raises(ValueError): util.parseColumnName('f.eid')
    with pytest.raises(ValueError): util.parseColumnName('abc')
    with pytest.raises(ValueError): util.parseColumnName('10')
    with pytest.raises(ValueError): util.parseColumnName('10-')
    with pytest.raises(ValueError): util.parseColumnName('10-1')
    with pytest.raises(ValueError): util.parseColumnName('10-1-2')
    with pytest.raises(ValueError): util.parseColumnName('10-1.2.3')
    with pytest.raises(ValueError): util.parseColumnName('f.a')
    with pytest.raises(ValueError): util.parseColumnName('f.a.b')
    with pytest.raises(ValueError): util.parseColumnName('f.a.b.c')
    with pytest.raises(ValueError): util.parseColumnName('f.10.')
    with pytest.raises(ValueError): util.parseColumnName('f.10.10.')
    with pytest.raises(ValueError): util.parseColumnName('f.10.10.10.')
    with pytest.raises(ValueError): util.parseColumnName('f.10.10.10.10')
    with pytest.raises(ValueError): util.parseColumnName('f..10')
    with pytest.raises(ValueError): util.parseColumnName('f.10.10..10')


def test_generateColumnName():

    tests = [

        (( 0,   0,  0), '0-0.0'),
        (( 1,   1,  1), '1-1.1'),
        ((10,  10, 10), '10-10.10'),
        (( 1,  -1,  1), '1--1.1'),
        ((10, -10, 10), '10--10.10'),
    ]

    for var, exp in tests:
        assert util.generateColumnName(*var) == exp


def test_timed():
    with util.timed('abc'):
        pass
    with util.timed('abc'):
        pass
    with util.timed('abc', fmt='abc %s %s'):
        pass
    with util.timed(fmt='abc %s %s'):
        pass
