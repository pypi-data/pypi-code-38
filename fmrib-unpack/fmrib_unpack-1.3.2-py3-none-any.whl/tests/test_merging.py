#!/usr/bin/env python
#
# test_importing_mergeData.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import itertools as it
import textwrap  as tw

import pandas as pd
import numpy  as np

import funpack.importing as importing
import funpack.merging   as merging
import funpack.fileinfo  as fileinfo

from . import tempdir


def _merge_testdata(samesubjs=False, samecols=False):

    if not samecols:
        headers = [
            'eid 1-0.0 2-0.0 3-0.0',
            'eid 1-0.0 2-0.0 3-0.0 4-0.0',
            'subj one two three',
            None]
    else:
        headers = [
            'eid 1-0.0 2-0.0 3-0.0',
            'eid 2-0.0 3-0.0 4-0.0',
            'eid 1-0.0 3-0.0 4-0.0',
            'eid 2-0.0 3-0.0 4-0.0 5-0.0']

    files = []
    data  = []

    for i, hdr in enumerate(headers):
        if hdr is not None:
            # we make one file arbitrarily
            # bigger than the rest
            ncols = len(hdr.split())
            if ncols == 5:
                nrows = 3
            else:
                nrows = 2
        else:
            ncols = 4
            nrows = 2

        fdata = []
        for ri in range(nrows):

            if samesubjs: row = [1000 + ri]
            else:         row = [(i + 1) * 1000 + ri]
            for ci in range(ncols - 1):
                row.append((i + 1) * 100 + ri * 10 + ci)
            fdata.append(row)
        files.append('test{}.txt'.format(i))
        with open(files[-1], 'wt') as f:
            if hdr is not None:
                f.write(hdr + '\n')
            for r in fdata:
                f.write(' '.join([str(c) for c in r]) + '\n')

    cols = fileinfo.fileinfo(files)[2]
    for fcols, hdr, f in zip(cols, headers, files):
        data.append(pd.read_csv(f,
                                index_col=0,
                                names=[c.name for c in fcols],
                                header=None if hdr is None else 0,
                                delim_whitespace=True))

    return files, data, cols


def test_mergeData_cols_naive():

    with tempdir():
        files, data, cols = _merge_testdata()

    datacopy = [d.copy() for d in data]

    merged, mcols = merging.mergeDataFrames(datacopy, cols, 'cols', 'naive')

    # Row indices are taken from
    # the file with the most rows
    lens   = [len(d.index) for d in data]
    maxlen = max(lens)
    lidx   = lens.index(maxlen)

    expcols = [cols[lidx][0]] + list(it.chain(*[c[1:] for c in cols]))
    exprows = data[lidx].index.values

    assert mcols == expcols
    assert np.all(merged.index.values == exprows)
    assert np.all(merged.columns == [c.name for c in mcols[1:]])

    for i, col in enumerate(mcols[1:]):

        didx    = files.index(col.datafile)
        cmdata  = merged.iloc[:, i].values

        expdata        = np.empty(maxlen, dtype=np.float)
        clen           = len(data[didx].iloc[:, col.index - 1])
        expdata[:clen] =     data[didx].iloc[:, col.index - 1].values
        expdata[clen:] = np.nan

        cmnan  = np.isnan(cmdata)
        expnan = np.isnan(expdata)

        assert np.all(cmdata[~cmnan] == expdata[~expnan])
        assert np.all(cmnan          == expnan)


def test_mergeData_rows_naive():

    with tempdir():
        files, data, cols = _merge_testdata()

    datacopy = [d.copy() for d in data]

    merged, mcols = merging.mergeDataFrames(datacopy, cols, 'rows', 'naive')

    # columns are taken from the
    # file with the most columns
    lens   = [len(d.columns) for d in data]
    maxlen = max(lens)
    lidx   = lens.index(maxlen)

    expcols = cols[lidx]
    exprows = list(it.chain(*[d.index.values for d in data]))
    nrows   = len(exprows)


    assert mcols == expcols
    assert np.all(merged.index.values == exprows)
    assert np.all(merged.columns == [c.name for c in mcols[1:]])


    for i, col in enumerate(mcols[1:]):

        cmdata     = merged.iloc[:, i].values
        expdata    = np.empty(nrows, dtype=np.float)
        expdata[:] = np.nan

        rowoff = 0
        for d in data:
            if (col.index - 1) < len(d.columns):
                dcd = d.iloc[:, col.index - 1]
                expdata[rowoff:rowoff + len(dcd)] = dcd
            rowoff += len(d.index)

        cmnan  = np.isnan(cmdata)
        expnan = np.isnan(expdata)

        assert np.all(cmdata[~cmnan] == expdata[~expnan])
        assert np.all(cmnan          == expnan)



