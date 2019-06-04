#!/usr/bin/env python
#
# test_loadtables.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import os.path as op
import textwrap
import itertools as it

import pandas as pd
import numpy  as np

import funpack.datatable as datatable
import funpack.loadtables as loadtables
import funpack.util as util
import funpack.custom as custom
import funpack.processing_functions as pfns

from . import tempdir, clear_plugins, patch_base_tables


def _prepare_variableTable(tdir, idxcol=0):

    datadata = [['eid',       '1',    '2',    '3'],
                ['1-0.0',    '10',   '20',   '30'],
                ['2-0.0',   '100',  '200',  '300'],
                ['5-0.0',   '500',  '600',  '700'],
                ['6-0.0',  '1000', '1100', '1200'],
                ['99-0.0',   '99',   '99',   '99']]
    datadata = [['eid',   '1-0.0',  '2-0.0',  '5-0.0',  '6-0.0',  '99-0.0'],
                [  '1',   '10',     '100',    '500',    '1000',   '99'],
                [  '2',   '20',     '200',    '600',    '1100',   '99'],
                [  '3',   '30',     '300',    '700',    '1200',   '99']]

    if idxcol != 0:
        for row in datadata:
            row.insert(idxcol, row.pop(0))

    datadata = '\n'.join(['\t'.join(row) for row in datadata])

    vardata = textwrap.dedent("""
    ID\tType\tDescription\tDataCoding\tNAValues\tRawLevels\tNewLevels\tParentValues\tChildValues\tClean
    1\tInteger\tvar 1\t100\t1,2,3\t10,20\t100,200\tv100 == 20\t123\tkeepVisits('last')
    2\tContinuous\tvar 2\t200\t\t\t\t\t\tremove, keepVisits('first')
    4\tInteger\tvar 4\t\t\t\t\t\t\t
    5\tDate\tvar 5\t\t\t\t\t\t\t
    6\tTime\tvar 6\t\t\t\t\t\t\t
    """).strip()

    dcdata = textwrap.dedent("""
    ID\tNAValues\tRawLevels\tNewLevels
    100\t100,200\t10, 11, 12\t20, 21, 22
    200\t500,600\t20, 21, 22\t30, 31, 32
    """).strip()

    typedata = textwrap.dedent("""
    Type\tClean
    Integer\tmakeNa('< 0')
    Continuous\tmakeNa('== 0')
    """).strip()

    fdata  = op.join(tdir, 'data.tsv')
    fvars  = op.join(tdir, 'vars.tsv')
    fdcs   = op.join(tdir, 'dcs.tsv')
    ftypes = op.join(tdir, 'typs.tsv')

    with open(fdata,  'wt') as f: f.write(datadata)
    with open(fvars,  'wt') as f: f.write(vardata)
    with open(fdcs,   'wt') as f: f.write(dcdata)
    with open(ftypes, 'wt') as f: f.write(typedata)

    return fdata, fvars, fdcs, ftypes


@clear_plugins
def test_loadTables():

    @custom.processor('dummy_proc1')
    def dummy_proc1():
        pass

    @custom.processor('dummy_proc2')
    def dummy_proc2():
        pass

    procdata = textwrap.dedent("""
    Variable\tProcess
    all\tdummy_proc1
    all_independent\tdummy_proc1
    1\tdummy_proc2
    1:5\tdummy_proc1, dummy_proc2
    1,2,3:5\tdummy_proc1
    """).strip()


    catdata = textwrap.dedent("""
    ID\tCategory\tVariables
    1\tcategory 1\t1, 2, 3, 4, 5
    2\tcategory 2\t6, 7, 8, 9, 10
    3\tcategory 3\t11:15, 16, 17, 18, 19, 20
    4\tcategory 4\t21:2:30
    """).strip()

    custom.registerBuiltIns()

    with tempdir() as td, patch_base_tables():

        with open('cattable.tsv', 'wt') as f:
            f.write(catdata)
        with open('proctable.tsv', 'wt') as f:
            f.write(procdata)

        fdata, fvars, fdcs, ftypes = _prepare_variableTable(td)
        vartable, proctable, cattable, unknowns, unprocessed = \
            loadtables.loadTables([fdata],
                                  [fvars],
                                  [fdcs],
                                  ftypes,
                                  'proctable.tsv',
                                  'cattable.tsv')

    assert len(unknowns)   == 1
    assert unknowns[0].vid == 99

    # Test a selection from each table
    expvids = [1, 2, 5, 6, 99]
    expdcs  = [100, 200, None, None, None]
    dcs     = [None if pd.isna(d) else d for d in vartable['DataCoding']]

    assert list(vartable.index) == expvids
    assert dcs                  == expdcs

    expproc4 = ([1, 2, 3, 4, 5],   ['dummy_proc1'])

    vids  = proctable['Variable'][4]
    procs = proctable['Process'][ 4]
    procs = [p.name for p in procs.values()]

    assert vids[0] == 'vids'
    assert vids[1] == expproc4[0]
    assert procs   == expproc4[1]

    assert      cattable['Category'] .iloc[2]  == 'category 3'
    assert list(cattable['Variables'].iloc[2]) == list(range(11, 21))


