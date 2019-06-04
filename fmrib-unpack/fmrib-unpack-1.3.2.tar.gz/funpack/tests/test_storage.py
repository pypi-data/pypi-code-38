#!/usr/bin/env python
#
# test_storage.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import multiprocessing as mp
import functools       as ft
import                    warnings

import numpy  as np
import pandas as pd
import           pytest


import funpack.storage as storage

from . import tempdir, gen_test_data


def test_HDFStoreCollection_attrs():
    with tempdir() as td:

        gen_test_data(50, 100, 'data1.txt', start_subj=1)
        gen_test_data(50, 100, 'data2.txt', start_subj=101)

        df1 = pd.read_csv('data1.txt', delimiter='\t', index_col='eid')
        df2 = pd.read_csv('data2.txt', delimiter='\t', index_col='eid')

        store = storage.HDFStoreCollection(prefix='mypref',
                                           workDir=td,
                                           colsPerFile=10)

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            store.append(df1)
            store.append(df2)

        assert        store.prefix      == 'mypref'
        assert        store.colsPerFile == 10
        assert        store.workDir     == td
        assert        store.nrows       == 200
        assert    len(store)            == 200
        assert        store.ncols       == 50
        assert np.all(store.columns     == df1.columns)
        assert np.all(store.index       == np.concatenate((df1.index,
                                                           df2.index)))
        for i, col in enumerate(df1.columns):
            assert store.columnIndex(col) == int(i / 10)

        blocks = store.columnBlocks(df1.columns)

        for i in range(5):
            exp = df1.columns[i * 10:i * 10 + 10]
            assert np.all(blocks[i]          == exp)
            assert np.all(store.columnsIn(i) == exp)


def test_HDFStoreCollection_bad_append():
    with tempdir():

        # columns don't match
        gen_test_data(10, 100, 'data1.txt', start_subj=1)
        gen_test_data(5,  100, 'data2.txt', start_subj=101)

        df1 = pd.read_csv('data1.txt', delimiter='\t', index_col='eid')
        df2 = pd.read_csv('data2.txt', delimiter='\t', index_col='eid')

        store = storage.HDFStoreCollection()

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            store.append(df1)

        with pytest.raises(ValueError):
            store.append(df2)


def test_HDFStoreCollection_read():

    with tempdir():

        gen_test_data(20, 100, 'data1.txt', start_subj=1)
        gen_test_data(20, 100, 'data2.txt', start_subj=101)

        df1 = pd.read_csv('data1.txt', delimiter='\t', index_col='eid')
        df2 = pd.read_csv('data2.txt', delimiter='\t', index_col='eid')
        df  = pd.concat((df1, df2), axis=0)

        store = storage.HDFStoreCollection(colsPerFile=5)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            store.append(df1)
            store.append(df2)

        tests = [
            slice(None),
            slice(20, 40),
            slice(20, 40, 2),
            (slice(None),       '1-0.0'),
            (slice(None),       '2-0.0'),
            (slice(None),       '10-0.0'),
            (slice(None),      ['8-0.0', '9-0.0', '10-0.0']),
            (slice(None),      ['4-0.0', '9-0.0', '16-0.0']),
            (slice(20, 30),     '2-0.0'),
            (slice(20, 30, 2),  '2-0.0'),
            (slice(20, 50),    ['2-0.0', '3-0.0']),
            (slice(20, 50),    ['2-0.0', '3-0.0', '6-0.0', '18-0.0']),
        ]

        for test in tests:
            got = store.loc[test]
            exp = df   .loc[test]

            assert np.all(got == exp)


def test_HDFStoreCollection_write():

    with tempdir():

        gen_test_data(20, 50, 'data1.txt', start_subj=1)
        gen_test_data(20, 50, 'data2.txt', start_subj=51)

        df1   = pd.read_csv('data1.txt', delimiter='\t', index_col='eid')
        df2   = pd.read_csv('data2.txt', delimiter='\t', index_col='eid')

        store = storage.HDFStoreCollection(colsPerFile=5)

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            store.append(df1)
            store.append(df2)

        # write one column at a time
        for col in df1.columns:

            newdata = pd.Series(np.random.randint(1, 10, 100),
                                index=np.concatenate((df1.index, df2.index)),
                                name=col)

            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                store.loc[:, col] = newdata

            assert np.all(store.loc[:, col] == newdata)

        # write several columns at a time
        tests = [
            [1, 2],
            [1, 6],
            [1, 7, 13, 17, 18],
        ]

        for test in tests:

            cols = ['{}-0.0'.format(t) for t in test]

            newdata = pd.DataFrame(
                np.random.randint(1, 10, (100, len(cols))),
                index=np.concatenate((df1.index, df2.index)),
                columns=cols)

            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                store.loc[:, cols] = newdata

            assert np.all(store.loc[:, cols] == newdata)


