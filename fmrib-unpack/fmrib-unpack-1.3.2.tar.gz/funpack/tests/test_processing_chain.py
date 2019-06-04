#!/usr/bin/env python
#
# test_processing_chain.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import textwrap as tw

import numpy as np

import funpack.main as main


from . import tempdir, patch_logging


@patch_logging
def test_binariseCategorical_outputs_go_through_sparsity_check():

    data = tw.dedent("""
    eid\t1-0.0\t2-0.0
    1\t0\t1
    2\t1\t1
    3\t1\t1
    4\t1\t2
    5\t1\t2
    6\t1\t2
    7\t1\t3
    8\t1\t3
    9\t1\t3
    10\t1\t3
    """).strip()

    # binarised outputs from var 1
    # should fail the maxcat test,
    # but those from var 2 should
    # pass

    exp = tw.dedent("""
    eid\t2-1\t2-2\t2-3
    1\t1\t0\t0
    2\t1\t0\t0
    3\t1\t0\t0
    4\t0\t1\t0
    5\t0\t1\t0
    6\t0\t1\t0
    7\t0\t0\t1
    8\t0\t0\t1
    9\t0\t0\t1
    10\t0\t0\t1
    """).strip()

    variables = tw.dedent("""
    ID\tType\tDescription\tDataCoding\tNAValues\tRawLevels\tNewLevels\tParentValues\tChildValues\tClean
    1\tInteger
    2\tInteger
    """).strip()

    with tempdir():

        with open('data.tsv',      'wt') as f: f.write(data)
        with open('variables.tsv', 'wt') as f: f.write(variables)

        main.main('-sp -n -n '
                  '-vf variables.tsv '
                  '-apr 1 binariseCategorical(nameFormat="{vid}-{value}") '
                  '-apr 2 binariseCategorical(nameFormat="{vid}-{value}") '
                  '-apr all removeIfSparse(maxcat=0.8,abscat=False) '
                  'out.tsv data.tsv'.split())

        with open('out.tsv', 'rt') as f:
            got = f.read().strip()

    assert got == exp