def test_mergeData_cols_inner():

    with tempdir():
        files, data, cols = _merge_testdata(samesubjs=True)

    datacopy = [d.copy() for d in data]

    merged, mcols = merging.mergeDataFrames(datacopy, cols, 'cols', 'inner')

    # only rows for subjects which
    # are present in all files should
    # be present in the merged data.
    expcols = [cols[0][0]] + list(it.chain(*[c[1:] for c in cols]))
    exprows = list(sorted(set.intersection(*[set(d.index.values)
                                             for d in data])))

    assert mcols == expcols
    assert np.all(merged.index.values == exprows)
    assert np.all(merged.columns == [c.name for c in mcols[1:]])

    for rid in exprows:
        row = []

        for d in data:
            if rid not in d.index:
                continue

            row.extend(list(d.loc[rid, :].values))

        assert np.all(merged.loc[rid, :] == row)


def test_mergeData_cols_outer():

    with tempdir():
        files, data, cols = _merge_testdata(samesubjs=True)

    datacopy = [d.copy() for d in data]

    merged, mcols = merging.mergeDataFrames(datacopy, cols, 'cols', 'outer')

    # rows for subjects which are
    # present in any files should
    # be present in the merged data.
    expcols = [cols[0][0]] + list(it.chain(*[c[1:] for c in cols]))
    exprows = list(sorted(set.union(*[set(d.index.values)
                                      for d in data])))

    assert mcols == expcols
    assert np.all(merged.index.values == exprows)
    assert np.all(merged.columns == [c.name for c in mcols[1:]])

    for rid in exprows:
        row = []

        for d in data:
            if rid not in d.index:
                row.extend([np.nan] * len(d.columns))
                continue

            row.extend(list(d.loc[rid, :].values))

        exp    = np.array(row)
        got    = merged.loc[rid, :]
        expnan = np.isnan(exp)
        gotnan = np.isnan(got)

        assert np.all(gotnan       == expnan)
        assert np.all(got[~gotnan] == exp[~expnan])


def test_mergeData_rows_inner():

    with tempdir():
        files, data, cols = _merge_testdata(samecols=True)

    datacopy = [d.copy() for d in data]

    merged, mcols = merging.mergeDataFrames(datacopy, cols, 'rows', 'inner')

    # expected columns are those
    # which are present in all
    # files
    colnames = [[c.name for c in cc[1:]] for cc in cols]
    joined   = set.intersection(*[set(c) for c in colnames])
    allcols  = list(it.chain(*[c[1:] for c in cols]))
    colnames = list(it.chain(*colnames))

    colidxs = [colnames.index(j) for j in joined]
    expcols = [cols[0][0]] + [allcols[i] for i in colidxs]

    assert np.all(merged.columns == [ec.name for ec in expcols[1:]])
    assert mcols == expcols

    for col in mcols[1:]:
        coldata = merged.loc[:, col.name].values
        expdata = []
        for d in datacopy:
            expdata.extend(list(d.loc[:, col.name].values))
        assert np.all(coldata == expdata)


def test_mergeData_rows_outer():

    with tempdir():
        files, data, cols = _merge_testdata(samecols=True)

    datacopy = [d.copy() for d in data]

    merged, mcols = merging.mergeDataFrames(datacopy, cols, 'rows', 'outer')

    # all columns should be
    # present, in the correct
    # order
    uniqnames = []
    uniqcols  = []

    for col in it.chain(*[c[1:] for c in cols]):
        if col.name not in uniqnames:
            uniqnames.append(col.name)
            uniqcols .append(col)
    expcols = [cols[0][0]] + uniqcols

    exprows = list(it.chain(*[d.index for d in datacopy]))

    assert np.all(merged.index.values == exprows)
    assert np.all(merged.columns == [ec.name for ec in expcols[1:]])
    assert mcols == expcols

    for col in mcols[1:]:
        got = merged.loc[:, col.name].values
        exp = []

        for d in datacopy:
            if col.name in d.columns:
                exp += list(d.loc[:, col.name].values)

            else:
                exp += [np.nan] * len(d.index)

        exp    = np.array(exp)
        gotnan = np.isnan(got)
        expnan = np.isnan(exp)

        assert np.all(gotnan == expnan)
        assert np.all(got[~gotnan] == exp[~expnan])



