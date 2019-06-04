#!/usr/bin/env python
#
# test_main.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import textwrap  as tw
import itertools as it
import os.path   as op
import              os
import              shlex

from unittest import mock

import numpy as np
import pytest

import pandas as pd

import funpack.main       as main
import funpack.custom     as custom
import funpack.importing  as importing
import funpack.loadtables as loadtables
import funpack.expression as expression
import funpack.processing as processing

from . import (patch_logging,
               patch_base_tables,
               clear_plugins,
               tempdir,
               gen_tables,
               gen_DataTable,
               gen_test_data,
               gen_DataTableFromDataFrame)


@patch_logging
def test_main_help():
    for opt in ['-V', '-h', '--version', '--help']:
        try:
            main.main([opt])
        except SystemExit as e:
            assert e.code == 0


@patch_logging
def test_main_minimal():
    with tempdir():
        gen_test_data(10, 100, 'data.tsv')
        main.main('-nb out.tsv data.tsv'.split())

        out  = pd.read_csv('out.tsv',  delimiter='\t')
        data = pd.read_csv('data.tsv', delimiter='\t')

        assert np.all(out.columns == data.columns)
        assert np.all(out.values  == data.values)


@patch_logging
def test_main_minimal_lowMemory():
    with tempdir():
        gen_test_data(10, 100, 'data.tsv')
        main.main('-nb -lm out.tsv data.tsv'.split())

        out  = pd.read_csv('out.tsv',  delimiter='\t')
        data = pd.read_csv('data.tsv', delimiter='\t')

        assert np.all(out.columns == data.columns)
        assert np.all(out.values  == data.values)


@patch_logging
def test_main_overwrite():
    with tempdir():
        gen_test_data(10, 100, 'data.tsv')

        with open('out.tsv', 'wt') as f:
            f.write('abc')

        with pytest.raises(SystemExit):
            main.main('-nb out.tsv data.tsv'.split())

        with open('out.tsv', 'rt') as f:
            assert f.read() == 'abc'

        main.main('-nb -ow out.tsv data.tsv'.split())

        out  = pd.read_csv('out.tsv',  delimiter='\t')
        data = pd.read_csv('data.tsv', delimiter='\t')

        assert np.all(out.columns == data.columns)
        assert np.all(out.values  == data.values)


@clear_plugins
@patch_logging
def test_main_pluginfile():

    plugin = tw.dedent("""
    import funpack.custom as custom

    @custom.cleaner()
    def replace_with_nines(dtable, vid):
        for col in dtable.columns(vid):
            dtable[:, col.name] = [9] * len(dtable)
    """).strip()

    with tempdir():
        gen_test_data(10, 100, 'data.tsv')

        with open('plugin.py', 'wt') as f:
            f.write(plugin)

        main.main(
            '-nb -p plugin.py -sp -gc replace_with_nines out.tsv data.tsv'.split())

        out = pd.read_csv('out.tsv', delimiter='\t')

        exp         = np.zeros((11, 100))
        exp[0,  :]  = range(1, 101)
        exp[1:, :] = 9

        assert np.all(out.values == exp.T)


@patch_logging
def test_main_passthrough():
    with tempdir():
        gen_test_data(10, 100, 'data.tsv')

        main.main('-sn -scv -scf -sr -sp out1.tsv data.tsv'.split())
        main.main('-pt                   out2.tsv data.tsv'.split())

        data = pd.read_csv('data.tsv', delimiter='\t', index_col=0)
        out1 = pd.read_csv('out1.tsv', delimiter='\t', index_col=0)
        out2 = pd.read_csv('out2.tsv', delimiter='\t', index_col=0)

        assert (out1.columns == data.columns).all()
        assert np.all((out1 == data))
        assert (out2.columns == data.columns).all()
        assert np.all((out2 == data))


@patch_logging
def test_main_configfile():

    cfg = tw.dedent("""
    overwrite
    no_builtins
    """).strip()

    with tempdir():
        gen_test_data(10, 100, 'data.tsv')

        with open('out.tsv', 'wt') as f:
            f.write('abc')

        with open('config.txt', 'wt') as f:
            f.write(cfg)

        main.main('-cfg config.txt out.tsv data.tsv'.split())

        out  = pd.read_csv('out.tsv',  delimiter='\t')
        data = pd.read_csv('data.tsv', delimiter='\t')

        assert np.all(out.columns == data.columns)
        assert np.all(out.values  == data.values)


@clear_plugins
@patch_logging
def test_main_loader():
    plugin = tw.dedent("""
    import funpack
    import pandas as pd

    @funpack.sniffer('silly_loader')
    def silly_sniffer(infile):
        return [
            funpack.Column(infile, 'eid',   0, 0,     0, 0),
            funpack.Column(infile, '1-0.0', 0, 12345, 0, 0)]

    @funpack.loader()
    def silly_loader(infile):
        df = pd.DataFrame()
        df['eid']   = list(range(1, 101))
        df['1-0.0'] = list(reversed(range(100)))
        return df.set_index('eid')
    """).strip()

    with tempdir():

        with open('in.tsv', 'wt') as f:
            f.write(' ')

        with open('plugin.py', 'wt') as f:
            f.write(plugin)

        main.main(
            '-p plugin.py -l in.tsv silly_loader out.tsv in.tsv'.split())

        out = pd.read_csv('out.tsv', delimiter='\t')

        exp         = np.zeros((2, 100))
        exp[0, :] = list(range(1, 101))
        exp[1, :] = list(reversed(range(100)))

        assert np.all(out.values == exp.T)


@patch_logging
def test_main_variables():
    with tempdir():
        gen_test_data(10, 100, 'data.tsv')

        with open('varfile.txt', 'wt') as f:
            f.write('2\n')
            f.write('3\n')

        # Single ID and range
        main.main('-nb -v varfile.txt -v 4 -v 5 -v 6:7 out.tsv data.tsv'.split())

        data = pd.read_csv('data.tsv', delimiter='\t').set_index('eid')
        out  = pd.read_csv('out.tsv',  delimiter='\t').set_index('eid')

        expcols = ['{}-0.0'.format(i) for i in [2, 3, 4, 5, 6, 7]]

        assert (out.columns == expcols).all()
        assert np.all(out.loc[:, :] == data.loc[:, expcols])

        # Single ID and range and list
        main.main('-nb -ow -v varfile.txt -v 8:10 -v 4,5,7 -v 1 '
                  'out.tsv data.tsv'.split())

        data = pd.read_csv('data.tsv', delimiter='\t').set_index('eid')
        out  = pd.read_csv('out.tsv',  delimiter='\t').set_index('eid')

        expcols = ['{}-0.0'.format(i) for i in [2, 3, 8, 9, 10, 4, 5, 7, 1]]

        assert (out.columns == expcols).all()
        assert np.all(out.loc[:, :] == data.loc[:, expcols])

        # Make sure duplicate variables are ignored
        with open('varfile.txt', 'wt') as f:
            f.write('2\n')
            f.write('2\n')
            f.write('3\n')
            f.write('3\n')
            f.write('3\n')
            f.write('4\n')

        main.main('-nb -ow -v varfile.txt -v 3 -v 4 -v 5 -v 5 -v 6:7 '
                  'out.tsv data.tsv'.split())

        data = pd.read_csv('data.tsv', delimiter='\t').set_index('eid')
        out  = pd.read_csv('out.tsv',  delimiter='\t').set_index('eid')

        expcols = ['{}-0.0'.format(i) for i in [2, 3, 4, 5, 6, 7]]

        assert (out.columns == expcols).all()
        assert np.all(out.loc[:, :] == data.loc[:, expcols])