def _parallel_read_job(st, col):
    return st.loc[:, col].mean()


def test_HDFStoreCollection_parallel_read():

    with tempdir(), mp.Pool(10) as pool:

        gen_test_data(20, 100, 'data1.txt', start_subj=1)
        gen_test_data(20, 100, 'data2.txt', start_subj=51)

        df1   = pd.read_csv('data1.txt', delimiter='\t', index_col='eid')
        df2   = pd.read_csv('data2.txt', delimiter='\t', index_col='eid')
        df    = pd.concat((df1, df2), axis=0)
        store = storage.HDFStoreCollection(colsPerFile=5)

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            store.append(df1)
            store.append(df2)

        got = pool.map(ft.partial(_parallel_read_job, store), df.columns)
        exp = [df[col].mean() for col in df.columns]

        got = np.array(got)
        exp = np.array(exp)

        assert np.all(got == exp)


def _parallel_write_job(st, col):
    data           = st.loc[:, col]
    st.loc[:, col] = data * 2


def test_HDFStoreCollection_parallel_write():

    with tempdir(), mp.Pool(10) as pool:

        mgr  = mp.Manager()

        gen_test_data(20, 100, 'data1.txt', start_subj=1)
        gen_test_data(20, 100, 'data2.txt', start_subj=51)

        df1   = pd.read_csv('data1.txt', delimiter='\t', index_col='eid')
        df2   = pd.read_csv('data2.txt', delimiter='\t', index_col='eid')
        df    = pd.concat((df1, df2), axis=0)
        store = storage.HDFStoreCollection(colsPerFile=5, mgr=mgr)

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            store.append(df1)
            store.append(df2)

        pool.map(ft.partial(_parallel_write_job, store), df.columns)

        got = store.loc[:]
        exp = df * 2

        assert np.all(got == exp)



def test_HDFStoreCollection_dropRows():

    with tempdir(), mp.Pool(10) as pool:

        mgr = mp.Manager()

        gen_test_data(50, 500, 'data1.txt', start_subj=1)
        gen_test_data(50, 500, 'data2.txt', start_subj=501)

        df1    = pd.read_csv('data1.txt', delimiter='\t', index_col='eid')
        df2    = pd.read_csv('data2.txt', delimiter='\t', index_col='eid')
        df     = pd.concat((df1, df2), axis=0)
        store1 = storage.HDFStoreCollection(colsPerFile=5, mgr=mgr)
        store2 = storage.HDFStoreCollection(colsPerFile=5, mgr=mgr)

        mask = np.random.choice(np.arange(1, 101), size=50, replace=False)

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            store1.append(df1)
            store1.append(df2)
            store2.append(df1)
            store2.append(df2)
            store1.dropRows(mask)
            store2.dropRows(mask, pool)

        exp = df.loc[mask, :]

        assert np.all(store1.index  == exp.index)
        assert np.all(store1.loc[:] == exp.loc[:, :])
        assert np.all(store2.index  == exp.index)
        assert np.all(store2.loc[:] == exp.loc[:, :])

        # test with a boolean mask
        df   = exp
        mask = np.random.randint(1, 11, len(df.index)) > 5

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            store1.dropRows(mask)
            store2.dropRows(mask, pool)

        exp = df.loc[mask, :]
        assert np.all(store1.index  == exp.index)
        assert np.all(store1.loc[:] == exp.loc[:, :])
        assert np.all(store2.index  == exp.index)
        assert np.all(store2.loc[:] == exp.loc[:, :])


def test_HDFStoreCollection_dropColumns():

    with tempdir(), mp.Pool(10) as pool:

        mgr = mp.Manager()

        gen_test_data(50, 500, 'data1.txt', start_subj=1)
        gen_test_data(50, 500, 'data2.txt', start_subj=501)

        df1    = pd.read_csv('data1.txt', delimiter='\t', index_col='eid')
        df2    = pd.read_csv('data2.txt', delimiter='\t', index_col='eid')
        df     = pd.concat((df1, df2), axis=0)
        store1 = storage.HDFStoreCollection(colsPerFile=5, mgr=mgr)
        store2 = storage.HDFStoreCollection(colsPerFile=5, mgr=mgr)

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            store1.append(df1)
            store1.append(df2)
            store2.append(df1)
            store2.append(df2)

        drop = np.random.choice(df.columns, size=20, replace=False)
        keep = [c for c in df.columns if c not in drop]

        store1.dropColumns(drop)
        store2.dropColumns(drop, pool)

        exp = df.loc[:, keep]

        assert np.all(store1.columns  == exp.columns)
        assert np.all(store1.loc[:]   == exp.loc[:, :])
        assert np.all(store2.columns  == exp.columns)
        assert np.all(store2.loc[:]   == exp.loc[:, :])
