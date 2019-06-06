# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from nose.tools import assert_raises
import os
import shutil
import tempfile

import numpy as np
from numpy.testing import assert_array_equal

from eelbrain import Dataset, datasets, load
from eelbrain.testing import file_path

from ...tests.test_data import assert_dataobj_equal, assert_dataset_equal


def test_r_tsv_io():
    "Test reading output of write.table"
    ds = load.tsv(file_path('r-write.table.txt'))
    assert_array_equal(ds['row'], ['1', '2'])
    assert_array_equal(ds['bin'], [0, 0])


def test_tsv_io():
    """Test tsv I/O"""
    names = ['A', 'B', 'rm', 'intvar', 'fltvar', 'fltvar2', 'index']

    # get Dataset
    ds = datasets.get_uv()
    ds['fltvar'][5:10] = np.nan
    ds[:4, 'rm'] = ''

    # save and load
    tempdir = tempfile.mkdtemp()
    try:
        dst = os.path.join(tempdir, 'ds.txt')

        ds.save_txt(dst)
        ds1 = load.tsv(dst)
        ds2 = load.tsv(dst, skiprows=1, names=names)

        assert_dataset_equal(ds1, ds, decimal=10)
        assert_dataset_equal(ds2, ds, decimal=10)

        # guess data types with missing
        intvar2 = ds['intvar'].as_factor()
        intvar2[10:] = ''
        ds_intvar = Dataset((intvar2,))
        ds_intvar.save_txt(dst)
        ds_intvar1 = load.tsv(dst, empty='nan')
        assert_dataobj_equal(ds_intvar1['intvar', :10], ds['intvar', :10])
        assert_array_equal(ds_intvar1['intvar', 10:], np.nan)

    finally:
        shutil.rmtree(tempdir)