def test_loadVariableTable_standard():

    custom.registerBuiltIns()

    with tempdir() as td, patch_base_tables():
        fdata, fvars, fdcs, ftypes = _prepare_variableTable(td)
        vartable, unk, unp = loadtables.loadVariableTable(
            [fdata], [fvars], [fdcs], ftypes)

    expvids       = [1, 2, 5, 6, 99]
    exptypes      = [util.CTYPES.integer, util.CTYPES.continuous,
                     util.CTYPES.date, util.CTYPES.time, util.CTYPES.unknown]
    expdescs      = ['var 1', 'var 2', 'var 5', 'var 6', '99-0.0']
    expdcs        = [100, 200, None, None, None]
    expnavals     = [[1, 2, 3], [500, 600], [], [], []]
    exprawlevels  = [[10, 20], [20, 21, 22], [], [], []]
    expnewlevels  = [[100, 200], [30, 31, 32], [], [], []]
    expparentvals = [[100], [], [], [], []]
    expchildvals  = [[123], [], [], [], []]
    expcleans     = [['keepVisits', 'makeNa'],
                     ['remove', 'keepVisits', 'makeNa'], [], [], []]

    assert len(unk)   == 1
    assert unk[0].vid == 99
    assert list(vartable.index)          == expvids
    assert list(vartable['Description']) == expdescs

    types      = [t for t in vartable['Type']]
    dcs        = [None if pd.isna(d) else d for d in vartable['DataCoding']]
    navals     = [list(v) if isinstance(v, np.ndarray) else []
                  for v in vartable['NAValues']]
    rawlevels  = [list(v) if isinstance(v, np.ndarray) else []
                  for v in vartable['RawLevels']]
    newlevels  = [list(v) if isinstance(v, np.ndarray) else []
                  for v in vartable['NewLevels']]
    parentvals = [[]   if pd.isna(exps)
                  else list(it.chain(*[e.variables for e in exps]))
                  for exps in vartable['ParentValues']]
    childvals  = [list(v) if isinstance(v, np.ndarray)
                  else [] for v in vartable['ChildValues']]
    cleans     = [[]   if pd.isna(p) else list(p.keys())
                  for p in vartable['Clean']]

    assert types      == exptypes
    assert dcs        == expdcs
    assert navals     == expnavals
    assert rawlevels  == exprawlevels
    assert newlevels  == expnewlevels
    assert parentvals == expparentvals
    assert childvals  == expchildvals
    assert cleans     == expcleans


def test_loadVariableTable_indexes():


    custom.registerBuiltIns()

    with tempdir() as td:
        fdata, fvars, fdcs, ftypes = _prepare_variableTable(td, 2)
        vartable, unk, unp = loadtables.loadVariableTable(
            [fdata], [fvars], [fdcs], ftypes, indexes={fdata : 2})

        print()
        print(open(fdata).read())

    expvids  = [1, 2, 5, 6, 99]
    expdescs = ['var 1', 'var 2', 'var 5', 'var 6', '99-0.0']

    assert len(unk)   == 1
    assert unk[0].vid == 99
    assert list(vartable.index)          == expvids
    assert list(vartable['Description']) == expdescs


