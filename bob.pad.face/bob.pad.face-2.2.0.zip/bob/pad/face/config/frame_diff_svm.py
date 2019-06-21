#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This file contains configurations to run Frame Differences and SVM based face PAD baseline.
The settings are tuned for the Replay-attack database.
The idea of the algorithms is inherited from the following paper: [AM11]_.
"""

#=======================================================================================
sub_directory = 'frame_diff_svm'
"""
Sub-directory where results will be placed.

You may change this setting using the ``--sub-directory`` command-line option
or the attribute ``sub_directory`` in a configuration file loaded **after**
this resource.
"""

#=======================================================================================
# define preprocessor:

from ..preprocessor import FrameDifference

NUMBER_OF_FRAMES = None  # process all frames
MIN_FACE_SIZE = 50  # Minimal size of the face to consider

preprocessor = FrameDifference(
    number_of_frames=NUMBER_OF_FRAMES,
    min_face_size=MIN_FACE_SIZE)
"""
In the preprocessing stage the frame differences are computed for both facial and non-facial/background
regions. In this case all frames of the input video are considered, which is defined by
``number_of_frames = None``. The frames containing faces of the size below ``min_face_size = 50`` threshold
are discarded. Both RGB and gray-scale videos are acceptable by the preprocessor.
The preprocessing idea is introduced in [AM11]_.
"""

#=======================================================================================
# define extractor:

from ..extractor import FrameDiffFeatures

WINDOW_SIZE = 20
OVERLAP = 0

extractor = FrameDiffFeatures(window_size=WINDOW_SIZE, overlap=OVERLAP)
"""
In the feature extraction stage 5 features are extracted for all non-overlapping windows in
the Frame Difference input signals. Five features are computed for each of windows in the
facial face regions, the same is done for non-facial regions. The non-overlapping option
is controlled by ``overlap = 0``. The length of the window is defined by ``window_size``
argument.
The features are introduced in the following paper: [AM11]_.
"""

#=======================================================================================
# define algorithm:

from bob.pad.base.algorithm import SVM

MACHINE_TYPE = 'C_SVC'
KERNEL_TYPE = 'RBF'
N_SAMPLES = 10000
TRAINER_GRID_SEARCH_PARAMS = {
    'cost': [2**P for P in range(-3, 14, 2)],
    'gamma': [2**P for P in range(-15, 0, 2)]
}
MEAN_STD_NORM_FLAG = True  # enable mean-std normalization
FRAME_LEVEL_SCORES_FLAG = True  # one score per frame(!) in this case

algorithm = SVM(
    machine_type=MACHINE_TYPE,
    kernel_type=KERNEL_TYPE,
    n_samples=N_SAMPLES,
    trainer_grid_search_params=TRAINER_GRID_SEARCH_PARAMS,
    mean_std_norm_flag=MEAN_STD_NORM_FLAG,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)
"""
The SVM algorithm with RBF kernel is used to classify the data into *real* and *attack* classes.
One score is produced for each frame of the input video, ``frame_level_scores_flag = True``.
The grid search of SVM parameters is used to select the successful settings.
The grid search is done on the subset of training data.
The size of this subset is defined by ``n_samples`` parameter.

The data is also mean-std normalized, ``mean_std_norm_flag = True``.
"""
