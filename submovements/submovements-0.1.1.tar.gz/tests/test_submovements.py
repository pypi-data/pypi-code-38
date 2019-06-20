"""Tests for `submovements` package."""

import pytest

from DataProcessing import Preprocessor, Trial
import pandas as pd
import numpy as np
from glob import glob
import os

def test_preprocessor_instance():
    pproc = Preprocessor()
    assert isinstance(pproc, Preprocessor)


def test_trial_instance():
    trial = Trial()
    assert isinstance(trial, Trial)


def test_invalid_source_dir():
    with pytest.raises(AssertionError) as AE:
        pproc = Preprocessor()
        gen = pproc.lopad_df_from_directory_gen('$')
        for t in gen:
            print(t)
    assert 'Destination directory does not exist' in str(AE)


def test_empty_source_dir():
    with pytest.raises(AssertionError) as AE:
        pproc = Preprocessor()
        gen = pproc.load_df_from_directory_gen('empty_dir')
        for t in gen:
            print(t)
    assert 'No source files' in str(AE)


def test_source_dir_with_bad_file_name():
    with pytest.raises(AssertionError) as AE:
        pproc = Preprocessor()
        gen = pproc.load_df_from_directory_gen('dir_with_bad_file_name')
        for t in gen:
            print(t)
    assert 'No source files' in str(AE)


def test_load_bad_file():
    with pytest.raises(AssertionError) as AE:
        pproc = Preprocessor()
        gen = pproc.load_df_from_directory_gen('dir_with_corrupt_file')
        for t in gen:
            print(t)
    assert 'Could not load' in str(AE)


def test_plot_empty_df():
    with pytest.raises(AssertionError) as AE:
        pproc = Preprocessor()
        gen = pproc.load_df_from_directory_gen('good_data')
        df = pd.DataFrame()
        for t in gen:
            pproc.plot(df)
    assert 'No data' in str(AE)


def test_process_empty_df():
    with pytest.raises(AssertionError) as AE:
        pproc = Preprocessor()
        gen = pproc.load_df_from_directory_gen('good_data')
        df = pd.DataFrame()
        for t in gen:
            pproc.filter_raw_data(df)
    assert 'No data' in str(AE)


def test_remove_baseline_empty_df():
    with pytest.raises(AssertionError) as AE:
        pproc = Preprocessor()
        gen = pproc.load_df_from_directory_gen('good_data')
        df = pd.DataFrame()
        for t in gen:
            pproc.remove_baseline(df)
    assert 'No data' in str(AE)


def test_remove_baseline_bad_threshold():
    with pytest.raises(AssertionError) as AE:
        pproc = Preprocessor()
        gen = pproc.load_df_from_directory_gen('good_data')
        for t in gen:
            pproc.remove_baseline(t.position_data, threshold=0)
    assert 'Threshold' in str(AE)

def test_data_processing_and_save_csv():
    path_to_raw_data = 'good_data/'
    path_to_trials = 'good_data/csv/'

    pproc = Preprocessor()
    raw_data_gen = pproc.load_df_from_directory_gen(dir_path=path_to_raw_data, cols=('x', 'y'))

    for trial in raw_data_gen:
        trial.preprocess(pproc)
        trial.save_df(trial.data, path_to_trials)

    list_of_raws = glob(os.path.join(path_to_raw_data, 'li_*.csv'))
    list_of_results = glob(os.path.join(path_to_trials, '*.csv'))
    assert list_of_raws == list_of_results