def test_loadVariableTable_clean():

    custom.registerBuiltIns()

    customClean       = {1 : 'fillMissing(10)'}
    customTypeClean   = {util.CTYPES.continuous : 'fillMissing(10)'}
    customGlobalClean = 'convertICD10Codes'

    with tempdir() as td:
        fdata, fvars, fdcs, ftypes = _prepare_variableTable(td)
        ppvt = loadtables.loadVariableTable(
            [fdata], [fvars], [fdcs], ftypes,
            clean=customClean)[0]
        tpvt = loadtables.loadVariableTable(
            [fdata], [fvars], [fdcs], ftypes,
            typeClean=customTypeClean)[0]
        pp_tpvt = loadtables.loadVariableTable(
            [fdata], [fvars], [fdcs], ftypes,
            clean=customClean,
            typeClean=customTypeClean)[0]
        pp_tp_gpvt = loadtables.loadVariableTable(
            [fdata], [fvars], [fdcs], ftypes,
            clean=customClean,
            typeClean=customTypeClean,
            globalClean=customGlobalClean)[0]

    pp_expcleans       = [['fillMissing'],
                          ['remove', 'keepVisits', 'makeNa'],
                          [], [], []]
    tp_expcleans       = [['keepVisits', 'makeNa'],
                           ['remove', 'keepVisits', 'fillMissing'],
                           [], [], []]
    pp_tp_expcleans    = [['fillMissing'],
                           ['remove', 'keepVisits', 'fillMissing'],
                           [], [], []]
    pp_tp_gp_expcleans = [['fillMissing', 'convertICD10Codes'],
                           ['remove', 'keepVisits', 'fillMissing',
                            'convertICD10Codes'],
                           ['convertICD10Codes'],
                           ['convertICD10Codes'],
                           ['convertICD10Codes']]
    pp_cleans          = [[] if pd.isna(p) else list(p.keys())
                           for p in ppvt['Clean']]
    tp_cleans          = [[] if pd.isna(p) else list(p.keys())
                           for p in tpvt['Clean']]
    pp_tp_cleans       = [[] if pd.isna(p) else list(p.keys())
                           for p in pp_tpvt['Clean']]
    pp_tp_gp_cleans    = [[] if pd.isna(p) else list(p.keys())
                           for p in pp_tp_gpvt['Clean']]

    assert pp_cleans       == pp_expcleans
    assert tp_cleans       == tp_expcleans
    assert pp_tp_cleans    == pp_tp_expcleans
    assert pp_tp_gp_cleans == pp_tp_gp_expcleans


@clear_plugins
def test_loadVariableTable_naValues():

    custom.registerBuiltIns()

    with tempdir() as td:
        fdata, fvars, fdcs, ftypes = _prepare_variableTable(td)

        vartable, _, _ = loadtables.loadVariableTable(
            [fdata], [fvars], [fdcs], ftypes,
            naValues={2   : [10, 20, 30],
                      99  : [10, 11, 12],
                      111 : [ 1,  2,  3]})

    expvids   = [1, 2, 5, 6, 99]
    expnavals = [[1, 2, 3], [10, 20, 30], [], [], [10, 11, 12]]

    navals    = [list(v) if isinstance(v, np.ndarray) else []
                 for v in vartable['NAValues']]

    assert list(vartable.index) == expvids
    assert navals               == expnavals


@clear_plugins
def test_loadVariableTable_recoding():

    custom.registerBuiltIns()

    with tempdir() as td:
        fdata, fvars, fdcs, ftypes = _prepare_variableTable(td)

        vartable, _, _ = loadtables.loadVariableTable(
            [fdata], [fvars], [fdcs], ftypes,
            recoding={2   : ([1, 2, 3],    [10, 20, 30]),
                      99  : ([40, 50],     [400, 500]),
                      111 : ([ 1,  2,  3], [100, 200, 300])})

    expvids      = [1, 2, 5, 6, 99]
    exprawlevels = [[10, 20],   [1, 2, 3],    [], [], [40, 50]]
    expnewlevels = [[100, 200], [10, 20, 30], [], [], [400, 500]]

    rawlevels = [list(v) if isinstance(v, np.ndarray) else []
                 for v in vartable['RawLevels']]
    newlevels = [list(v) if isinstance(v, np.ndarray) else []
                 for v in vartable['NewLevels']]

    assert list(vartable.index) == expvids
    assert rawlevels            == exprawlevels
    assert newlevels            == expnewlevels


