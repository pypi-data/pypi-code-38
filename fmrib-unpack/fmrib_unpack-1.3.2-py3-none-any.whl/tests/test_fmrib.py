#!/usr/bin/env python
#
# test_fmrib.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import textwrap as tw

import pandas as pd
import numpy  as np

import funpack.plugins.fmrib as fmrib


from . import tempdir, gen_DataTableFromDataFrame

TEST_DATES = tw.dedent("""
    2016-01-01
    2016-12-31
    2017-01-01
    2017-12-31
    2018-01-01
    2018-12-31
    """).strip().split('\n')

EXPECT_DATES = [
    2016.0, 2016.9972677595629,
    2017.0, 2017.9972602739726,
    2018.0, 2018.9972602739726]


TEST_TIMES = tw.dedent("""
    2016-01-01T07:00:00+0
    2016-01-01T19:59:59+0
    2016-12-31T07:00:00+0
    2016-12-31T19:59:59+0
    2017-01-01T07:00:00+0
    2017-01-01T19:59:59+0
    2017-12-31T07:00:00+0
    2017-12-31T19:59:59+0
    2018-01-01T07:00:00+0
    2018-01-01T19:59:59+0
    2018-12-31T07:00:00+0
    2018-12-31T19:59:59+0
    """).strip().split('\n')


EXPECT_TIMES = [
    2016.0, 2016.002732182056,  2016.9972677595629, 2016.9999999416189,
    2017.0, 2017.0027396674861, 2017.9972602739726, 2017.9999999414588,
    2018.0, 2018.0027396674861, 2018.9972602739726, 2018.9999999414588]


def test_columns_FMRIBImaging():
    fmrib.columns_FMRIBImaging('abc')


def test_load_FMRIBImaging():

    data = tw.dedent("""
    1234567  20150311  133817.240000  5.01  2  0
    1847293  20150428  130036.235000  5.01  1  1
    6821357  20151004  175803.285000  5.02  0  2
    """).strip()

    expect_index = [1234567, 1847293, 6821357]
    expect_cols  = {
        'acq_time'         : [pd.to_datetime('2015-03-11T13:38:17.24+0'),
                              pd.to_datetime('2015-04-28T13:00:36.235+0'),
                              pd.to_datetime('2015-10-04T17:58:03.285+0')],
        'acq_phase'        : [5.01, 5.01, 5.02],
        'processing_phase' : [2, 1, 0],
        'flipped_SWI'      : [0, 1, 2]
    }

    with tempdir():

        with open('data.tsv', 'wt') as f:
            f.write(data)

        result = fmrib.load_FMRIBImaging('data.tsv')

        assert np.all(result.index == expect_index)
        assert np.all(sorted(result.columns) == sorted(expect_cols.keys()))

        for colname in expect_cols.keys():
            col = pd.Series(expect_cols[colname], index=expect_index)
            assert (col == result[colname]).all()


def test_dateAsYearFraction():

    dates  = TEST_DATES
    expect = EXPECT_DATES

    dates  = [pd.to_datetime(d) for d in dates]
    result = [fmrib.dateAsYearFraction(d) for d in dates]

    assert np.all(np.isclose(expect, result))
    assert np.isnan(fmrib.dateAsYearFraction('notadate'))


def test_normalisedAcquisitionTime():

    times  = TEST_TIMES
    expect = EXPECT_TIMES

    times  = [pd.to_datetime(t) for t in times]
    result = [fmrib.normalisedAcquisitionTime(t) for t in times]

    assert np.all(np.isclose(expect, result))
    assert np.isnan(fmrib.normalisedAcquisitionTime('notatime'))


def test_format_funcs():

    dates   = TEST_DATES
    times   = TEST_TIMES[:len(dates)]
    dexpect = EXPECT_DATES
    texpect = EXPECT_TIMES[:len(dates)]

    dates = [pd.to_datetime(d) for d in dates]
    times = [pd.to_datetime(t) for t in times]


    df = pd.DataFrame()
    df['eid'] = range(1, len(dates) + 1)
    df.set_index('eid', inplace=True)
    df['1-0.0'] = dates
    df['2-0.0'] = times

    dt = gen_DataTableFromDataFrame(df)

    dresult = fmrib.format_dateAsYearFraction(
        dt, '1-0.0', dt[:, '1-0.0'])
    tresult = fmrib.format_normalisedAcquisitionTime(
        dt, '2-0.0', dt[:, '2-0.0'])

    assert (dresult == dexpect).all()
    assert (tresult == texpect).all()
