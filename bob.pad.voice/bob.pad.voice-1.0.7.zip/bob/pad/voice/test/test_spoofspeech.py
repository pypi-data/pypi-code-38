#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Pavel Korshunov <pavel.korshunov@idiap.ch>
# @date: Thu Apr 28 16:41:21 CEST 2016
#



from __future__ import print_function


import os
import shutil
import tempfile
import numpy

import bob.io.base.test_utils
import bob.bio.base
import bob.pad.base
import bob.bio.spear
import bob.pad.voice

import pkg_resources

dummy_dir = pkg_resources.resource_filename('bob.pad.voice', 'test/dummy')
data_dir = pkg_resources.resource_filename('bob.pad.voice', 'test/data')


def _spoof(parameters, cur_test_dir, sub_dir, score_types=('dev-real',), scores_extension=''):
    from bob.pad.base.script.spoof import main
    try:
        main(parameters)

        # assert that the score file exists
        score_files = [os.path.join(cur_test_dir, sub_dir, 'Default', 'scores',
                                    'scores-%s%s' % (score_type, scores_extension)) for score_type in score_types]
        assert os.path.exists(score_files[0]), "Score file %s does not exist" % score_files[0]

        # also assert that the scores are still the same -- though they have no real meaning
        reference_files = [os.path.join(data_dir, sub_dir, 'scores-%s' % score_type) for score_type in score_types]

        # read reference and new data
        for i in range(0, len(score_types)):
            data2check = []
            for sfile in (score_files[i], reference_files[i]):
                f = bob.bio.base.score.load.open_file(sfile)
                d_ = []
                for line in f:
                    if isinstance(line, bytes): line = line.decode('utf-8')
                    d_.append(line.rstrip().split())
                data2check.append(numpy.array(d_))

            assert data2check[0].shape == data2check[1].shape
            # assert that the data order is still correct
            assert (data2check[0][:, 0:3] == data2check[1][:, 0:3]).all()
            # assert that the values are OK
            print (data2check)
            assert numpy.allclose(data2check[0][:, 3].astype(float), data2check[1][:, 3].astype(float), 1e-3)

    finally:
        shutil.rmtree(cur_test_dir)


def test_spoof_EnergyLBP1():
    test_dir = tempfile.mkdtemp(prefix='bobtest_')
    # define dummy parameters
    parameters = [
        '-d', 'dummy-speech',
        '-p', 'mod-4hz',
        '-e', 'lbp-hist',
        '-a', 'logregr',
        '-vs', 'test_energylbp',
        '--groups', ['dev', 'eval'],
        '--temp-directory', test_dir,
        '--result-directory', test_dir
    ]

    print(bob.pad.base.tools.command_line(parameters))

    _spoof(parameters, test_dir, 'test_energylbp', ('dev-real', 'dev-attack'))
    _spoof(parameters, test_dir, 'test_energylbp', ('eval-real', 'eval-attack'))


def test_spoof_EnergyLBP2():
    test_dir = tempfile.mkdtemp(prefix='bobtest_')
    # define dummy parameters
    parameters = [
        '-d', 'bob.pad.voice.test.dummy.database.DummyDatabaseSpeechSpoof()',
        '-p', 'bob.bio.spear.preprocessor.Mod_4Hz()',
        '-e', 'bob.pad.voice.extractor.LBPHistograms(features_processor=bob.pad.voice.extractor.SpectrogramExtended())',
        '-a', 'bob.pad.voice.algorithm.LogRegr()',
        '-vs', 'test_energylbp',
        '--temp-directory', test_dir,
        '--result-directory', test_dir
    ]

    print(bob.pad.base.tools.command_line(parameters))

    _spoof(parameters, test_dir, 'test_energylbp')