@clear_plugins
def test_loadVariableTable_childValues():

    custom.registerBuiltIns()

    with tempdir() as td:
        fdata, fvars, fdcs, ftypes = _prepare_variableTable(td)

        childValues = {
            1   : ('v2 != 7', [12345]),
            99  : ('v5  < 7', [54321]),
            111 : ('v1 == 6', [55555])}

        vartable, _, _ = loadtables.loadVariableTable(
            [fdata], [fvars], [fdcs], ftypes,
            childValues=childValues)

    expvids       = [1, 2, 5, 6, 99]
    expparentvals = [[2],     [], [], [], [5]]
    expchildvals  = [[12345], [], [], [], [54321]]

    parentvals = [[]   if pd.isna(exps)
                  else list(it.chain(*[e.variables for e in exps]))
                  for exps in vartable['ParentValues']]
    childvals  = [list(v) if isinstance(v, np.ndarray)
                  else [] for v in vartable['ChildValues']]

    assert list(vartable.index) == expvids
    assert parentvals           == expparentvals
    assert childvals            == expchildvals


@clear_plugins
def test_loadProcessingTable():

    @custom.processor('dummy_proc1')
    def dummy_proc1():
        pass

    @custom.processor('dummy_proc2')
    def dummy_proc2():
        pass

    filedata = textwrap.dedent("""
    Variable\tProcess
    all\tdummy_proc1
    all_independent\tdummy_proc1
    1\tdummy_proc2
    1:5\tdummy_proc1, dummy_proc2
    1,2,3:5\tdummy_proc1
    all_except,1,3\tdummy_proc1
    all_independent_except,2,5\tdummy_proc2
    """).strip()

    exp = [
        ('all',                    [],                ['dummy_proc1']),
        ('all_independent',        [],                ['dummy_proc1']),
        ('vids',                   [1],               ['dummy_proc2']),
        ('vids',                   [1, 2, 3, 4, 5],   ['dummy_proc1',
                                                       'dummy_proc2']),
        ('vids',                   [1, 2, 3, 4, 5],   ['dummy_proc1']),
        ('all_except',             [1, 3],            ['dummy_proc1']),
        ('all_independent_except', [2, 5],            ['dummy_proc2']),
    ]

    prepend = [('100:105', 'dummy_proc1, dummy_proc2')]
    append  = [('100', 'dummy_proc1'), ('200', 'dummy_proc2')]

    preexp = [
        ('vids', [100, 101, 102, 103, 104, 105],
         ['dummy_proc1', 'dummy_proc2'])]
    appexp = [('vids', [100], ['dummy_proc1']),
              ('vids', [200], ['dummy_proc2'])]

    with tempdir():
        with open('proctable.tsv', 'wt') as f:
            f.write(filedata)

        pfns.dummy_proc1 = dummy_proc1
        pfns.dummy_proc2 = dummy_proc2

        pt_normal       = loadtables.loadProcessingTable(
            'proctable.tsv')
        pt_skip         = loadtables.loadProcessingTable(
            'proctable.tsv', skipProcessing=True)
        pt_pre          = loadtables.loadProcessingTable(
            'proctable.tsv', prependProcess=prepend)
        pt_app          = loadtables.loadProcessingTable(
            'proctable.tsv', appendProcess=append)
        pt_pre_app      = loadtables.loadProcessingTable(
            'proctable.tsv',
            prependProcess=prepend,
            appendProcess=append)
        pt_skip_pre_app = loadtables.loadProcessingTable(
            'proctable.tsv',
            prependProcess=prepend,
            appendProcess=append,
            skipProcessing=True)

    assert len(pt_normal)       == len(exp)
    assert len(pt_skip)         == 0
    assert len(pt_pre)          == len(exp) + len(prepend)
    assert len(pt_app)          == len(exp) + len(append)
    assert len(pt_pre_app)      == len(exp) + len(prepend) + len(append)
    assert len(pt_skip_pre_app) ==            len(prepend) + len(append)

    for table, offset in [(pt_normal,  0),
                          (pt_pre,     len(prepend)),
                          (pt_app,     0),
                          (pt_pre_app, len(prepend))]:

        for i in range(len(exp)):

            exppvtype, expvids, expprocs = exp[i]

            pvtype, vids = table['Variable'][i + offset]
            procs        = table['Process'][i + offset]
            procs        = [p.name for p in procs.values()]

            assert pvtype == exppvtype
            assert vids   == expvids
            assert procs  == expprocs

    for table in [pt_pre, pt_pre_app, pt_skip_pre_app]:
        for i in range(len(preexp)):
            exppvtype, expvids, expprocs = preexp[i]

            pvtype, vids = table['Variable'][i]
            procs        = table['Process'][i]
            procs        = [p.name for p in procs.values()]

            assert pvtype == exppvtype
            assert vids   == expvids
            assert procs  == expprocs

    for table, offset in [(pt_app, len(exp)),
                          (pt_pre_app, len(prepend) + len(exp)),
                          (pt_skip_pre_app, len(prepend))]:
        for i in range(len(appexp)):
            exppvtype, expvids, expprocs = appexp[i]

            pvtype, vids = table['Variable'][i + offset]
            procs        = table['Process'][i + offset]
            procs        = [p.name for p in procs.values()]

            assert pvtype == exppvtype
            assert vids   == expvids
            assert procs  == expprocs


