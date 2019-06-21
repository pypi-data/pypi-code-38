#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @author: Pavel Korshunov <pavel.korshunov@idiap.ch>
# @date: Thu Apr 21 16:41:21 CEST 2016
#


from __future__ import print_function

import bob.measure

import os
import shutil
import tempfile
import numpy

import bob.io.base.test_utils
import bob.bio.base
import bob.bio.base.score.load as bio_load
import bob.pad.base
from bob.bio.base.test import utils

import pkg_resources

dummy_dir = pkg_resources.resource_filename('bob.pad.base', 'test/dummy')
data_dir = pkg_resources.resource_filename('bob.pad.base', 'test/data')


def _detect(parameters, cur_test_dir, sub_dir, score_types=('dev-real',), scores_extension=''):
    from bob.pad.base.script.spoof import main
    try:
        main(parameters)

        # assert that the score file exists
        score_files = [os.path.join(cur_test_dir, sub_dir, 'Default', 'scores',
                                    'scores-%s%s' % (score_type, scores_extension)) for score_type in score_types]
        assert os.path.exists(score_files[0]), "Score file %s does not exist" % score_files[0]

        # also assert that the scores are still the same -- though they have no real meaning
        reference_files = [os.path.join(data_dir, 'scores-%s' % score_type) for score_type in score_types]

        # read reference and new data
        for i in range(0, len(score_types)):
            data2check = []
            for sfile in (score_files[i], reference_files[i]):
                f = bio_load.open_file(sfile)
                d_ = []
                for line in f:
                    if isinstance(line, bytes): line = line.decode('utf-8')
                    d_.append(line.rstrip().split())
                data2check.append(numpy.array(d_))

            assert data2check[0].shape == data2check[1].shape
            # assert that the data order is still correct
            print(data2check)
            assert (data2check[0][:, 0:3] == data2check[1][:, 0:3]).all()
            # assert that the values are OK
            assert numpy.allclose(data2check[0][:, 3].astype(float), data2check[1][:, 3].astype(float), 1e-5)

    finally:
        # print ("empty")
        shutil.rmtree(cur_test_dir)


def test_detect_local():
    test_dir = tempfile.mkdtemp(prefix='bobtest_')
    # define dummy parameters
    parameters = [
        '-d', os.path.join(dummy_dir, 'database.py'),
        '-p', os.path.join(dummy_dir, 'preprocessor.py'),
        '-e', os.path.join(dummy_dir, 'extractor.py'),
        '-a', os.path.join(dummy_dir, 'algorithm.py'),
        '-vs', 'test_local',
        '--temp-directory', test_dir,
        '--result-directory', test_dir
    ]

    print(bob.pad.base.tools.command_line(parameters))

    _detect(parameters, test_dir, 'test_local', ('dev-real',))
    _detect(parameters, test_dir, 'test_local', ('dev-attack',))


def test_detect_resources():
    test_dir = tempfile.mkdtemp(prefix='bobtest_')
    # define dummy parameters
    parameters = [
        '-d', 'dummy',
        '-p', 'test',
        '-e', 'test',
        '-a', 'test',
        '-vs', 'test_resource',
        '--groups', ['dev', 'eval'],
        '--temp-directory', test_dir,
        '--result-directory', test_dir
    ]

    print(bob.pad.base.tools.command_line(parameters))

    _detect(parameters, test_dir, 'test_resource', ('dev-real', 'dev-attack'))
    _detect(parameters, test_dir, 'test_resource', ('eval-real', 'eval-attack'))


def test_detect_commandline():
    test_dir = tempfile.mkdtemp(prefix='bobtest_')
    # define dummy parameters
    parameters = [
        '-d', 'bob.pad.base.test.dummy.database.TestDatabase()',
        '-p', 'bob.pad.base.test.dummy.preprocessor.DummyPreprocessor()',
        '-e', 'bob.pad.base.test.dummy.extractor.DummyExtractor()',
        '-a', 'bob.pad.base.test.dummy.algorithm.DummyAlgorithm()',
        '-vs', 'test_commandline',
        '--temp-directory', test_dir,
        '--result-directory', test_dir
    ]

    print(bob.pad.base.tools.command_line(parameters))

    _detect(parameters, test_dir, 'test_commandline')


@utils.grid_available
def test_detect_parallel():
    test_dir = tempfile.mkdtemp(prefix='bobtest_')
    test_database = os.path.join(test_dir, "submitted.sql3")

    # define dummy parameters
    parameters = [
        '-d', os.path.join(dummy_dir, 'database.py'),
        '-p', 'test',
        '-e', 'bob.pad.base.test.dummy.extractor.DummyExtractor()',
        '-a', 'test',
        '-vs', 'test_parallel',
        '--temp-directory', test_dir,
        '--result-directory', test_dir,
        '-vv',
        '-g',
        'bob.bio.base.grid.Grid(grid_type = "local", number_of_parallel_processes = 2, scheduler_sleep_time = 0.1)',
        '-G', test_database, '--run-local-scheduler', '--stop-on-failure'
    ]

    print(bob.pad.base.tools.command_line(parameters))

    _detect(parameters, test_dir, 'test_parallel')


def test_detect_compressed():
    test_dir = tempfile.mkdtemp(prefix='bobtest_')
    # define dummy parameters
    parameters = [
        '-d', 'dummy',
        '-p', 'test',
        '-e', 'test',
        '-a', 'test',
        '-vs', 'test_compressed',
        '--temp-directory', test_dir,
        '--result-directory', test_dir,
        '--write-compressed-score-files'
    ]

    print(bob.bio.base.tools.command_line(parameters))

    _detect(parameters, test_dir, 'test_compressed', score_types=('dev-real', 'dev-attack'),
            scores_extension='.tar.bz2')
