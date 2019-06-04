#!/usr/bin/env python


import random
import textwrap as tw
import os.path  as op

import numpy as np
import pandas as pd

import funpack.hierarchy as hierarchy

from . import (tempdir, gen_DataTable)


def test_getHierarchyFilePath():

    dt = gen_DataTable([np.random.randint(1, 10, 10)])

    dt.vartable.loc[1, 'DataCoding'] = 123

    exp = op.join(op.dirname(hierarchy.__file__),
                  'data', 'hierarchy', 'coding123.tsv')
    assert hierarchy.getHierarchyFilePath(dt, 1) == exp


def test_loadHierarchyFile():

    hier = tw.dedent("""
    coding	meaning	node_id	parent_id
    30	meaning 30	3	1
    40	meaning 40	4	1
    50	meaning 50	5	4
    20	meaning 20	2	0
    60	meaning 60	6	2
    10	meaning 10	1	0
    """).strip()

    with tempdir():

        with open('hier.txt', 'wt') as f:
            f.write(hier)

        h = hierarchy.loadHierarchyFile('hier.txt')

        print(h._Hierarchy__codings)

        assert h.parents(10) == []
        assert h.parents(20) == []
        assert h.parents(30) == [10]
        assert h.parents(40) == [10]
        assert h.parents(50) == [40, 10]
        assert h.parents(60) == [20]



def test_codeToNumeric():

    icd10hier = hierarchy.getHierarchyFilePath(name='icd10')
    icd10hier = hierarchy.loadHierarchyFile(icd10hier)
    codes     = list(random.sample(icd10hier.codings, 20)) + ['badcode']
    exp       = [icd10hier.index(c) + 1 for c in codes[:-1]] + [np.nan]

    conv = [hierarchy.codeToNumeric(c, 'icd10') for c in codes]

    exp  = np.array(exp)
    conv = np.array(conv)

    expna  = np.isnan(exp)
    convna = np.isnan(conv)

    assert np.all(     expna  ==       convna)
    assert np.all(exp[~expna] == conv[~convna])

    ncodes = [(code, ncode)
              for code, ncode
              in zip(codes, conv)
              if not pd.isna(ncode)]

    codes, ncodes = zip(*ncodes)
    codes = [c.lower() for c in codes]

    assert codes == [hierarchy.numericToCode(c, 'icd10').lower()
                     for c in ncodes]


def test_Hierarchy():
    with tempdir():
        data = tw.dedent("""
        coding\tmeaning\tnode_id\tparent_id
        a\ta desc\t5\t0
        b\tb desc\t1\t5
        c\tc desc\t3\t5
        d\td desc\t4\t3
        e\te desc\t2\t1
        """)

        with open('codings.tsv', 'wt') as f:
            f.write(data)

        h = hierarchy.loadHierarchyFile('codings.tsv')

        assert h.index('a') == 4
        assert h.index('b') == 0
        assert h.index('c') == 2
        assert h.index('d') == 3
        assert h.index('e') == 1
        assert h.coding(0)  == 'b'
        assert h.coding(1)  == 'e'
        assert h.coding(2)  == 'c'
        assert h.coding(3)  == 'd'
        assert h.coding(4)  == 'a'

        assert h.parents('a') == []
        assert h.parents('b') == ['a']
        assert h.parents('c') == ['a']
        assert h.parents('d') == ['c', 'a']
        assert h.parents('e') == ['b', 'a']

        assert h.description('a') == 'a desc'
        assert h.description('b') == 'b desc'
        assert h.description('c') == 'c desc'
        assert h.description('d') == 'd desc'
        assert h.description('e') == 'e desc'

        h.set('a', 'meta', 'aa')
        h.set('b', 'meta', 'bb')
        h.set('c', 'meta', 'cc')
        h.set('d', 'meta', 'dd')
        h.set('e', 'meta', 'ee')

        assert h.get('a', 'meta') == 'aa'
        assert h.get('b', 'meta') == 'bb'
        assert h.get('c', 'meta') == 'cc'
        assert h.get('d', 'meta') == 'dd'
        assert h.get('e', 'meta') == 'ee'