def test_loadCategoryTable():

    filedata = textwrap.dedent("""
    ID\tCategory\tVariables
    1\tcategory 1\t1, 2, 3, 4, 5
    2\tcategory 2\t6, 7, 8, 9, 10
    3\tcategory 3\t11:15, 16, 17, 18, 19, 20
    4\tcategory 4\t21:2:30
    """).strip()

    with tempdir():
        with open('cattable1.tsv', 'wt') as f:
            f.write(filedata)

        with open('cattable2.tsv', 'wt') as f:
            f.write(filedata + '\n')
            f.write('5\tunknown\t100,101,102\n')

        unknowns = [datatable.Column('data.tsv', 'var1', 0, 103, 0, 0),
                    datatable.Column('data.tsv', 'var2', 1, 104, 0, 0),
                    datatable.Column('data.tsv', 'var3', 2, 105, 0, 0)]

        cattable1 = loadtables.loadCategoryTable('cattable1.tsv',
                                                 unknownVars=unknowns)
        cattable2 = loadtables.loadCategoryTable('cattable2.tsv',
                                                 unknownVars=unknowns)

    expnames = ['category 1',
                'category 2',
                'category 3',
                'category 4',
                'unknown']
    expvars = [range(1, 6),
               range(6, 11),
               range(11, 21),
               range(21, 30, 2),
               [103, 104, 105]]

    assert len(cattable1) == len(expvars)
    assert len(cattable2) == len(expvars)

    assert np.all(cattable1.index == [1, 2, 3, 4, loadtables.UNKNOWN_CATEGORY_ID])
    assert np.all(cattable2.index == [1, 2, 3, 4, 5])

    for i in range(len(expnames)):

        en =      expnames[i]
        ev = list(expvars[i])

        assert      cattable1['Category'] .iloc[i]  == en
        assert list(cattable1['Variables'].iloc[i]) == ev
        assert      cattable2['Category'] .iloc[i]  == en

        if en == 'unknown':
            assert list(cattable2['Variables'].iloc[i]) == [100, 101, 102] + ev


def test_categoryVariables():
    filedata = textwrap.dedent("""
    ID\tCategory\tVariables
    1\tage, sex\t1, 2, 3, 4, 5
    2\talcohol, tobacco\t6, 7, 8, 9, 10
    3\tmilk\t11:15, 16, 17, 18, 19, 20
    4\tcigars\t7, 8, 9
    """).strip()

    with tempdir():
        with open('cattable.tsv', 'wt') as f:
            f.write(filedata)

        cattable = loadtables.loadCategoryTable('cattable.tsv')

    tests = [
        (['age, sex'],          range(1, 6)),
        (['age', 'sex'],        range(1, 6)),
        (['alcohol'],           range(6, 11)),
        (['age', 'milk'],       it.chain(range(1, 6), range(11, 21))),
        (['milk', 'age'],       it.chain(range(11, 21), range(1, 6))),
        (['age', 1],            range(1, 6)),
        (['age', 3],            it.chain(range(1, 6), range(11, 21))),
        ([3, 'age'],            it.chain(range(11, 21), range(1, 6))),
        (['tobacco', 'cigars'], range(6, 11)),
        (['cigars', 'tobacco'], [7, 8, 9, 6, 10]),
    ]

    for cats, exp in tests:
        vids = loadtables.categoryVariables(cattable, cats)
        exp  = list(exp)
        assert exp == vids