@clear_plugins
@patch_logging
def test_main_formatters():

    def _datefmt(d):
        return d.strftime('%d-%m-%Y')
    def _timefmt(t):
        return t.strftime('%d-%m-%Y %S %M %H')

    plugin = tw.dedent("""
    from funpack import custom

    def _datefmt(d):
        return d.strftime('%d-%m-%Y')
    def _timefmt(t):
        return t.strftime('%d-%m-%Y %S %M %H')

    @custom.formatter('test_date_format')
    def datefmt(dtable, column, series):
        return series.apply(_datefmt)

    @custom.formatter('test_time_format')
    def timefmt(dtable, column, series):
        return series.apply(_timefmt)

    @custom.formatter('test_var_format')
    def varfmt(dtable, column, series):
        def fmt(v):
            return str(v + 10)
        return series.apply(fmt)
    """).strip()

    with tempdir():

        # Using specific VIDs that
        # are date/time types in the
        # built-in variable table
        datecol = '53-0.0'
        timecol = '4289-0.0'
        varcol1 = '48-0.0'
        varcol2 = '49-0.0'
        datevar = 53
        timevar = 4289
        varvar1 = 48
        varvar2 = 49
        names = [datecol, timecol, varcol1, varcol2]

        with open('plugin.py', 'wt') as f:
            f.write(plugin)

        gen_test_data(4, 100, 'data.tsv', ctypes={1 : 'date', 2 : 'datetime'},
                      names=names)

        data = pd.read_csv('data.tsv',
                           delimiter='\t',
                           parse_dates=[datecol, timecol],
                           infer_datetime_format=True,
                           index_col=0)

        main.main('-n -n '
                  '-p plugin.py '
                  '-edf test_date_format '
                  '-etf test_time_format '
                  '-tvf {} test_var_format '
                  '-tvf {} test_var_format '
                  'out.tsv data.tsv'.format(varvar1, varcol2).split())

        got  = pd.read_csv('out.tsv', delimiter='\t')
        gotd =          got[ datecol]
        gott =          got[ timecol]
        got1 =          got[ varcol1]
        got2 =          got[ varcol2]
        expd =          data[datecol].apply(_datefmt)
        expt =          data[timecol].apply(_timefmt)
        exp1 = np.array(data[varcol1] + 10)
        exp2 = np.array(data[varcol2] + 10)

        assert np.all(np.array(gotd) == expd)
        assert np.all(np.array(gott) == expt)
        assert np.all(np.array(got1) == exp1)
        assert np.all(np.array(got2) == exp2)


@patch_logging
@clear_plugins
def test_main_loader():

    plugin = tw.dedent("""
    import pandas as pd
    import numpy  as np

    from funpack import datatable
    from funpack import custom

    @custom.sniffer('test_loader')
    def sniffer(infile):
        cols = [
            datatable.Column(infile, 'eid',   0, 0, 0, 0),
            datatable.Column(infile, '1-0.0', 1, 1, 0, 0)]
        return cols

    @custom.loader('test_loader')
    def loader(infile):
        df            = pd.DataFrame()
        df['eid']   = np.arange(10, 110)
        df['1-0.0'] = [12345] * 100
        return df.set_index('eid')
    """).strip()


    with tempdir():

        with open('plugin.py', 'wt') as f:
            f.write(plugin)

        with open('data.tsv', 'wt') as f:
            f.write(' ')
        main.main('-p plugin.py '
                  '-l data.tsv test_loader out.tsv data.tsv'.split())

        got = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        assert np.all(got.index      == np.arange(10, 110))
        assert np.all(got['1-0.0'] == 12345)


@patch_logging
@clear_plugins
def test_main_visits():

    custom.registerBuiltIns()

    plugin = tw.dedent("""
    from funpack import custom

    @custom.cleaner('test_clean')
    def clean(dtable, vid):
        dtable[:, dtable.columns(vid)[0].name] *= 2
    """).strip()

    with tempdir():

        with open('plugin.py', 'wt') as f:
            f.write(plugin)

        gen_test_data(10, 100, 'data.tsv', min_visits=2, max_visits=3)

        tables = loadtables.loadTables(['data.tsv'])[:3]
        dt, _  = importing.importData(['data.tsv'], *tables)

        base = '-p plugin.py -ow -nb '

        main.main((base + '-vi first out.tsv data.tsv').split())
        gotfirst = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        main.main((base + '-vi last out.tsv data.tsv').split())
        gotlast = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        main.main((base + '-vi 1 out.tsv data.tsv').split())
        gotone = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        main.main((base + '-vi 1 -gc test_clean out.tsv data.tsv').split())
        gotonecleaned = pd.read_csv('out.tsv', delimiter='\t', index_col=0)

        for vid in dt.variables:
            if vid == 0:
                continue
            firstcol = dt.columns(vid)[ 0].name
            lastcol  = dt.columns(vid)[-1].name
            onecol   = dt.columns(vid)[ 1].name

            assert np.all(dt[:, firstcol]   == gotfirst[     firstcol])
            assert np.all(dt[:, lastcol]    == gotlast[      lastcol])
            assert np.all(dt[:, onecol]     == gotone[       onecol])
            assert np.all(dt[:, onecol] * 2 == gotonecleaned[onecol])


@patch_logging
def test_main_subjects():

    custom.registerBuiltIns()

    with tempdir():
        gen_test_data(10, 20, 'data.tsv')
        tables = loadtables.loadTables(['data.tsv'])[:3]
        dt, _  = importing.importData(['data.tsv'], *tables)

        args = ' -ow -sp out.tsv data.tsv'

        mask = np.zeros(20, dtype=np.bool)

        with open('subjects.txt', 'wt') as f:
            f.write('\n'.join(map(str, [1, 2, 3])))
        main.main(shlex.split('-s subjects.txt ' + args))
        mask[:]  = 0
        mask[:3] = 1
        got  = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        exp  = dt[mask, :]
        assert np.all(got == exp)

        main.main(shlex.split('-s 3 -s 4 -s 5:10 ' + args))
        mask[:]    = 0
        mask[2:10] = 1
        got  = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        exp  = dt[mask, :]
        assert np.all(got == exp)

        main.main(shlex.split('-s subjects.txt -s 3 -s 4 -s 5:10 ' + args))
        mask[:]   = 0
        mask[:10] = 1
        got  = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        exp  = dt[mask, :]
        assert np.all(got == exp)

        main.main(shlex.split('-ex 1:10 ' + args))
        mask[:]   = 0
        mask[10:] = 1
        got  = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        exp  = dt[mask, :]
        assert np.all(got == exp)

        # exclude overrides include
        main.main(shlex.split('-s subjects.txt -ex 3:10 ' + args))
        mask[:]   = 0
        mask[:2]  = 1
        got  = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        exp  = dt[mask, :]
        assert np.all(got == exp)

        main.main(shlex.split('-s subjects.txt -s 4:10 -ex 8:20 ' + args))
        mask[:]  = 0
        mask[:7] = 1
        got  = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        exp  = dt[mask, :]
        assert np.all(got == exp)


