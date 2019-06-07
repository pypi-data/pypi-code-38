# Tai Sakuma <tai.sakuma@gmail.com>
import os
import numpy as np
import pandas as pd

import pytest

from pandas.util.testing import assert_frame_equal

import alphatwirl

from qtwirl import qtwirl

##__________________________________________________________________||
pytestmark = pytest.mark.filterwarnings('ignore::RuntimeWarning')

##__________________________________________________________________||
TESTDATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

SAMPLE_ROOT_FILE_DIR = os.path.join(TESTDATADIR, 'root')
SAMPLE_ROOT_FILE_NAMES = [
    'sample_chain_01.root',
    'sample_chain_02.root',
    'sample_chain_03_zombie.root',
    'sample_chain_04.root',
]
SAMPLE_ROOT_FILE_PATHS = [os.path.join(SAMPLE_ROOT_FILE_DIR, n) for n in SAMPLE_ROOT_FILE_NAMES]

##__________________________________________________________________||
@pytest.fixture()
def file_dir(tmpdir_factory):
    ret = str(tmpdir_factory.mktemp(''))
    return ret

@pytest.mark.parametrize('store_file', [False, True])
def test_one_table(store_file, file_dir):

    ##
    sample_paths = SAMPLE_ROOT_FILE_PATHS

    ##
    RoundLog = alphatwirl.binning.RoundLog
    reader_cfg = dict(
        key_name='jet_pt',
        key_binning=RoundLog(0.1, 100),
        key_index='*',
        key_out_name='jet_pt',
        store_file=store_file,
        file_dir=file_dir
    )

    results = qtwirl(
        sample_paths,
        reader_cfg=reader_cfg,
        tree_name='tree',
        process=16,
        quiet=False,
        max_events_per_process=500
    )

    ##
    tbl_expected_dir = os.path.join(TESTDATADIR, 'tbl')
    tbl_expected_path = os.path.join(tbl_expected_dir, '00', 'tbl_n.jet_pt-w.txt')
    tbl_expected = pd.read_csv(tbl_expected_path, delim_whitespace=True)

    ##
    assert_frame_equal(tbl_expected, results, check_names=True)

    ##
    if store_file is True:
        tbl_stored_file_name = 'tbl_n.jet_pt-w.txt'
        assert [tbl_stored_file_name] == os.listdir(file_dir)
        tbl_stored_path = os.path.join(file_dir, tbl_stored_file_name)
        tbl_stored = pd.read_csv(tbl_stored_path, delim_whitespace=True)
        assert_frame_equal(tbl_expected, tbl_stored, check_names=True)
    else:
        assert [ ] == os.listdir(file_dir)

##__________________________________________________________________||
@pytest.mark.parametrize('count', [False, True])
@pytest.mark.parametrize('store_file', [False, True])
def test_one_selection_four_tables(count, store_file, file_dir):

    ##
    sample_paths = SAMPLE_ROOT_FILE_PATHS

    ##
    RoundLog = alphatwirl.binning.RoundLog
    from scribblers.essentials import FuncOnNumpyArrays
    reader_cfg = [
        dict(set_default=dict(
            table_cfg=dict(
                store_file=store_file,
                file_dir=file_dir
            ),
            selection_cfg=dict(
                store_file=store_file,
                file_dir=file_dir
            )
        )),
        dict(selection_cfg=dict(
            condition=dict(All=('ev: ev.njets[0] > 4', )),
            count=count
        )),
        dict(key_name='jet_pt',
             key_binning=RoundLog(0.1, 100),
             key_index='*',
             key_out_name='jet_pt'
        ),
        dict(key_name='met',
             key_binning=RoundLog(0.1, 100)
        ),
        dict(
            key_name=('njets', 'met'),
            key_binning=(None, RoundLog(0.2, 100, min=50, underflow_bin=0))
        ),
        dict(reader=FuncOnNumpyArrays(
            src_arrays=['jet_pt'],
            out_name='ht',
            func=np.sum)),
        dict(key_name='ht',
             key_binning=RoundLog(0.1, 100)
        ),
    ]

    results = qtwirl(
        sample_paths,
        reader_cfg=reader_cfg,
        tree_name='tree',
        process=16,
        quiet=False,
        max_events_per_process=500
    )

    ##
    tbl_expected_file_names = [
        'tbl_selection_count.txt',
        'tbl_n.jet_pt-w.txt',
        'tbl_n.met.txt',
        'tbl_n.njets.met.txt',
        'tbl_n.ht.txt',
    ]
    if count is False:
        tbl_expected_file_names = tbl_expected_file_names[1:]

    ##
    assert len(tbl_expected_file_names) == len(results)

    ##
    tbl_expected_dir = os.path.join(TESTDATADIR, 'tbl')
    tbl_expected_paths = [os.path.join(tbl_expected_dir, '01', n) for n in tbl_expected_file_names]
    tbls_expected = [pd.read_csv(p, delim_whitespace=True) for p in tbl_expected_paths]

    ##
    for expected, actual in zip(tbls_expected, results):
        assert_frame_equal(expected, actual, check_names=True, check_less_precise=True)


    ##
    if store_file is True:
        assert set(tbl_expected_file_names) == set(os.listdir(file_dir))
        for expected, file_name in zip(tbls_expected, tbl_expected_file_names):
            tbl_stored_path = os.path.join(file_dir, file_name)
            tbl_stored = pd.read_csv(tbl_stored_path, delim_whitespace=True)
            assert_frame_equal(expected, tbl_stored, check_names=True, check_less_precise=True)

    else:
        assert [ ] == os.listdir(file_dir)

##__________________________________________________________________||
