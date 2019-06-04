#!/usr/bin/env python
#
# test_processing.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import itertools as it
import multiprocessing as mp
import textwrap as tw
from unittest import mock
from collections import defaultdict

import numpy  as np
import pandas as pd
import           pytest

import funpack.processing as processing
import funpack.importing  as importing
import funpack.loadtables as loadtables
import funpack.custom     as custom
import funpack.util       as util


from . import (clear_plugins,
               tempdir,
               gen_test_data,
               gen_DataTableFromDataFrame,
               gen_tables)


def  test_processData():           _test_processData(False)
def  test_processData_lowMemory(): _test_processData(True)
def _test_processData(lowMemory):

    custom.registerBuiltIns()

    sparse      = np.random.random(100)
    sparse[:50] = np.nan
    series1     = np.sin(np.linspace(0, np.pi * 6, 100))
    series2     = series1 + np.random.random(100)
    corr        = pd.Series(series1).corr(pd.Series(series2))

    vartable, proctable, cattable = gen_tables(range(1, 4))[:3]

    procs = [
        'removeIfSparse(60)',
        'removeIfRedundant({:0.2f})'.format(corr - 0.01)]

    procs  = [processing.parseProcesses(p, 'processor') for p in procs]
    procs  = [{p[0].name : p[0]} for p in procs]

    with tempdir(), mp.Pool(mp.cpu_count()) as pool:

        mgr = mp.Manager()

        df = pd.DataFrame({'1-0.0' : sparse,
                           '2-0.0' : series1,
                           '3-0.0' : series2},
                          index=np.arange(1, 101))
        df.index.name = 'eid'
        df.to_csv('data.txt')

        dtable, _ = importing.importData('data.txt',
                                         vartable,
                                         proctable,
                                         cattable,
                                         lowMemory=lowMemory,
                                         pool=pool,
                                         mgr=mgr)

        dtable.proctable['Variable'] = [('all_independent', []),
                                        ('all', [])]
        dtable.proctable['Process']  = procs
        processing.processData(dtable)
        assert [c.name for c in dtable.allColumns[1:]] == ['2-0.0']

        dtable, _ = importing.importData('data.txt',
                                         vartable,
                                         proctable,
                                         cattable,
                                         lowMemory=lowMemory,
                                         pool=pool,
                                         mgr=mgr)
        dtable.proctable['Variable'] = [('vids', [2, 3]),
                                        ('vids', [1, 2])]
        dtable.proctable['Process']  = procs
        processing.processData(dtable)
        assert [c.name for c in dtable.allColumns[1:]] == \
            ['1-0.0', '2-0.0', '3-0.0']
        df = None
        mgr = None
        pool = None
        dtable = None


def test_parseProcesses_parser():

    parser = processing.makeParser()

    with mock.patch('funpack.custom.exists', return_value=True):

        p = processing.parseProcesses('blah', 'none')
        assert len(p)   == 1
        p = p[0]
        assert p.name   == 'blah'
        assert p.args   == ()
        assert p.kwargs == {}
        print(p)

        p = processing.parseProcesses('blah()', 'none')
        assert len(p)   == 1
        p = p[0]
        assert p.name   == 'blah'
        assert p.args   == ()
        assert p.kwargs == {}

        p = processing.parseProcesses('blah(1, 2)', 'none')
        assert len(p)   == 1
        p = p[0]
        assert p.name   == 'blah'
        assert p.args   == (1, 2)
        assert p.kwargs == {}

        p = processing.parseProcesses('blah("a", \'b\', 3)', 'none')
        assert len(p)   == 1
        p = p[0]
        assert p.name   == 'blah'
        assert p.args   == ('a', 'b', 3)
        assert p.kwargs == {}

        p = processing.parseProcesses('blah(a=1, b=2, c=3)', 'none')
        assert len(p)   == 1
        p = p[0]
        assert p.name   == 'blah'
        assert p.args   == ()
        assert p.kwargs == {'a' : 1, 'b' : 2, 'c' : 3}

        p = processing.parseProcesses('blah("a", b=2, c=3)', 'none')
        assert len(p)   == 1
        p = p[0]
        assert p.name   == 'blah'
        assert p.args   == ('a',)
        assert p.kwargs == {'b' : 2, 'c' : 3}