@patch_logging
def test_main_subject_expression():
    custom.registerBuiltIns()

    with tempdir():
        data = np.random.randint(1, 10, (30, 6))
        data[:, 0] = np.arange(1, 31)
        cols = ['eid'] + ['{}-0.0'.format(i) for i in range(1, 6)]

        np.savetxt('data.tsv', data, delimiter='\t', header='\t'.join(cols))

        tables = loadtables.loadTables(['data.tsv'])[:3]
        dt, _  = importing.importData(['data.tsv'], *tables)

        mask = np.zeros(30, dtype=np.bool)

        args = ' -ow -sp out.tsv data.tsv '

        main.main(shlex.split('-s "v1 > 4 || v2 < 7" ' + args))
        mask[(data[:, 1] > 4) | (data[:, 2] < 7)] = 1
        got  = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        exp  = dt[mask, :]
        assert np.all(got == exp)


@patch_logging
def test_main_subjects_and_expression():

    custom.registerBuiltIns()

    with tempdir():
        data = np.random.randint(1, 10, (100, 6))
        data[:, 0] = np.arange(1, 101)
        data[ :20:2, 1] = 6
        data[1:20:2, 1] = 2
        cols = ['eid'] + ['{}-0.0'.format(i) for i in range(1, 6)]

        np.savetxt('data.tsv', data, delimiter='\t', header='\t'.join(cols))

        tables = loadtables.loadTables(['data.tsv'])[:3]
        dt, _  = importing.importData(['data.tsv'], *tables)

        with open('subjects.txt', 'wt') as f:
            f.write('\n'.join(map(str, [1, 2, 3])))

        main.main(shlex.split('-ow '
                              '-s subjects.txt '
                              '-s 3 '
                              '-s 3 '
                              '-s 4 '
                              '-s 4 '
                              '-s 5:10 '
                              '-s "v1 > 4" '
                              '-ex 8:20 '
                              '-sp '
                              'out.tsv data.tsv'))

        mask = np.zeros(100, dtype=np.bool)
        mask[:8:2] = 1

        got  = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        exp  = dt[mask, :]

        assert np.all(got == exp)



@patch_logging
def test_main_categories():
    with tempdir():

        with open('variables.tsv', 'wt') as f:
            f.write('ID\tType\tDescription\tDataCoding\tNAValues\tRawLevels\tNewLevels\tParentValues\tChildValues\tClean\n')
            f.write( '1\tContinuous\t\t\t\t\t\t\t\t\n')
            f.write( '3\tContinuous\t\t\t\t\t\t\t\t\n')
            f.write( '5\tContinuous\t\t\t\t\t\t\t\t\n')
            f.write( '7\tContinuous\t\t\t\t\t\t\t\t\n')
            f.write( '9\tContinuous\t\t\t\t\t\t\t\t\n')
            f.write('11\tContinuous\t\t\t\t\t\t\t\t\n')
            f.write('13\tContinuous\t\t\t\t\t\t\t\t\n')
            f.write('15\tContinuous\t\t\t\t\t\t\t\t\n')
            f.write('17\tContinuous\t\t\t\t\t\t\t\t\n')
            f.write('19\tContinuous\t\t\t\t\t\t\t\t\n')

        with open('categories.tsv', 'wt') as f:
            f.write('ID\tCategory\tVariables\n')
            f.write('1\tcat1\t1:5\n')
            f.write('2\tcat2\t6:10\n')
            f.write('3\tcat3\t11:15\n')

        cat1 = ['{}-0.0'.format(i) for i in range(1,  6)]
        cat2 = ['{}-0.0'.format(i) for i in range(6,  11)]
        unkn = ['{}-0.0'.format(i) for i in range(2, 21, 2)]
        cat3 = ['{}-0.0'.format(i) for i in range(11, 16)]

        gen_test_data(20, 100, 'data.tsv')

        data = pd.read_csv('data.tsv', delimiter='\t', index_col=0)

        pref = '-ow -nb -cf categories.tsv -vf variables.tsv '
        suf  = ' out.tsv data.tsv'

        main.main((pref + '-c cat1' + suf).split())
        out = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        assert np.all(out.loc[:, :] == data.loc[:, cat1])

        main.main((pref + '-c 1' + suf).split())
        out = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        assert np.all(out.loc[:, :] == data.loc[:, cat1])

        main.main((pref + '-c cat2' + suf).split())
        out = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        assert np.all(out.loc[:, :] == data.loc[:, cat2])

        main.main((pref + '-c 1 -c cat2' + suf).split())
        out = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        assert np.all(out.loc[:, :] == data.loc[:, cat1 + cat2])

        main.main((pref + '-c unknown' + suf).split())
        out = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        assert np.all(out.loc[:, :] == data.loc[:, unkn])

        main.main((pref + '-c -1' + suf).split())
        out = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        assert np.all(out.loc[:, :] == data.loc[:, unkn])

        main.main((pref + '-c -1 -c cat3' + suf).split())
        out = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        expcols = unkn + [c for c in cat3 if c not in unkn]
        assert np.all(out.loc[:, :] == data.loc[:, expcols])


@patch_logging
def test_main_column_names():
    with tempdir():
        gen_test_data(10, 100, 'data.tsv')

        main.main(shlex.split('-nb -oi subby -cp "{variable}-woo" out.tsv data.tsv'))
        got = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        exp = ['{}-woo'.format(i) for i in range(1, 11)]
        assert np.all(got.columns == exp)
        assert got.index.name == 'subby'

        main.main(shlex.split(
            '-nb -ow -rc 1-0.0 woopy -cp "{name}" out.tsv data.tsv'))
        got = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        exp = ['{}-0.0'.format(i) for i in range(1, 11)]
        exp[0] = 'woopy'
        assert np.all(got.columns == exp)

        # non-standard input column names
        names = ['{}-0.0'.format(i) for i in range(1, 10)] + ['woopy']
        gen_test_data(10, 100, 'data.tsv', names=names)
        main.main(shlex.split('-nb -ow out.tsv data.tsv'))
        got = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        assert sorted(got.columns) == sorted(names)

        gen_test_data(10, 100, 'data.tsv', names=names)
        main.main(shlex.split('-nb -ow -cp "{name}-{visit}" out.tsv data.tsv'))
        exp = ['{}-0.0-0'.format(i) for i in range(1, 10)] + ['woopy-0']
        got = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        assert sorted(got.columns) == sorted(exp)


