#!/usr/bin/env python
#
# test_processing_functions.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import string
import random

import numpy  as np
import pandas as pd

import funpack.importing            as importing
import funpack.util                 as util
import funpack.processing_functions as pfns

from . import (gen_DataTable,
               tempdir,
               gen_tables)


def test_removeIfSparse():

    sparse = np.random.random(100)
    good   = np.random.random(100)

    sparse[:50] = np.nan

    dtable = gen_DataTable([good, sparse])
    remove = pfns.removeIfSparse(dtable, [1, 2], minpres=60)
    remove = [r.name for r in remove]
    assert remove == ['2-0.0']

    dtable = gen_DataTable([good, sparse])
    remove = pfns.removeIfSparse(dtable, [1, 2], minpres=40)
    remove = [r.name for r in remove]
    assert remove == []


def test_removeIfSparse_typed():

    mincat = np.zeros(100)
    good   = np.zeros(100)
    maxcat = np.zeros(100)

    mincat[:5]  = 1
    maxcat[:95] = 1
    good[  :50] = 1

    dtable = gen_DataTable([mincat, good, maxcat])
    dtable.vartable.loc[1, 'Type'] = util.CTYPES.categorical_single
    dtable.vartable.loc[2, 'Type'] = util.CTYPES.categorical_single
    dtable.vartable.loc[3, 'Type'] = util.CTYPES.categorical_single
    remove = pfns.removeIfSparse(dtable, [1, 2, 3], mincat=10, maxcat=90)
    remove = [r.name for r in remove]
    assert remove == ['1-0.0', '3-0.0']

    dtable.vartable.loc[1, 'Type'] = util.CTYPES.unknown
    dtable.vartable.loc[2, 'Type'] = util.CTYPES.unknown
    dtable.vartable.loc[3, 'Type'] = util.CTYPES.unknown
    remove = pfns.removeIfSparse(dtable, [1, 2, 3], mincat=10, maxcat=90)
    remove = [r.name for r in remove]
    assert remove == []

    remove = pfns.removeIfSparse(dtable, [1, 2, 3], mincat=10, maxcat=90,
                                 ignoreType=True)
    remove = [r.name for r in remove]
    assert remove == ['1-0.0', '3-0.0']


def test_removeIfRedundant():

    series1 = np.sin(np.linspace(0, np.pi * 6, 100))
    series2 = series1 + np.random.random(100)
    corr    = pd.Series(series1).corr(pd.Series(series2))

    dtable = gen_DataTable([series1, series2])
    remove = pfns.removeIfRedundant(dtable, [1, 2], corr * 0.9)
    remove = [r.name for r in remove]

    assert remove == ['2-0.0']

    dtable = gen_DataTable([series1, series2])
    remove = pfns.removeIfRedundant(dtable, [1, 2], corr * 1.1)
    remove = [r.name for r in remove]

    assert remove == []


def test_binariseCateorical():

    data = np.random.randint(1, 10, (50, 14))
    data[:, 0] = np.arange(1, 51)
    cols = ['eid',
            '1-0.0', '1-1.0',
            '2-0.0', '2-1.0', '2-2.0',
            '3-0.0',
            '4-0.0', '4-0.1', '4-0.2',
            '5-0.0', '5-0.1', '5-1.0', '5-1.1']

    vids  = list(range(1, 6))
    didxs = list(range(1, 14))

    with tempdir():
        np.savetxt('data.txt', data, delimiter=',', header=','.join(cols))
        vartable, proctable, cattable = gen_tables(range(1, 13))[:3]
        dt, _ = importing.importData('data.txt', vartable, proctable, cattable)

        remove, add, addvids, meta = pfns.binariseCategorical(
            dt, vids,
            acrossVisits=False,
            acrossInstances=False,
            nameFormat='{vid}-{visit}.{instance}.{value}')

        names = [cols[i] for i in didxs]
        assert [r.name for r in remove] == names

        uniqs = [(i, np.unique(data[:, i])) for i in didxs]
        offset = 0

        for didx, duniqs in uniqs:

            for u in duniqs:

                exp = data[:, didx] == u
                i = offset
                offset += 1

                assert addvids[i] == int(cols[didx].split('-')[0])
                assert add[i].name == '{}.{}'.format(cols[didx], int(u))
                assert (add[i] == exp).all()
                assert meta[i] == u

        remove, add, addvids, meta = pfns.binariseCategorical(
            dt, vids,
            acrossVisits=True,
            acrossInstances=False,
            nameFormat='{vid}.{instance}.{value}')

        names = []
        offset = 0
        for vid in vids:
            for instance in dt.instances(vid):
                cols = [c.name for c in dt.columns(vid, instance=instance)]
                uniqs = sorted(np.unique(dt[:, cols]))
                names.extend(cols)

                for u in uniqs:
                    exp = np.any(dt[:, cols] == u, axis=1)

                    i = offset
                    offset += 1
                    got = add[i]
                    assert addvids[i] == vid
                    assert got.name == '{}.{}.{}'.format(vid, instance, int(u))
                    assert (got == exp).all()
                    assert meta[i] == u
        assert names == [r.name for r in remove]

        remove, add, addvids, meta = pfns.binariseCategorical(
            dt, vids,
            acrossVisits=False,
            acrossInstances=True,
            nameFormat='{vid}.{visit}.{value}')

        names = []
        offset = 0
        for vid in vids:
            for visit in dt.visits(vid):
                cols = [c.name for c in dt.columns(vid, visit=visit)]
                uniqs = sorted(np.unique(dt[:, cols]))
                names.extend(cols)

                for u in uniqs:
                    exp = np.any(dt[:, cols] == u, axis=1)

                    i = offset
                    offset += 1
                    got = add[i]
                    assert addvids[i] == vid
                    assert got.name == '{}.{}.{}'.format(vid, visit, int(u))
                    assert (got == exp).all()
                    assert meta[i] == u
        assert names == [r.name for r in remove]

        remove, add, addvids, meta = pfns.binariseCategorical(
            dt, vids,
            acrossVisits=True,
            acrossInstances=True,
            nameFormat='{vid}.{value}')

        names = []
        offset = 0
        for vid in vids:
            cols = [c.name for c in dt.columns(vid)]
            uniqs = sorted(np.unique(dt[:, cols]))
            names.extend(cols)

            for u in uniqs:
                exp = np.any(dt[:, cols] == u, axis=1)

                i = offset
                offset += 1
                got = add[i]
                assert addvids[i] == vid
                assert got.name == '{}.{}'.format(vid, int(u))
                assert (got == exp).all()
                assert meta[i] == u
        assert names == [r.name for r in remove]


