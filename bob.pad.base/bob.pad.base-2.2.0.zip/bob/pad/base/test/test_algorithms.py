#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#

from __future__ import print_function

import numpy as np

import bob.io.image  # for image loading functionality
import bob.bio.video
import bob.pad.base

from bob.pad.base.algorithm import SVM
from bob.pad.base.algorithm import OneClassGMM
from bob.pad.base.algorithm import MLP
from bob.pad.base.algorithm import PadLDA

import random

from bob.pad.base.utils import (
    convert_array_to_list_of_frame_cont,
    convert_list_of_frame_cont_to_array,
    convert_frame_cont_to_array
)

from bob.pad.base.database import PadFile
from bob.pad.base.algorithm import Predictions
from bob.pad.base import padfile_to_label


def test_prediction():
    alg = Predictions()
    sample = [0, 1]
    assert alg.score(sample)[0] == sample[1]


def test_padfile_to_label():
    f = PadFile(client_id='', path='', attack_type=None, file_id=1)
    assert padfile_to_label(f) is True, padfile_to_label(f)
    f = PadFile(client_id='', path='', attack_type='print', file_id=1)
    assert padfile_to_label(f) is False, padfile_to_label(f)


def test_video_svm_pad_algorithm():

    random.seed(7)

    N = 20000
    mu = 1
    sigma = 1
    real_array = np.transpose(
        np.vstack([[random.gauss(mu, sigma) for _ in range(N)],
                   [random.gauss(mu, sigma) for _ in range(N)]]))

    mu = 5
    sigma = 1
    attack_array = np.transpose(
        np.vstack([[random.gauss(mu, sigma) for _ in range(N)],
                   [random.gauss(mu, sigma) for _ in range(N)]]))

    real = convert_array_to_list_of_frame_cont(real_array)
    attack = convert_array_to_list_of_frame_cont(attack_array)

    training_features = [real, attack]

    MACHINE_TYPE = 'C_SVC'
    KERNEL_TYPE = 'RBF'
    N_SAMPLES = 1000
    TRAINER_GRID_SEARCH_PARAMS = {'cost': [1], 'gamma': [0.5, 1]}
    MEAN_STD_NORM_FLAG = True  # enable mean-std normalization
    FRAME_LEVEL_SCORES_FLAG = True  # one score per frame(!) in this case

    algorithm = SVM(
        machine_type=MACHINE_TYPE,
        kernel_type=KERNEL_TYPE,
        n_samples=N_SAMPLES,
        trainer_grid_search_params=TRAINER_GRID_SEARCH_PARAMS,
        mean_std_norm_flag=MEAN_STD_NORM_FLAG,
        frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

    machine = algorithm.train_svm(
        training_features=training_features,
        n_samples=algorithm.n_samples,
        machine_type=algorithm.machine_type,
        kernel_type=algorithm.kernel_type,
        trainer_grid_search_params=algorithm.trainer_grid_search_params,
        mean_std_norm_flag=algorithm.mean_std_norm_flag,
        projector_file="",
        save_debug_data_flag=False)

    assert machine.n_support_vectors == [148, 150]
    assert machine.gamma == 0.5

    real_sample = convert_frame_cont_to_array(real[0])

    prob = machine.predict_class_and_probabilities(real_sample)[1]

    assert prob[0, 0] > prob[0, 1]

    precision = algorithm.comp_prediction_precision(machine, real_array,
                                                    attack_array)

    assert precision > 0.99


def test_video_gmm_pad_algorithm():

    random.seed(7)

    N = 1000
    mu = 1
    sigma = 1
    real_array = np.transpose(
        np.vstack([[random.gauss(mu, sigma) for _ in range(N)],
                   [random.gauss(mu, sigma) for _ in range(N)]]))

    mu = 5
    sigma = 1
    attack_array = np.transpose(
        np.vstack([[random.gauss(mu, sigma) for _ in range(N)],
                   [random.gauss(mu, sigma) for _ in range(N)]]))

    real = convert_array_to_list_of_frame_cont(real_array)

    N_COMPONENTS = 1
    RANDOM_STATE = 3
    FRAME_LEVEL_SCORES_FLAG = True

    algorithm = OneClassGMM(
        n_components=N_COMPONENTS,
        random_state=RANDOM_STATE,
        frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)

    # training_features[0] - training features for the REAL class.
    real_array_converted = convert_list_of_frame_cont_to_array(real)  # output is array

    assert (real_array == real_array_converted).all()

    # Train the OneClassGMM machine and get normalizers:
    machine, features_mean, features_std = algorithm.train_gmm(
        real=real_array_converted)

    algorithm.machine = machine

    algorithm.features_mean = features_mean

    algorithm.features_std = features_std

    scores_real = algorithm.project(real_array_converted)

    scores_attack = algorithm.project(attack_array)

    assert (np.min(scores_real) + 7.9423798970985917) < 0.000001
    assert (np.max(scores_real) + 1.8380480068281055) < 0.000001
    assert (np.min(scores_attack) + 38.831260843070098) < 0.000001
    assert (np.max(scores_attack) + 5.3633030621521272) < 0.000001


def test_convert_list_of_frame_cont_to_array():

  N = 1000
  mu = 1
  sigma = 1
  real_array = np.transpose(np.vstack([[random.gauss(mu, sigma) for _ in range(N)], [random.gauss(mu, sigma) for _ in range(N)]]))

  features_array = convert_list_of_frame_cont_to_array(real_array)
  assert isinstance(features_array[0], np.ndarray)
  features_fm = convert_array_to_list_of_frame_cont(real_array)
  assert isinstance(features_fm[0], bob.bio.video.FrameContainer)


def test_MLP():

    random.seed(7)

    N = 20000
    mu = 1
    sigma = 1
    real_array = np.transpose(
        np.vstack([[random.gauss(mu, sigma) for _ in range(N)],
                   [random.gauss(mu, sigma) for _ in range(N)]]))

    mu = 5
    sigma = 1
    attack_array = np.transpose(
        np.vstack([[random.gauss(mu, sigma) for _ in range(N)],
                   [random.gauss(mu, sigma) for _ in range(N)]]))


    training_features = [real_array, attack_array]

    mlp = MLP(max_iter=100)
    mlp.train_projector(training_features, '/tmp/mlp.hdf5')

    real_sample = real_array[0]
    prob = mlp.project(real_sample)
    assert prob[0] > prob[1]


def test_LDA():

    random.seed(7)

    N = 20000
    mu = 1
    sigma = 1
    real_array = np.transpose(
        np.vstack([[random.gauss(mu, sigma) for _ in range(N)],
                   [random.gauss(mu, sigma) for _ in range(N)]]))

    mu = 5
    sigma = 1
    attack_array = np.transpose(
        np.vstack([[random.gauss(mu, sigma) for _ in range(N)],
                   [random.gauss(mu, sigma) for _ in range(N)]]))

    training_features = [real_array, attack_array]

    lda = PadLDA()
    lda.train_projector(training_features, '/tmp/lda.hdf5')
    assert lda.machine.shape == (2, 1)