@patch_logging
@clear_plugins
def test_main_clean():

    plugin = tw.dedent("""
    from funpack import custom

    @custom.cleaner('test_clean1')
    def clean1(dtable, vid):
        dtable[:, dtable.columns(vid)[0].name] *= 2
    @custom.cleaner('test_clean2')
    def clean2(dtable, vid):
        dtable[:, dtable.columns(vid)[0].name] *= 3
    @custom.cleaner('test_clean3')
    def clean3(dtable, vid):
        dtable[:, dtable.columns(vid)[0].name] *= 4
    @custom.cleaner('test_clean4')
    def clean4(dtable, vid):
        dtable[:, dtable.columns(vid)[0].name] *= 5
    @custom.cleaner('test_clean_int')
    def clean_int(dtable, vid):
        dtable[:, dtable.columns(vid)[0].name] *= 6
    """).strip()

    with tempdir():

        with open('plugin.py', 'wt') as f:
            f.write(plugin)

        with open('variables.tsv', 'wt') as f:
            f.write('ID\tType\tDescription\tDataCoding\tNAValues\tRawLevels\tNewLevels\tParentValues\tChildValues\tClean\n')
            f.write( '4\tInteger\t\t\t\t\t\t\t\t\n')

        gen_test_data(10, 100, 'data.tsv')
        main.main('-nb -p plugin.py '
                  '-vf variables.tsv '
                  '-cl 1 test_clean1 '
                  '-cl 2 test_clean2 '
                  '-cl 3 test_clean3 '
                  '-tc integer test_clean_int '
                  'out.tsv data.tsv'.split())

        data = pd.read_csv('data.tsv', delimiter='\t', index_col=0)
        got  = pd.read_csv('out.tsv',  delimiter='\t', index_col=0)

        assert np.all(( 2 * data['1-0.0']) == got['1-0.0'])
        assert np.all(( 3 * data['2-0.0']) == got['2-0.0'])
        assert np.all(( 4 * data['3-0.0']) == got['3-0.0'])
        assert np.all(( 6 * data['4-0.0']) == got['4-0.0'])

        main.main('-nb -ow '
                  '-cl 4 test_clean4 '
                  '-gc test_clean1 '
                  'out.tsv data.tsv'.split())

        got  = pd.read_csv('out.tsv',  delimiter='\t', index_col=0)
        assert np.all(( 2 * data['1-0.0']) == got['1-0.0'])
        assert np.all(( 2 * data['2-0.0']) == got['2-0.0'])
        assert np.all(( 2 * data['3-0.0']) == got['3-0.0'])
        assert np.all((10 * data['4-0.0']) == got['4-0.0'])

        main.main('-nb -ow -vf variables.tsv '
                  '-gc test_clean4 '
                  'out.tsv data.tsv'.split())
        data = pd.read_csv('data.tsv', delimiter='\t', index_col=0)
        got  = pd.read_csv('out.tsv',  delimiter='\t', index_col=0)
        assert np.all(( 5 * data.loc[:, :]) == got.loc[:, :])


        # Override clean on command line
        with open('variables.tsv', 'wt') as f:
            f.write('ID\tType\tDescription\tDataCoding\tNAValues\tRawLevels\tNewLevels\tParentValues\tChildValues\tClean\n')
            f.write( '4\tInteger\t\t\t\t\t\t\t\ttest_clean4\n')
        main.main('-nb -ow -vf variables.tsv '
                  '-cl 4 test_clean3 '
                  'out.tsv data.tsv'.split())
        data = pd.read_csv('data.tsv', delimiter='\t', index_col=0)
        got  = pd.read_csv('out.tsv',  delimiter='\t', index_col=0)
        assert np.all(( 4 * data.loc[:, '4-0.0']) == got.loc[:, '4-0.0'])

        main.main(shlex.split('-nb -ow -vf variables.tsv '
                              '-cl 4 \'\' '
                              'out.tsv data.tsv'))
        data = pd.read_csv('data.tsv', delimiter='\t', index_col=0)
        got  = pd.read_csv('out.tsv',  delimiter='\t', index_col=0)
        assert np.all((data.loc[:, :]) == got.loc[:, :])


@patch_logging
def test_main_badargs():

    with tempdir():

        gen_test_data(10, 10, 'data.tsv')

        with pytest.raises(ValueError):
            main.main('-f non-existent-format '
                      'out.tsv data.tsv'.split())

        with pytest.raises(ValueError):
            main.main('-l data.tsv non_existent_loader '
                      'out.tsv data.tsv'.split())

        with pytest.raises(ValueError):
            main.main('-edf non_existent_format '
                      'out.tsv data.tsv'.split())

        with pytest.raises(ValueError):
            main.main('-etf non_existent_format '
                      'out.tsv data.tsv'.split())

        with pytest.raises(ValueError):
            main.main('-tvf 1 non_existent_format '
                      'out.tsv data.tsv'.split())


@patch_logging
def test_main_subject_ordering():

    with tempdir():
        gen_test_data(10, 100, 'data.tsv')

        # skip processing, otherwise sparsity check will fail
        # main.main('-s 5:-1:1 -sp out.tsv data.tsv'.split())
        # data = pd.read_csv('data.tsv', delimiter='\t', index_col=0)
        # got  = pd.read_csv('out.tsv',  delimiter='\t', index_col=0)

        # assert np.all(got == data.loc[[5, 4, 3, 2, 1], :])

        # order should still be applied if subject
        # inclusion expressions are specified
        main.main(shlex.split('-s 10:-1:1 -s "v1 > 50" -sp -ow out.tsv data.tsv'))
        data = pd.read_csv('data.tsv', delimiter='\t', index_col=0)
        got  = pd.read_csv('out.tsv',  delimiter='\t', index_col=0)

        exp = list(reversed(1 + np.where(data.loc[:10, '1-0.0'] > 50)[0]))
        print(exp)
        print(got.index)
        assert np.all(got.index == exp)


@patch_logging
def test_main_variable_ordering():

    with tempdir():

        gen_test_data(20, 100, 'data.tsv')
        data = pd.read_csv('data.tsv', delimiter='\t', index_col=0)

        with open('variables.tsv', 'wt') as f:
            f.write('ID\tType\tDescription\tDataCoding\tNAValues\tRawLevels\tNewLevels\tParentValues\tChildValues\tClean\n')
            f.write( '1\tContinuous\t\t\t\t\t\t\t\t\n')
            f.write( '3\tContinuous\t\t\t\t\t\t\t\t\n')
            f.write( '5\tContinuous\t\t\t\t\t\t\t\t\n')
            f.write( '7\tContinuous\t\t\t\t\t\t\t\t\n')
            f.write( '9\tContinuous\t\t\t\t\t\t\t\t\n')
            f.write('11\tContinuous\t\t\t\t\t\t\t\t\n')
            f.write('13\tContinuous\t\t\t\t\t\t\t\t\n')
            f.write('15\tContinuous\t\t\t\t\t\t\t\t\n')
            f.write('17\tContinuous\t\t\t\t\t\t\t\t\n')
            f.write('19\tContinuous\t\t\t\t\t\t\t\t\n')

        with open('categories.tsv', 'wt') as f:
            f.write('ID\tCategory\tVariables\n')
            f.write('1\tcat1\t1:5\n')
            f.write('2\tcat2\t6:10\n')
            f.write('3\tcat3\t11:15\n')
            f.write('4\tcat4\t16:20\n')

        allvars = ['{}-0.0'.format(v) for v in range(1,  21)]
        cat1    = ['{}-0.0'.format(v) for v in range(1,  6)]
        cat2    = ['{}-0.0'.format(v) for v in range(6,  11)]
        cat3    = ['{}-0.0'.format(v) for v in range(11, 16)]
        cat4    = ['{}-0.0'.format(v) for v in range(16, 21)]
        catunkn = ['{}-0.0'.format(v) for v in range(2,  21, 2)]

        argbase = ' -q -nb -vf variables.tsv -cf categories.tsv  -ow out.tsv data.tsv'

        main.main(('-v 1 -v 2 -v 3' + argbase).split())
        got = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        exp = data.loc[:, allvars[:3]]
        assert np.all(got == exp)

        main.main(('-v 3 -v 2 -v 1' + argbase).split())
        got = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        exp = data.loc[:, allvars[2::-1]]
        assert np.all(got == exp)

        main.main(('-c cat1 -c cat3' + argbase).split())
        got = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        exp = data.loc[:, cat1 + cat3]
        assert np.all(got == exp)

        main.main(('-c cat3 -c cat1' + argbase).split())
        got = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        exp = data.loc[:, cat3 + cat1]
        assert np.all(got == exp)

        main.main(('-v 17 -c cat3 -v 3' + argbase).split())
        got = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        exp = data.loc[:, [allvars[16]] + [allvars[2]] + cat3]
        assert np.all(got == exp)


