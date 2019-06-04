#!/usr/bin/env python
#
# test_talk_examples.py - Examples from a talk at OHBA in may 2019.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import os
import shlex
import os.path as op

import pandas as pd
import numpy  as np

import funpack.main as main

from . import (tempdir,
               patch_logging)


tests = list("""
funpack -s ##/subjects1.txt out.tsv ##/data1.tsv
funpack -v ##/variables2.txt out.tsv ##/data2.tsv
funpack -co ##/columns3.txt out.tsv ##/data3.tsv
funpack -s "v1 > 40" out.tsv ##/data4.tsv
funpack -nv 1 -1,-3 out.tsv ##/data5.tsv
funpack -re 1 444,555,500 0.25,0.5,5 out.tsv ##/data6.tsv
funpack -cv 2 v1==0 0 out.tsv ##/data7.tsv
funpack -apr 41202 binariseCategorical out.tsv ##/data8.tsv
funpack -cl 41202 flattenHierarchical out.tsv ##/data9.tsv
""".strip().split('\n'))


EXDIR = op.join(op.dirname(__file__), 'example_data')


@patch_logging
def test_examples():

    with tempdir():
        for i, test in enumerate(tests, 1):

            test = test.replace('##', EXDIR + op.sep)
            test = shlex.split(test)[1:]

            main.main(test)

            expout = pd.read_csv(op.join(EXDIR, 'out{}.tsv'.format(i)),
                                 header=0,
                                 delimiter='\t',
                                 index_col=0)
            gotout = pd.read_csv('out.tsv',
                                 header=0,
                                 delimiter='\t',
                                 index_col=0)

            assert np.all(expout.columns == gotout.columns)
            assert np.all(expout.index   == gotout.index)
            assert np.all(expout.isna()  == gotout.isna())

            for ec, gc in zip(expout.columns, gotout.columns):
                ec = expout[ec]
                gc = gotout[gc]
                assert (ec[~ec.isna()] == gc[~gc.isna()]).all()

            os.remove('out.tsv')