def test_binariseCateorical_no_replace():

    data = np.random.randint(1, 10, (50, 3))
    data[:, 0] = np.arange(1, 51)
    cols = ['eid', '1-0.0', '2-0.0']
    vids  = [1, 2]

    with tempdir():
        np.savetxt('data.txt', data, delimiter=',', header=','.join(cols))
        vartable, proctable, cattable = gen_tables(vids)[:3]
        dt, _ = importing.importData('data.txt', vartable, proctable, cattable)

        remove, add, addvids, meta = pfns.binariseCategorical(
            dt, [1], replace=False, nameFormat='{vid}.{value}')

        uniq = np.unique(data[:, 1])

        assert len(remove)  == 0
        assert len(add)     == len(uniq)
        assert len(addvids) == len(uniq)

        assert sorted(uniq) == sorted(meta)

        assert sorted([c.name for c in add]) == \
               sorted(['1.{}'.format(u) for u in uniq])
        assert np.all([v == 1 for v in addvids])


def test_binariseCategorical_nonnumeric():

    data = [random.choice(string.ascii_letters[:8]) for i in range(40)]
    data = [data[:20], data[20:]]

    with tempdir():
        with open('data.txt', 'wt') as f:
            f.write('eid, 1-0.0, 1-1.0\n')
            for i, (v1, v2) in enumerate(zip(*data)):
                f.write('{}, {}, {}\n'.format(i + 1, v1, v2))

        vartable, proctable, cattable = gen_tables([1])[:3]
        dt, _ = importing.importData('data.txt', vartable, proctable, cattable)

        remove, add, addvids, meta = pfns.binariseCategorical(
            dt, [1],
            acrossVisits=True,
            acrossInstances=True,
            nameFormat='{vid}.{value}')

        unique   = set(data[0] + data[1])
        remnames = [r.name for r in remove]
        addnames = [a.name for a in add]

        assert '1-0.0' in remnames and '1-1.0' in remnames
        assert len(addvids) == len(add)
        assert all([v == 1 for v in addvids])
        assert sorted(unique) == sorted(meta)

        for u in unique:
            name = '1.{}'.format(u)
            assert name in addnames

            series = add[addnames.index(name)]
            mask = [u == data[0][i] or u == data[1][i] for i in range(20)]

            assert (series == mask).all()


def test_expandCompound():

    data = []

    for i in range(20):
        rlen = np.random.randint(1, 20)
        row = np.random.randint(1, 100, rlen)
        data.append(row)

    exp = np.full((len(data), max(map(len, data))), np.nan)

    for i in range(len(data)):
        exp[i, :len(data[i])] = data[i]

    with tempdir():
        with open('data.txt', 'wt') as f:
            f.write('eid\t1-0.0\n')
            for i in range(len(data)):
                f.write(str(i + 1) + '\t' + ','.join(map(str, data[i])))
                f.write('\n')

        vartable, proctable, cattable = gen_tables([1])[:3]
        dt, _ = importing.importData('data.txt', vartable, proctable, cattable)

        dt[:, '1-0.0'] = dt[:, '1-0.0'].apply(
            lambda v: np.fromstring(v, sep=','))

        remove, add, addvids = pfns.expandCompound(dt, [1])

        assert [r.name for r in remove] == ['1-0.0']
        assert len(add) == max(map(len, data))
        assert len(addvids) == len(add)
        assert all([v == 1 for v in addvids])

        for col in range(exp.shape[1]):
            expcol = exp[:, col]
            gotcol = add[col].values

            expna = np.isnan(expcol)
            gotna = np.isnan(gotcol)

            assert np.all(        expna  ==         gotna)
            assert np.all(expcol[~expna] == gotcol[~gotna])