@patch_logging
def test_main_subject_and_variable_ordering():

    with tempdir():
        gen_test_data(10, 100, 'data.tsv')

        # skip procesing, otherwise sparsity check will fail
        main.main('-s 5:-1:1 -v 5:-2:1 -sp out.tsv data.tsv'.split())
        data = pd.read_csv('data.tsv', delimiter='\t', index_col=0)
        got  = pd.read_csv('out.tsv',  delimiter='\t', index_col=0)
        exp  = data.loc[[5, 4, 3, 2, 1], ['5-0.0', '3-0.0', '1-0.0']]

        assert np.all(got == exp)



@patch_logging
def test_main_serial_parallel_lowMemory():

    with tempdir(), mock.patch('funpack.storage.COLUMNS_PER_FILE', 5):
        gen_test_data(50, 250, 'data.tsv')

        with open('variables.tsv', 'wt') as f:
            f.write('ID\tType\tDescription\tDataCoding\tNAValues\tRawLevels\tNewLevels\tParentValues\tChildValues\tClean\n')

        data = pd.read_csv('data.tsv', delimiter='\t', index_col=0)
        base = ' -lm -ow -nb -vf variables.tsv out.tsv data.tsv'

        main.main(('-nj 0' + base).split())
        custom.clearRegistry()
        out0 = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        main.main(('-nj 1' + base).split())
        custom.clearRegistry()
        out1 = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        main.main(('-nj 2' + base).split())
        custom.clearRegistry()
        out2 = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        main.main(('-nj 4' + base).split())
        custom.clearRegistry()
        out4 = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        main.main(('-nj 8' + base).split())
        custom.clearRegistry()
        out8 = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        main.main(('-nj 16' + base).split())
        custom.clearRegistry()
        out16 = pd.read_csv('out.tsv', delimiter='\t', index_col=0)

        for got in [out0, out1, out2, out4, out8, out16]:
            assert np.all(np.isclose(got, data))


@patch_logging
def test_main_icd10():
    with tempdir():
        codings = tw.dedent("""
        coding\tmeaning\tnode_id\tparent_id
        a10\ta desc\t5\t0
        b20\tb desc\t1\t5
        c30\tc desc\t3\t5
        d40\td desc\t4\t3
        e50\te desc\t2\t1
        """).strip()

        data = tw.dedent("""
        eid,1-0.0
        1,a10
        2,b20
        3,c30
        4,d40
        5,e50
        """)

        exp = tw.dedent("""
        code\tvalue\tdescription\tparent_descs
        a10\t5\ta desc\t
        b20\t1\tb desc\t[a desc]
        c30\t3\tc desc\t[a desc]
        d40\t4\td desc\t[a desc] [c desc]
        e50\t2\te desc\t[a desc] [b desc]
        """).strip()

        with open('icd10.tsv', 'wt') as f: f.write(codings)
        with open('data.tsv',  'wt') as f: f.write(data)

        with mock.patch('funpack.hierarchy.getHierarchyFilePath',
                        return_value='icd10.tsv'):
            main.main('-cl 1 convertICD10Codes '
                      '-imf icd10_mappings.tsv out.tsv data.tsv'
                      .split())

        with open('icd10_mappings.tsv', 'rt') as f:
            got = f.read().strip()

        assert exp == got


@patch_logging
def test_main_import_all():

    with tempdir():

        gen_test_data(10, 20, 'data.tsv')

        main.main('-nb out.tsv data.tsv'.split())
        baseline = pd.read_csv('out.tsv', delimiter='\t', index_col=0)

        main.main('--import_all -nb -ow out.tsv data.tsv'.split())
        passthru = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        assert np.all(baseline == passthru)

        main.main('-v 1:3 --import_all -nb -ow out.tsv data.tsv'.split())
        dropvars = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        exp = baseline.loc[:, ['1-0.0', '2-0.0', '3-0.0']]
        assert np.all(dropvars == exp)

        main.main('-v 3:-1:1 --import_all -nb -ow out.tsv data.tsv'.split())
        ordered = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        exp = baseline.loc[:, ['3-0.0', '2-0.0', '1-0.0']]
        assert np.all(ordered == exp)


        vartable = tw.dedent("""
        ID\tType\tDescription\tDataCoding\tNAValues\tRawLevels\tNewLevels\tParentValues\tChildValues\tClean
        3
        4
        5
        """).strip()

        with open('variables.tsv', 'wt') as f:
            f.write(vartable)

        main.main('-r -nb -vf variables.tsv --import_all -ow out.tsv data.tsv'.split())
        ordered = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        exp = baseline.loc[:, ['3-0.0', '4-0.0', '5-0.0']]
        assert np.all(ordered == exp)