@clear_plugins
def test_parseProcesses_run():

    called = {}

    @custom.processor('boo')
    def boo(a, b):
        assert a == 1 and b == 'hah'
        called['boo'] = True

    @custom.processor('foo')
    def foo(c, d):
        assert c == 'wah' and d == 4
        called['foo'] = True

    @custom.cleaner('moo')
    def moo(*a):
        called['moo'] = True

    @custom.cleaner('woo')
    def woo(x, y):
        assert x == 10 and y == 20
        called['woo'] = True

    @custom.processor('hoo')
    def hoo(truearg, falsearg, nonearg):
        assert truearg is True
        assert falsearg is False
        assert nonearg is None
        called['hoo'] = True

    procs  = processing.parseProcesses(
        'boo(1, \'hah\'), foo("wah", 4), hoo(True, False, None)',
        'processor')
    pprocs = processing.parseProcesses(
        'moo, moo(), woo(10, 20)',
        'cleaner')

    assert procs[0].name == 'boo'
    assert procs[0].args == (1, 'hah')
    assert procs[1].name == 'foo'
    assert procs[1].args == ('wah', 4)
    assert procs[2].name == 'hoo'
    assert procs[2].args == (True, False, None)

    procs[0].run()
    procs[1].run()
    procs[2].run()

    assert called['boo']
    assert called['foo']
    assert called['hoo']

    assert pprocs[0].name == 'moo'
    assert pprocs[1].name == 'moo'
    assert pprocs[2].name == 'woo'
    assert pprocs[0].args == ()
    assert pprocs[1].args == ()
    assert pprocs[2].args == (10, 20)

    pprocs[0].run()
    assert called['moo']
    called.clear()
    pprocs[1].run()
    assert called['moo']
    pprocs[2].run()
    assert called['woo']

    with pytest.raises(processing.NoSuchProcessError):
        processing.parseProcesses('gurh', 'processor')
    with pytest.raises(processing.NoSuchProcessError):
        processing.parseProcesses('boo', 'cleaner')
    with pytest.raises(processing.NoSuchProcessError):
        processing.parseProcesses('moo', 'processor')


@clear_plugins
def test_processData_variable_types():

    procfile = tw.dedent("""
    Variable\tProcess
    1:3\trun_vids
    all\trun_all
    all_independent\trun_all_independent
    all_except,1,2,3\trun_all_except
    all_independent_except,4,5,6\trun_all_independent_except
    """).strip()

    called_on = defaultdict(list)

    @custom.processor()
    def run_vids(dtable, vids):
        called_on['vids'].append(vids)

    @custom.processor()
    def run_all(dtable, vids):
        called_on['all'].append(vids)

    @custom.processor()
    def run_all_independent(dtable, vids):
        called_on['all_independent'].append(vids)

    @custom.processor()
    def run_all_except(dtable, vids):
        called_on['all_except'].append(vids)

    @custom.processor()
    def run_all_independent_except(dtable, vids):
        called_on['all_independent_except'].append(vids)

    with tempdir():
        open('processing.tsv', 'wt').write(procfile)
        gen_test_data(6, 50, 'data.tsv')

        proctable = loadtables.loadProcessingTable('processing.tsv')
        vartable, _, cattable = gen_tables(range(1, 7))[:3]
        dtable, _ = importing.importData('data.tsv',
                                         vartable,
                                         proctable,
                                         cattable)
        processing.processData(dtable)

        assert called_on['vids']                   == [[1, 2, 3]]
        assert called_on['all']                    == [[1, 2, 3, 4, 5, 6]]
        assert called_on['all_independent']        == [[1], [2], [3],
                                                       [4], [5], [6]]
        assert called_on['all_except']             == [[4, 5, 6]]
        assert called_on['all_independent_except'] == [[1], [2], [3]]


