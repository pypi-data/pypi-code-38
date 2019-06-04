#!/usr/bin/env python
#
# test_icd10.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import textwrap as tw

from unittest import mock

import pytest

import numpy  as np
import pandas as pd

import funpack.icd10     as icd10
import funpack.hierarchy as hierarchy

from . import tempdir

def test_store_saveCodes():

    with tempdir():

        icd10.storeCodes.store = []

        with pytest.raises(ValueError):
            icd10.saveCodes('file', None, ['badfield'])

        codings = tw.dedent("""
        coding\tmeaning\tnode_id\tparent_id
        a10\ta desc\t5\t0
        b20\tb desc\t1\t5
        c30\tc desc\t3\t5
        d40\td desc\t4\t3
        e50\te desc\t2\t1
        f60\tf desc\t9\t9
        """)

        with open('codings.tsv', 'wt') as f:
            f.write(codings)

        codes = ['a10', np.nan, 'b20', 'c30', 'd40', 'e50']

        icd10.storeCodes(codes[:2])
        icd10.storeCodes(codes[2:])

        del codes[1]

        h = hierarchy.loadHierarchyFile('codings.tsv')

        with mock.patch('funpack.hierarchy.getHierarchyFilePath',
                        return_value='codings.tsv'):
            icd10.saveCodes(
                'mapping.tsv', h,
                fields=['code', 'value', 'description',
                        'parent_codes', 'parent_descs'])

        values = [h.index(c) + 1 for c in codes]

        mf      = pd.read_csv('mapping.tsv', delimiter='\t', index_col=False)
        descs   = ['a desc', 'b desc', 'c desc', 'd desc', 'e desc']
        pcodes  = [np.nan, 'a10', 'a10', 'a10,c30', 'a10,b20']
        pdescs  = [np.nan, '[a desc]', '[a desc]',
                   '[a desc] [c desc]', '[a desc] [b desc]']

        gotpcodes = mf['parent_codes']
        gotpdescs = mf['parent_descs']

        assert (mf['code']         == codes) .all()
        assert (mf['value']        == values).all()
        assert (mf['description']  == descs) .all()
        assert np.isnan(gotpcodes.iloc[0])
        assert np.isnan(gotpdescs.iloc[0])
        assert (gotpcodes.iloc[1:] == pcodes[1:]).all()
        assert (gotpdescs.iloc[1:] == pdescs[1:]).all()