@patch_logging
def test_main_unknown_vars():

    vartable = tw.dedent("""
    ID\tType\tDescription\tDataCoding\tNAValues\tRawLevels\tNewLevels\tParentValues\tChildValues\tClean
    1
    2
    3
    4
    5
    """).strip()

    exp = tw.dedent("""
    name\tfile\tclass\tprocessed\texported
    6-0.0\t{file}\tunknown\t{}\t{}
    7-0.0\t{file}\tunknown\t{}\t{}
    8-0.0\t{file}\tunknown\t{}\t{}
    9-0.0\t{file}\tunknown\t{}\t{}
    10-0.0\t{file}\tunknown\t{}\t{}
    1-0.0\t{file}\tunprocessed\t{}\t{}
    2-0.0\t{file}\tunprocessed\t{}\t{}
    3-0.0\t{file}\tunprocessed\t{}\t{}
    4-0.0\t{file}\tunprocessed\t{}\t{}
    5-0.0\t{file}\tunprocessed\t{}\t{}
    """).strip()

    def check(fname, *fmtargs, **fmtkwargs):

        drop = fmtkwargs.pop('drop', [])

        cexp = exp.split('\n')

        for d in drop:
            cexp = [l for l in cexp if not l.startswith('{}-'.format(d))]
        cexp = '\n'.join(cexp)

        with open(fname, 'rt') as f:
            got = f.read().strip()

        print('exp', cexp.format(*fmtargs, **fmtkwargs))
        print('got')
        print( got)

        assert got == cexp.format(*fmtargs, **fmtkwargs)

    with tempdir() as td:

        fullfile = op.realpath(op.join(td, 'data.tsv'))

        gen_test_data(10, 50, 'data.tsv')
        with open('variables.tsv', 'wt') as f:
            f.write(vartable)

        # don't use --import_all -
        # no file generated
        main.main('-ow -nb '
                  '-vf variables.tsv '
                  '-uf unknowns.tsv '
                  'out.tsv data.tsv'.split())
        assert not op.exists('unknowns.tsv')

        main.main('-ow -nb '
                  '-vf variables.tsv '
                  '-uf unknowns.tsv '
                  '--import_all '
                  'out.tsv data.tsv'.split())

        check('unknowns.tsv',
              1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
              1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
              file=fullfile)
        os.remove('unknowns.tsv')

        # still generated if we use --remove_unknown
        main.main('-ow -nb '
                  '-vf variables.tsv '
                  '-uf unknowns.tsv '
                  '--import_all '
                  '--remove_unknown '
                  'out.tsv data.tsv'.split())
        check('unknowns.tsv',
              1, 0, 1, 0, 1, 0, 1, 0, 1, 0,
              1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
              file=fullfile)
        os.remove('unknowns.tsv')

        # some unknowns exported, some dropped
        main.main('-ow -nb '
                  '-vf variables.tsv '
                  '-uf unknowns.tsv '
                  '-v 3:7 '
                  '--import_all '
                  'out.tsv data.tsv'.split())
        check('unknowns.tsv',
              1, 1, 1, 1, 1, 0, 1, 0, 1, 0,
              1, 0, 1, 0, 1, 1, 1, 1, 1, 1,
              file=fullfile)
        os.remove('unknowns.tsv')

        # some unknowns
        # failed processing
        data2 = pd.read_csv('data.tsv', delimiter='\t', index_col=0)
        data2.loc[1:45, '6-0.0'] = np.nan
        data2.loc[5:,   '8-0.0'] = np.nan
        data2.to_csv('data2.tsv', sep='\t')
        fullfile2 = op.realpath(op.join(td, 'data2.tsv'))
        main.main('-ow -nb -n -n '
                  '-sp '
                  '-apr 6 removeIfSparse(minpres=20) '
                  '-apr 8 removeIfSparse(minpres=20) '
                  '-vf variables.tsv '
                  '-uf unknowns.tsv '
                  '--import_all '
                  'out.tsv data2.tsv'.split())
        check('unknowns.tsv',
              0, 0, 1, 1, 0, 0, 1, 1, 1, 1,
              1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
              file=fullfile2)
        os.remove('unknowns.tsv')

        # known vars with
        # processing omitted
        main.main('-ow -nb -n -n '
                  '-sp '
                  '-nv 1 "1,2,3" '
                  '-vf variables.tsv '
                  '-uf unknowns.tsv '
                  '--import_all '
                  'out.tsv data.tsv'.split())
        check('unknowns.tsv',
              1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
              1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
              file=fullfile,
              drop=[1])
        os.remove('unknowns.tsv')


@patch_logging
def test_main_import_all_variable_removed():

    data = tw.dedent("""
    f.eid\t1-0.0\t2-0.0
    1\t5\t10
    2\t6\t
    3\t7\t
    4\t8\t
    5\t9\t
    6\t10\t
    7\t11\t
    8\t12\t
    9\t13\t
    10\t14\t
    """).strip()

    with tempdir():
        with open('data.tsv', 'wt') as f:
            f.write(data)

        main.main('-ia -v 1:2 -sp -apr all removeIfSparse(minpres=5) '
                  'out.tsv data.tsv'.split())

        got = pd.read_csv('out.tsv', delimiter='\t', index_col=0)
        assert np.all(got.index == np.arange(1, 11))
        assert got.columns == ['1-0.0']
        assert np.all(got['1-0.0'] == np.arange(5, 15))


@patch_logging
def test_main_navalues():
    data = tw.dedent("""
    f.eid\t1-0.0\t2-0.0
    1\t5\t10
    2\t6\t20
    3\t7\t30
    4\t8\t40
    5\t9\t50
    """).strip()

    with tempdir():
        with open('data.tsv', 'wt') as f:
            f.write(data)

        main.main(shlex.split('-nv 1 "5,7" -nv 2 "40" -sp '
                              'out.tsv data.tsv'))

        got = pd.read_csv('out.tsv', delimiter='\t', index_col=0)

        expc1 = np.array([np.nan, 6, np.nan, 8, 9])
        expc2 = np.array([10, 20, 30, np.nan, 50])

        c1 = np.array(got['1-0.0'])
        c2 = np.array(got['2-0.0'])

        c1nan = np.isnan(c1)
        c2nan = np.isnan(c2)

        assert np.all(np.isnan(expc1) == c1nan)
        assert np.all(np.isnan(expc2) == c2nan)

        assert np.all(expc1[~c1nan] == c1[~c1nan])
        assert np.all(expc2[~c2nan] == c2[~c2nan])


@patch_logging
def test_main_recoding():
    data = tw.dedent("""
    f.eid\t1-0.0\t2-0.0
    1\t5\t10
    2\t6\t20
    3\t7\t30
    4\t8\t40
    5\t9\t50
    """).strip()

    with tempdir():
        with open('data.tsv', 'wt') as f:
            f.write(data)

        main.main(shlex.split('-re 1 "5,7" "50,70" -re 2 "40" "70" -sp '
                              'out.tsv data.tsv'))

        got = pd.read_csv('out.tsv', delimiter='\t', index_col=0)

        expc1 = np.array([50, 6, 70, 8, 9])
        expc2 = np.array([10, 20, 30, 70, 50])

        c1 = np.array(got['1-0.0'])
        c2 = np.array(got['2-0.0'])

        assert np.all(expc1 == c1)
        assert np.all(expc2 == c2)


@patch_logging
def test_main_child_values():
    data = tw.dedent("""
    f.eid\t1-0.0\t2-0.0\t3-0.0
    1\t5\t\t100
    2\t\t20\t200
    3\t7\t30\t300
    4\t8\t40\t400
    5\t\t50\t500
    """).strip()

    with tempdir():
        with open('data.tsv', 'wt') as f:
            f.write(data)

        main.main(shlex.split('-cv 1 "v3 > 400,v2 == 20" "20,50" '
                              '-cv 2 "v3 < 200" "50" '
                              '-nb out.tsv data.tsv'))

        got = pd.read_csv('out.tsv', delimiter='\t', index_col=0)

        expc1 = np.array([  5,  50,   7,   8,  20])
        expc2 = np.array([ 50,  20,  30,  40,  50])
        expc3 = np.array([100, 200, 300, 400, 500])

        c1 = np.array(got['1-0.0'])
        c2 = np.array(got['2-0.0'])
        c3 = np.array(got['3-0.0'])

        assert np.all(expc1 == c1)
        assert np.all(expc2 == c2)
        assert np.all(expc3 == c3)