@clear_plugins
def test_processData_returnValues():

    @custom.processor()
    def nothing(dtable, vids):
        return None

    @custom.processor()
    def remove(dtable, vids):
        cols = list(it.chain(*[dtable.columns(v) for v in vids]))
        return cols

    @custom.processor()
    def add(dtable, vids):
        newseries = []
        newvids   = []
        for v in vids:
            col = dtable.columns(v)[0]
            data = dtable[:, col.name]
            newseries.append(pd.Series(data + 10,
                                       name='{}-0.0'.format(v * 10)))
            newvids.append(v * 10)
        return newseries, newvids

    @custom.processor()
    def add_and_remove(dtable, vids):
        remcols   = []
        newseries = []
        newvids   = []
        for v in vids:
            col = dtable.columns(v)[0]
            data = dtable[:, col.name]
            newseries.append(pd.Series(data + 10,
                                       name='{}-0.0'.format(v * 10)))
            newvids.append(v * 10)
            remcols.append(col)
        return remcols, newseries, newvids

    @custom.processor()
    def add_and_remove_meta(dtable, vids):
        remcols   = []
        newseries = []
        newvids   = []
        newmeta   = []
        for v in vids:
            col = dtable.columns(v)[0]
            data = dtable[:, col.name]
            newseries.append(pd.Series(data + 10,
                                       name='{}-0.0'.format(v * 10)))
            newvids.append(v * 10)
            remcols.append(col)
            newmeta.append(v * 10)
        return remcols, newseries, newvids, newmeta

    procfile = tw.dedent("""
    Variable\tProcess
    1:3\tremove
    4:6\tadd
    7:9\tadd_and_remove
    10:12\tnothing
    13:15\tadd_and_remove_meta
    """).strip()

    with tempdir():
        open('processing.tsv', 'wt').write(procfile)
        gen_test_data(15, 50, 'data.tsv')

        proctable = loadtables.loadProcessingTable('processing.tsv')
        vartable, _, cattable = gen_tables(range(1, 16))[:3]
        dtable, _ = importing.importData('data.tsv',
                                         vartable,
                                         proctable,
                                         cattable)

        processing.processData(dtable)

        gotcols = [c.name for c in dtable.allColumns[1:]]
        expcols = ['{}-0.0'.format(v)
                   for v in [4, 5, 6,
                             10, 11, 12,
                             40, 50, 60,
                             70, 80, 90,
                             130, 140, 150]]

        assert sorted(expcols) == sorted(gotcols)


@clear_plugins
def test_processData_metadata():

    @custom.metaproc()
    def modmeta(val):
        return val * 10

    @custom.processor()
    def process(dtable, vids):
        newseries = []
        newvids   = []
        newmeta   = []
        for v in vids:
            col = dtable.columns(v)[0]
            data = dtable[:, col.name]
            newseries.append(pd.Series(data + 10,
                                       name='{}-0.0'.format(v * 10)))
            newvids.append(v * 10)
            newmeta.append(v * 10)
        return [], newseries, newvids, newmeta

    procfile = tw.dedent("""
    Variable\tProcess
    1\tprocess
    2\tprocess(metaproc='modmeta')
    """).strip()

    with tempdir():
        open('processing.tsv', 'wt').write(procfile)
        gen_test_data(2, 50, 'data.tsv')

        proctable = loadtables.loadProcessingTable('processing.tsv')
        vartable, _, cattable = gen_tables([1, 2])[:3]
        dtable, _ = importing.importData('data.tsv',
                                         vartable,
                                         proctable,
                                         cattable)
        processing.processData(dtable)
        gotcols = [c.name for c in dtable.allColumns[1:]]
        expcols = ['{}-0.0'.format(v) for v in [1, 2, 10, 20]]

        assert sorted(expcols) == sorted(gotcols)

        col1, col2, col10, col20 = dtable.allColumns[1:]

        assert col1 .metadata is None
        assert col2 .metadata is None
        assert col10.metadata == 10
        assert col20.metadata == 200

def test_processData_existing_column():

    @custom.processor()
    def myproc(dtable, vids):
        remcols   = []
        newseries = []
        newvids   = []

        vid  = vids[0]
        col  = dtable.columns(vid)[0]
        data = dtable[:, col.name]

        # add a new column with the
        # same name as the existing
        # one, and remove the existing
        # one.
        newseries.append(pd.Series(data + 10, name=col.name))
        newvids.append(vid)
        remcols.append(col)

        return remcols, newseries, newvids

    data = np.random.randint(0, 10, 50)
    df    = pd.DataFrame({'eid'   : np.arange(1, 51),
                          '1-0.0' : data}).set_index('eid')
    dt    = gen_DataTableFromDataFrame(df)

    procs = processing.parseProcesses('myproc', 'processor')
    procs = {procs[0].name : procs[0]}

    dt.proctable.loc[1, ['Variable', 'Process']] = [('vids', [1]), procs]

    # make sure the variable metadata
    # is preserved for the new column
    dt.vartable.at[1, 'Type']        = util.CTYPES.categorical_single
    dt.vartable.at[1, 'Description'] = 'Super cool'

    processing.processData(dt)

    assert np.all(dt.vartable.index)       == [1]
    assert [c.name for c in dt.allColumns] == ['eid', '1-0.0']
    assert dt.vartable.at[1, 'Type'] == util.CTYPES.categorical_single
    assert dt.vartable.at[1, 'Description'] == 'Super cool'
