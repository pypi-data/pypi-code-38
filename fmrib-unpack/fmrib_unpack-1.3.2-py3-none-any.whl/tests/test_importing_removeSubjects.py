#!/usr/bin/env python
#
# test_importing_removeSubjects.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import numpy as np

import funpack.importing as importing

from . import gen_DataTable


def test_removeSubjects():

    data = np.random.randint(1, 10, (10, 500))

    # Options in order of precedence:
    #
    #   - exclude:  list of subjects to *exclude*
    #   - exprs:    list of expressions specifying *inclusion*

    # pass through
    dtable = gen_DataTable(data)
    importing.removeSubjects(dtable)
    assert np.all(dtable.index == np.arange(1, 501))
    assert np.all(dtable[:, :] == data.T)

    # exclude
    dtable = gen_DataTable(data)
    importing.removeSubjects(dtable, exclude=[1, 2, 3])
    assert np.all(dtable.index ==         np.arange(4, 501))
    assert np.all(dtable[:, :] == data[:, np.arange(3, 500)].T)

    # expr
    mask     = data[0, :] > 5
    dtable = gen_DataTable(data)
    importing.removeSubjects(dtable, exprs=['v1 > 5'])
    assert np.all(dtable.index == (np.where(mask)[0] + 1))
    assert np.all(dtable[:, :] == data[:, mask].T)

    # expr + exclude
    mask     = data[0, :] > 5
    mask[:3] = 0
    dtable = gen_DataTable(data)
    importing.removeSubjects(dtable, exprs=['v1 > 5'], exclude=[1, 2, 3])
    assert np.all(dtable.index == (np.where(mask)[0] + 1))
    assert np.all(dtable[:, :] == data[:, mask].T)

    # multiple expressions
    dtable = gen_DataTable(data)
    importing.removeSubjects(dtable, exprs=['v1 > 5', 'v2 == 9'])
    mask = (data[0, :] > 5) | (data[1, :] == 9)
    assert np.all(dtable.index == np.where(mask)[0] + 1)
    assert np.all(dtable[:, :] == data[:, mask].T)