@patch_logging
def test_main_no_builtins():

    # TODO This test is obsolete

    vt, _, _, _          = gen_tables([1, 2])
    vt.at[1, 'NAValues'] = '1, 2, 3'
    vt.at[2, 'NAValues'] = '4, 5, 6'

    data = tw.dedent("""
    eid\t1-0.0\t2-0.0
    1\t1\t4
    2\t2\t5
    3\t3\t6
    4\t4\t7
    5\t5\t8
    """)

    expwith = np.array([[np.nan, np.nan, np.nan, 4, 5],
                        [np.nan, np.nan, np.nan, 7, 8]]).T
    expwout = np.array([[1, 2, 3, 4, 5],
                        [4, 5, 6, 7, 8]]).T

    with tempdir():

        with open('data.tsv', 'wt') as f:
            f.write(data)

        vt.to_csv('variables.tsv', sep='\t')

        with patch_base_tables():

            # we have to pass -vf in, as the
            # original DEFAULT_VFILE is baked
            # into  config.CLI_ARGUMENTS,
            # which is a pain to patch. This
            # has the same effect.
            #
            # And we skip processing for the first
            # one, otherwise the default redundancy
            # check will remove one of our vars
            main.main('-sp -vf variables.tsv out1.tsv data.tsv'.split())
            main.main('-nb                   out2.tsv data.tsv'.split())

            gotwith = np.array(pd.read_csv('out1.tsv',
                                           delimiter='\t',
                                           index_col=0))
            gotwout = np.array(pd.read_csv('out2.tsv',
                                           delimiter='\t',
                                           index_col=0))

            expwithna = np.isnan(expwith)

            assert np.all(         expwithna  == np.isnan(gotwith))
            assert np.all(expwith[~expwithna] == gotwith[~expwithna])

            assert np.all(gotwout == expwout)


@patch_logging
def test_main_indexes():
    data1 = tw.dedent("""
    eid,col1,col2
    1,11,21
    2,12,22
    3,13,23
    4,14,24
    """).strip()
    data2 = tw.dedent("""
    col3,eid,col4
    31,1,41
    32,2,42
    33,3,43
    34,4,44
    """).strip()
    data3 = tw.dedent("""
    col5,col6,eid
    51,61,1
    52,62,2
    53,63,3
    54,64,4
    """).strip()

    exp = np.array([np.arange(11, 15),
                    np.arange(21, 25),
                    np.arange(31, 35),
                    np.arange(41, 45),
                    np.arange(51, 55),
                    np.arange(61, 65)])

    with tempdir():
        with open('data1.txt', 'wt') as f: f.write(data1)
        with open('data2.txt', 'wt') as f: f.write(data2)
        with open('data3.txt', 'wt') as f: f.write(data3)

        args = '-nb            ' \
               '-i data1.txt 0 ' \
               '-i data2.txt 1 ' \
               '-i data3.txt 2 '

        main.main((args + 'out1.tsv data1.txt data2.txt data3.txt').split())
        main.main((args + 'out2.tsv data1.txt data3.txt data2.txt').split())
        main.main((args + 'out3.tsv data2.txt data1.txt data3.txt').split())
        main.main((args + 'out4.tsv data2.txt data3.txt data1.txt').split())
        main.main((args + 'out5.tsv data3.txt data1.txt data2.txt').split())
        main.main((args + 'out6.tsv data3.txt data2.txt data1.txt').split())

        for out in range(1, 7):
            fname = 'out{}.tsv'.format(out)

            df = pd.read_csv(fname, index_col=0, delimiter='\t')

            gotcols = list(sorted(df.columns))
            expcols = ['col{}'.format(i) for i in range(1, 7)]

            assert gotcols == expcols

            expdf            = pd.DataFrame(exp.T)
            expdf.index      = [1, 2, 3, 4]
            expdf.index.name = 'eid'
            expdf.columns    = expcols

            assert np.all(df[expcols] == expdf[expcols])


@patch_logging
def test_main_bad_inputs():

    data = tw.dedent("""
    eid,col1
    1,10
    2,20
    3,30
    4,40
    5,50
    """)

    badfile1 = tw.dedent("""
    a
    1
    2
    3
    """)

    badfile2 = tw.dedent("""
    1
    a
    3
    """)

    with tempdir():
        with open('data.txt',     'wt') as f: f.write(data)
        with open('badfile1.txt', 'wt') as f: f.write(badfile1)
        with open('badfile2.txt', 'wt') as f: f.write(badfile2)

        with pytest.raises(Exception):
            main.main('out.tsv nofile')

        with pytest.raises(Exception):
            main.main('-v foo out.tsv data.txt')
        with pytest.raises(Exception):
            main.main('-v 1,foo,3 out.tsv data.txt')
        with pytest.raises(Exception):
            main.main('-v 1:foo:3 out.tsv data.txt')
        with pytest.raises(Exception):
            main.main('-v nofile out.tsv data.txt')
        with pytest.raises(Exception):
            main.main('-v badfile1.txt sout.tsv data.txt')
        with pytest.raises(Exception):
            main.main('-v badfile2.txt sout.tsv data.txt')

        with pytest.raises(Exception):
            main.main('-s foo out.tsv data.txt')
        with pytest.raises(Exception):
            main.main('-s 1,foo,3 out.tsv data.txt')
        with pytest.raises(Exception):
            main.main('-s 1:foo:3 out.tsv data.txt')
        with pytest.raises(Exception):
            main.main('-s nofile out.tsv data.txt')
        with pytest.raises(Exception):
            main.main('-s badfile1.txt sout.tsv data.txt')
        with pytest.raises(Exception):
            main.main('-s badfile2.txt sout.tsv data.txt')

        with pytest.raises(Exception):
            main.main('-ex foo out.tsv data.txt')
        with pytest.raises(Exception):
            main.main('-ex 1,foo,3 out.tsv data.txt')
        with pytest.raises(Exception):
            main.main('-ex 1:foo:3 out.tsv data.txt')
        with pytest.raises(Exception):
            main.main('-ex nofile out.tsv data.txt')
        with pytest.raises(Exception):
            main.main('-ex badfile1.txt sout.tsv data.txt')
        with pytest.raises(Exception):
            main.main('-ex badfile2.txt sout.tsv data.txt')


@patch_logging
def test_main_column_patterns():

    data = tw.dedent("""
    eid,col1,column2,col3
    1,11,21,31
    2,12,22,32
    3,13,23,33
    4,14,24,34
    5,15,25,35
    """).strip()

    with tempdir():
        with open('data.txt', 'wt') as f:
            f.write(data)

        main.main('-nb -co column2 -co col3 out1.txt data.txt'.split())
        main.main('-nb -co col?             out2.txt data.txt'.split())

        got1 = pd.read_csv('out1.txt', delimiter='\t', index_col=0)
        got2 = pd.read_csv('out2.txt', delimiter='\t', index_col=0)

        assert np.all(got1.columns == ['column2', 'col3'])
        assert np.all(got2.columns == ['col1',    'col3'])


@patch_logging
def test_main_importAll_column_patterns():

    data = tw.dedent("""
    eid,col1,column2,col3
    1,11,21,31
    2,12,22,32
    3,13,23,33
    4,14,24,34
    5,15,25,35
    """).strip()

    with tempdir():
        with open('data.txt', 'wt') as f:
            f.write(data)

        main.main('-nb -ia -co column2 -co col3 out1.txt data.txt'.split())
        main.main('-nb -ia -co col?             out2.txt data.txt'.split())

        got1 = pd.read_csv('out1.txt', delimiter='\t', index_col=0)
        got2 = pd.read_csv('out2.txt', delimiter='\t', index_col=0)

        assert np.all(got1.columns == ['column2', 'col3'])
        assert np.all(got2.columns == ['col1',    'col3'])


