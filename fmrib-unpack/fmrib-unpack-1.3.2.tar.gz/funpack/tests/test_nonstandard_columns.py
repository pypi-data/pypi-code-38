#!/usr/bin/env python
#
# test_nonstandard_columns.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import             shlex
import textwrap as tw

import pandas   as pd
import numpy    as np

import funpack.main as main


from . import (patch_logging,
               clear_plugins,
               tempdir,
               gen_tables,
               gen_DataTable,
               gen_test_data,
               gen_DataTableFromDataFrame)


@patch_logging
def test_nonstandard_columns():

    indata = tw.dedent("""
    f.eid,f.1.0.0,f.2.0.0,f.3.0.0
    1,4,7,3
    2,1,9,2
    3,,3,5
    """).strip()

    tests = [
        ('-nb -nv 2 7',
         """
         f.eid,f.1.0.0,f.2.0.0,f.3.0.0
         1,4,,3
         2,1,9,2
         3,,3,5
         """),
        ('-nb -re 3 2,3 10,20',
         """
         f.eid,f.1.0.0,f.2.0.0,f.3.0.0
         1,4,7,20
         2,1,9,10
         3,,3,5
         """),
        ('-nb -cv 1 "v2 == 3" 25',
         """
         f.eid,f.1.0.0,f.2.0.0,f.3.0.0
         1,4,7,3
         2,1,9,2
         3,25,3,5
         """),
    ]

    for cmd, expout in tests:
        with tempdir():
            expout = tw.dedent(expout).strip()

            with open('in.csv',  'wt') as f: f.write(indata)
            with open('exp.csv', 'wt') as f: f.write(expout)

            main.main(shlex.split(cmd + ' out.csv in.csv'))

            got = pd.read_csv('out.csv', index_col=0, delimiter='\t')
            exp = pd.read_csv('exp.csv', index_col=0)

            assert np.all(exp.columns             == got.columns)
            assert np.all(np.isnan(exp.loc[:, :]) == np.isnan(got.loc[:, :]))
            assert np.all(exp.loc[:, :].notna()   == got.loc[:, :].notna())
