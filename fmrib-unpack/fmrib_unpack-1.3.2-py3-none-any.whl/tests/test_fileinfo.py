#!/usr/bin/env python
#
# test_fileinfo.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import textwrap

import pytest

import funpack.custom as custom
import funpack.fileinfo as fileinfo
import funpack.datatable as datatable

from . import tempdir, clear_plugins


AVID = datatable.AUTO_VARIABLE_ID


sniff_tests = [
    ("""col1, col2, col3
1, 2, 3
4, 5, 6
""",
     [('col1', None, None, None),
      ('col2', None, None, None),
      ('col3', None, None, None)]),
    ("""1, 2, 3
4, 5, 6
7, 8, 9
""",
     [(None, None, None, None),
      (None, None, None, None),
      (None, None, None, None)]),
    ("""col1\tcol2\tcol3
1\t2\t3
4\t5\t6
""",
     [('col1', None, None, None),
      ('col2', None, None, None),
      ('col3', None, None, None)]),
    ("""eid\t1-0.0\t2-1.2\t3-3.5
1\t2\t3\t4
5\t6\t7\t8
9\t10\t11\t12
""",
     [('eid',   None, None, None),
      ('1-0.0', 1, 0, 0),
      ('2-1.2', 2, 1, 2),
      ('3-3.5', 3, 3, 5)]),
    ("""1000   2000   3000
4000   5000   6000
7000   8000   9000
""",
     [(None, None, None, None),
      (None, None, None, None),
      (None, None, None, None)]),
    ("""col1   col2   col3
1000   2000   3000
4000   5000   6000
7000   8000   9000
""",
     [('col1', None, None, None),
      ('col2', None, None, None),
      ('col3', None, None, None)]),

    ("""col1  col2      col3
1000   2000   3000
4000   5000   6000
7000   8000   9000
""",
     [('col1', None, None, None),
      ('col2', None, None, None),
      ('col3', None, None, None)]),

    ("""col1\tcol2\tcol3
\t\t
1\t\t
1\t2\t3
1\t2\t
\t2\t3
\t\t3
""",
     [('col1', None, None, None),
      ('col2', None, None, None),
      ('col3', None, None, None)]),
    ("""1
2
3
4
5
6
""",
     [(None, None, None, None)]),
    ("""col1
2
3
4
5
6
""",
     [('col1', None, None, None)]),
    ("""1-2.3
2
3
4
5
6
""",
     [('1-2.3', 1, 2, 3)]),
    ("""eid
2
3
4
5
6
""",
     [('eid', None, None, None)]),
    ("""eid





""",
     [('eid', None, None, None)]),
    ("""eid\t1-0.0\t2-0.0
\t\t
\t\t
\t\t
\t\t
\t\t
""",
     [('eid',   None, None, None),
      ('1-0.0', 1, 0, 0),
      ('2-0.0', 2, 0, 0)]),
    ("""eid,1-0.0,2-0.0
1,,
2,,
3,,
4,,
5,,3
""",
     [('eid',   None, None, None),
      ('1-0.0', 1, 0, 0),
      ('2-0.0', 2, 0, 0)]),
]


def test_sniff():

    for test, expected in sniff_tests:

        with tempdir():

            with open('data.txt', 'wt') as f:
                f.write(test)

            dialect, cols = fileinfo.sniff('data.txt')

        assert len(cols) == len(expected)

        for i, (exp, col) in enumerate(zip(expected, cols)):

            name, vid, visit, instance = exp

            assert col.datafile == 'data.txt'
            assert col.index    == i
            assert col.name     == name
            assert col.vid      == vid
            assert col.visit    == visit
            assert col.instance == instance


    baddata = textwrap.dedent("""
    abcdefg
    1, 2, 3
    4, 5\t8
    """).strip()


    with tempdir():
        with open('data.txt', 'wt') as f:
            f.write(baddata)

        with pytest.raises(ValueError):
            fileinfo.sniff('data.txt')