def test_mergeData_non0_indexes_cols():

    data1 = tw.dedent("""
    eid,col1,col2
    1,11,21
    2,12,22
    3,13,23
    """)
    data2 = tw.dedent("""
    col3,eid,col4
    31,1,41
    32,2,42
    33,3,43
    """)
    data3 = tw.dedent("""
    col5,col6,eid
    51,61,1
    52,62,2
    53,63,3
    """)

    with tempdir():
        with open('data1.txt', 'wt') as f: f.write(data1)
        with open('data2.txt', 'wt') as f: f.write(data2)
        with open('data3.txt', 'wt') as f: f.write(data3)

        cols = fileinfo.fileinfo(['data1.txt', 'data2.txt', 'data3.txt'],
                                 indexes={'data1.txt' : 0,
                                          'data2.txt' : 1,
                                          'data3.txt' : 2})[2]

        df1 = pd.read_csv('data1.txt', delimiter=',', index_col=0)
        df2 = pd.read_csv('data2.txt', delimiter=',', index_col=1)
        df3 = pd.read_csv('data3.txt', delimiter=',', index_col=2)

        merged, gotcols = merging.mergeDataFrames([df1, df2, df3],
                                                  cols,
                                                  axis='variables',
                                                  strategy='inner')


        expcols = cols[0] + [cols[1][0], cols[1][2], cols[2][0], cols[2][1]]

        assert gotcols == expcols
        assert np.all(merged.columns == [e.name for e in expcols[1:]])
        assert np.all(merged.index   == [1,  2,  3])
        assert np.all(merged['col1'] == [11, 12, 13])
        assert np.all(merged['col2'] == [21, 22, 23])
        assert np.all(merged['col3'] == [31, 32, 33])
        assert np.all(merged['col4'] == [41, 42, 43])
        assert np.all(merged['col5'] == [51, 52, 53])
        assert np.all(merged['col6'] == [61, 62, 63])


def test_mergeData_non0_indexes_rows():

    data1 = tw.dedent("""
    eid,col1,col2
    1,11,21
    2,12,22
    3,13,23
    """)
    data2 = tw.dedent("""
    col1,eid,col2
    14,4,24
    15,5,25
    16,6,26
    """)
    data3 = tw.dedent("""
    col1,col2,eid
    17,27,7
    18,28,8
    19,29,9
    """)

    with tempdir():

        with open('data1.txt', 'wt') as f: f.write(data1)
        with open('data2.txt', 'wt') as f: f.write(data2)
        with open('data3.txt', 'wt') as f: f.write(data3)

        cols = fileinfo.fileinfo(['data1.txt', 'data2.txt', 'data3.txt'],
                                 indexes={'data1.txt' : 0,
                                          'data2.txt' : 1,
                                          'data3.txt' : 2})[2]

        df1 = pd.read_csv('data1.txt', delimiter=',', index_col=0)
        df2 = pd.read_csv('data2.txt', delimiter=',', index_col=1)
        df3 = pd.read_csv('data3.txt', delimiter=',', index_col=2)

        merged, gotcols = merging.mergeDataFrames([df1, df2, df3],
                                                  cols,
                                                  axis='subjects',
                                                  strategy='inner')

        expcols = cols[0]

        assert gotcols == expcols
        assert np.all(merged.columns == [e.name for e in expcols[1:]])
        assert np.all(merged.index   == np.arange( 1, 10))
        assert np.all(merged['col1'] == np.arange(11, 20))
        assert np.all(merged['col2'] == np.arange(21, 30))


def test_mergeData_different_index_names():
    data1 = tw.dedent("""
    id1,col1,col2
    1,14,24
    2,15,25
    3,16,26
    """)
    data2 = tw.dedent("""
    id2,col1,col2
    1,17,27
    2,18,28
    3,19,29
    """)

    with tempdir():
        with open('data1.txt', 'wt') as f: f.write(data1)
        with open('data2.txt', 'wt') as f: f.write(data2)

        cols = fileinfo.fileinfo(['data1.txt', 'data2.txt'])[2]

        df1 = pd.read_csv('data1.txt', delimiter=',')
        df2 = pd.read_csv('data2.txt', delimiter=',')

        merged, gotcols = merging.mergeDataFrames([df1, df2],
                                                  cols,
                                                  axis='subjects',
                                                  strategy='inner')

        assert gotcols[0] == cols[0][0]
        assert merged.index.name == 'id1'
