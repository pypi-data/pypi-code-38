#!/usr/bin/env python
#
# test_dryrun.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import os.path as op

import numpy  as np
import pandas as pd

import funpack.main as main

from . import gen_DataTable, gen_test_data, tempdir


def test_main_dryrun():
    with tempdir():
        gen_test_data(10, 100, 'data.tsv')
        assert main.main('--dry_run out.tsv data.tsv'.split()) == 0
        assert not op.exists('out.tsv')