fileinfo_tests = [
    ("""col1, col2, col3
1, 2, 3
4, 5, 6
""",
     True,
     [('col1', 0,        0, 0),
      ('col2', AVID,     0, 0),
      ('col3', AVID + 1, 0, 0)]),
    ("""1, 2, 3
4, 5, 6
7, 8, 9
""",
     False,
     [( '0-0.0' .format(0),        0,        0, 0),
      ( '{}-0.0'.format(AVID + 2), AVID + 2, 0, 0),
      ( '{}-0.0'.format(AVID + 3), AVID + 3, 0, 0)]),
    ("""col1\tcol2\tcol3\tcol4
1\t2\t3\t4
5\t6\t7\t8
""",
     True,
     [('col1', 0,        0, 0),
      ('col2', AVID + 4, 0, 0),
      ('col3', AVID + 5, 0, 0),
      ('col4', AVID + 6, 0, 0)]),
    ("""eid\t1-0.0\t2-1.2\t3-3.5
1\t2\t3\t4
5\t6\t7\t8
9\t10\t11\t12
""",
     True,
     [('eid',   0, 0, 0),
      ('1-0.0', 1, 0, 0),
      ('2-1.2', 2, 1, 2),
      ('3-3.5', 3, 3, 5)]),
    ("""1
2
3
4
5
6
""",
     False,
     [('0-0.0', 0, 0, 0)]),
    ("""col1
2
3
4
5
6
""",
     True,
     [('col1', 0, 0, 0)]),
    ("""eid
2
3
4
5
6
""",
     True,
     [('eid', 0, 0, 0)]),
]


def test_fileinfo():

    with tempdir():

        fnames = []

        for i, test in enumerate(fileinfo_tests):
            fnames.append('data{}.txt'.format(i))
            with open(fnames[-1], 'wt') as f:
                f.write(test[0])

        dialects, headers, colss = fileinfo.fileinfo(fnames)

        dialects = list(dialects)
        headers  = list(headers)
        colss    = list(colss)

        fnames.append(fnames[-1])
        sd, sh, sc = fileinfo.fileinfo(fnames[-1])
        dialects.append(sd)
        headers .append(sh)
        colss   .append(sc)

    assert len(dialects) == len(fnames)
    assert len(headers)  == len(fnames)
    assert len(colss)    == len(fnames)

    for ti, test in enumerate(fileinfo_tests):

        exphdr  = test[1]
        expcols = test[2]

        assert headers[ti]    == exphdr
        assert len(colss[ti]) == len(expcols)

        for i, (exp, col) in enumerate(zip(expcols, colss[ti])):

            name, vid, visit, instance = exp

            assert col.datafile == 'data{}.txt'.format(ti)
            assert col.index    == i
            assert col.name     == name
            assert col.vid      == vid
            assert col.visit    == visit
            assert col.instance == instance


def test_fileinfo_indexes():
    data = textwrap.dedent("""
    col1,col2
    1,4
    2,5
    3,6
    """.strip())
    with tempdir():

        with open('data.txt', 'wt') as f:
            f.write(data)

        cols = fileinfo.fileinfo('data.txt')[2][0]
        assert cols[0].vid == 0
        assert cols[1].vid == AVID

        cols = fileinfo.fileinfo('data.txt', indexes={'data.txt' : 0})[2][0]
        assert cols[0].vid == 0
        assert cols[1].vid == AVID

        cols = fileinfo.fileinfo('data.txt', indexes={'data.txt' : 1})[2][0]
        assert cols[0].vid == AVID
        assert cols[1].vid == 0



@clear_plugins
def test_fileinfo_parser():

    customCols = [
        datatable.Column('custom.txt', 'col1', 0, 10, 0, 0),
        datatable.Column('custom.txt', 'col2', 1, 11, 0, 0),
        datatable.Column('custom.txt', 'col3', 2, 12, 0, 0)]

    @custom.sniffer('test_fileinfo')
    def columns(f):
        return customCols


    with tempdir():
        with open('data.txt', 'wt') as f:
            f.write(fileinfo_tests[0][0])

        fnames  = ['data.txt', 'custom.txt']
        parsers = {'custom.txt' : 'test_fileinfo'}

        dialects, headers, colss = fileinfo.fileinfo(
            fnames, sniffers=parsers)

    assert len(dialects) == 2
    assert len(headers)  == 2
    assert len(colss)    == 2

    expcols = fileinfo_tests[0][2]

    for i, (exp, col) in enumerate(zip(expcols, colss[0])):

        name, vid, visit, instance = exp

        assert col.datafile == 'data.txt'
        assert col.index    == i
        assert col.name     == name
        assert col.vid      == vid
        assert col.visit    == visit
        assert col.instance == instance

    assert colss[1] == customCols