@patch_logging
def test_main_column_patterns_and_variables():

    data = tw.dedent("""
    eid,col1,1-0.0,2-0.0,3-0.0
    1,101,11,21,31
    2,102,12,22,32
    3,103,13,23,33
    4,104,14,24,34
    5,105,15,25,35
    """).strip()

    with tempdir():
        with open('data.txt', 'wt') as f:
            f.write(data)

        main.main('-nb -co col1 -v 1 -v 3 out.txt data.txt'.split())

        got = pd.read_csv('out.txt', delimiter='\t', index_col=0)

        assert np.all(got.columns == ['col1', '1-0.0', '3-0.0'])


@patch_logging
def test_main_columns_from_file():
    data = tw.dedent("""
    eid,a,b,c,d1,d2,e
    1,10,100,1000,10000,100000,1000000
    2,20,200,2000,20000,200000,2000000
    3,30,300,3000,30000,300000,3000000
    4,40,400,4000,40000,400000,4000000
    5,50,500,5000,50000,500000,5000000
    """).strip()


    with tempdir():
        with open('data.txt', 'wt') as f:
            f.write(data)
        with open('cols.txt', 'wt') as f:
            f.write('a\nb\n')

        main.main(shlex.split(
            '-nb -co cols.txt -co "d*" -co e out.txt data.txt'))

        got = pd.read_csv('out.txt',  index_col=0, delimiter='\t')
        exp = pd.read_csv('data.txt', index_col=0).drop(columns=['c'])

        assert got.equals(exp)


@patch_logging
def test_main_variables_and_visits():

    data = tw.dedent("""
    id,1-0.0,1-1.0,2-0.0,3-0.0,3-1.0
    1,11,110,21,31,310
    2,12,120,22,32,320
    3,13,130,23,33,330
    4,14,140,24,34,340
    5,15,150,25,35,350
    """).strip()

    with tempdir():
        with open('data.txt', 'wt') as f:
            f.write(data)

        main.main('-nb -v 1 -v 3 -vi last out.txt data.txt'.split())

        got = pd.read_csv('out.txt', delimiter='\t', index_col=0)

        assert np.all(got.columns == ['1-1.0', '3-1.0'])


@patch_logging
def test_main_argparse_bug_workaround():
    # https://bugs.python.org/issue9334
    data = tw.dedent("""
    id,1-0.0,2-0.0
    1,11,-10
    2,12,-11
    3,13,-13
    4,14,-14
    5,15,-15
    """).strip()

    with tempdir():
        with open('data.txt', 'wt') as f:
            f.write(data)

        main.main(
            shlex.split('-nb -re  2 "-10,-11" "-11,-12" out.txt data.txt'))

        got = pd.read_csv('out.txt', delimiter='\t', index_col=0)

        assert np.all(got['1-0.0'] == range( 11,  16))
        assert np.all(got['2-0.0'] == range(-11, -16, -1))


@patch_logging
def test_main_description_file():

    vartable = tw.dedent("""
    ID\tType\tDescription\tDataCoding\tNAValues\tRawLevels\tNewLevels\tParentValues\tChildValues\tClean
    1\t\tvar one
    2\t\tvar two
    3\t\tvar three
    4
    """).strip()

    proctable = tw.dedent("""
    Variable\tProcess
    1\tmyprocess
    2\tmyprocess(metaproc='mymetaproc')
    """)

    @custom.processor()
    def myprocess(dtable, vids):
        columns = it.chain(*[dtable.columns(v) for v in vids])

        add     = []
        addvid  = []
        addmeta = []

        for col in columns:
            series = dtable[:, col.name]
            col.metadata = col.vid + 20

            newseries = pd.Series(series + 5, name=col.name + '_a')
            dtable[:, col.name] = dtable[:, col.name] + 3

            add    .append(newseries)
            addvid .append(col.vid)
            addmeta.append(col.vid + 40)

        return [], add, addvid, addmeta

    @custom.metaproc()
    def mymetaproc(val):
        return str(val) + ' metaprocced'

    with tempdir():
        with open('vartable.tsv',  'wt') as f: f.write(vartable)
        with open('proctable.tsv', 'wt') as f: f.write(proctable)

        gen_test_data(4, 10, 'data.tsv')

        main.main('-nb -vf vartable.tsv -pf proctable.tsv '
                  '-def descriptions.tsv '
                  'out.tsv data.tsv'.split())

        inp   = pd.read_csv('data.tsv',         delimiter='\t', index_col=0)
        got   = pd.read_csv('out.tsv',          delimiter='\t', index_col=0)
        descs = pd.read_csv('descriptions.tsv',
                            delimiter='\t',
                            index_col=0,
                            header=None,
                            names=('column', 'description'))

        assert all(got.columns == ['1-0.0', '1-0.0_a',
                                   '2-0.0', '2-0.0_a',
                                   '3-0.0', '4-0.0'])

        assert (got['1-0.0']   == (inp['1-0.0'] + 3)).all()
        assert (got['1-0.0_a'] == (inp['1-0.0'] + 5)).all()
        assert (got['2-0.0']   == (inp['2-0.0'] + 3)).all()
        assert (got['2-0.0_a'] == (inp['2-0.0'] + 5)).all()
        assert (got['3-0.0']   == (inp['3-0.0']))    .all()
        assert (got['4-0.0']   == (inp['4-0.0']))    .all()

        assert descs.loc['1-0.0',   'description'] == 'var one (21)'
        assert descs.loc['1-0.0_a', 'description'] == 'var one (41)'
        assert descs.loc['2-0.0',   'description'] == 'var two (22)'
        assert descs.loc['2-0.0_a', 'description'] == 'var two (42 metaprocced)'
        assert descs.loc['3-0.0',   'description'] == 'var three (0.0)'
        assert descs.loc['4-0.0',   'description'] == 'n/a (0.0)'


def test_main_summary_file():
    class A:
        pass
    with tempdir():
        data = np.random.randint(1, 10, (10, 4))
        dt   = gen_DataTable(data)
        vt   = dt.vartable

        args = A()
        args.summary_file = 'summary.tsv'

        vt.at[1, 'RawLevels']    = [1, 2, 3]
        vt.at[1, 'NewLevels']    = [3, 2, 1]
        vt.at[2, 'NAValues']     = [1, 2, 3, 4]
        vt.at[3, 'ParentValues'] = [expression.Expression('v1 == 0')]
        vt.at[3, 'ChildValues']  = [0]
        vt.at[4, 'Clean']        = {
            'flattenHierarchical' :
            processing.Process('cleaner', 'flattenHierarchical', (), {})}

        main.doSummaryExport(dt, args)

        sum = pd.read_csv('summary.tsv', delimiter='\t', index_col=0)

        assert sum.at[1, 'RawLevels']    == str(vt.at[1, 'RawLevels'])
        assert sum.at[1, 'NewLevels']    == str(vt.at[1, 'NewLevels'])
        assert sum.at[2, 'NAValues']     == str(vt.at[2, 'NAValues'])
        assert sum.at[3, 'ParentValues'] == str(vt.at[3, 'ParentValues'])
        assert sum.at[3, 'ChildValues']  == str(vt.at[3, 'ChildValues'])
        assert sum.at[4, 'Clean']        == '[{}]'.format(
            str(vt.at[4, 'Clean']['flattenHierarchical']))
