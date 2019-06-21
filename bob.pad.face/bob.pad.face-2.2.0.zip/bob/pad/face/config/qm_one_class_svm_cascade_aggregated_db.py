#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This file contains configurations to run Image Quality Measures (IQM) and SVM based face PAD baseline.
The settings of the preprocessor and extractor are tuned for the Replay-attack database.
In the SVM algorithm the amount of training data is reduced speeding-up the training for
large data sets, such as Aggregated PAD database.
The IQM features used in this algorithm/resource are introduced in the following papers: [WHJ15]_ and [CBVM16]_.
"""

#=======================================================================================
sub_directory = 'qm_svm_aggregated_db'
"""
Sub-directory where results will be placed.

You may change this setting using the ``--sub-directory`` command-line option
or the attribute ``sub_directory`` in a configuration file loaded **after**
this resource.
"""

#=======================================================================================
# define preprocessor:

from ..preprocessor import FaceCropAlign

from bob.bio.video.preprocessor import Wrapper

from bob.bio.video.utils import FrameSelector

FACE_SIZE = 64 # The size of the resulting face
RGB_OUTPUT_FLAG = True # RGB output
USE_FACE_ALIGNMENT = False # use annotations
MAX_IMAGE_SIZE = None # no limiting here
FACE_DETECTION_METHOD = None # use annotations
MIN_FACE_SIZE = 50 # skip small faces

_image_preprocessor = FaceCropAlign(face_size = FACE_SIZE,
                                   rgb_output_flag = RGB_OUTPUT_FLAG,
                                   use_face_alignment = USE_FACE_ALIGNMENT,
                                   max_image_size = MAX_IMAGE_SIZE,
                                   face_detection_method = FACE_DETECTION_METHOD,
                                   min_face_size = MIN_FACE_SIZE)

_frame_selector = FrameSelector(selection_style = "all")

preprocessor = Wrapper(preprocessor = _image_preprocessor,
                       frame_selector = _frame_selector)
"""
In the preprocessing stage the face is cropped in each frame of the input video given facial annotations.
The size of the face is normalized to ``FACE_SIZE`` dimensions. The faces of the size
below ``MIN_FACE_SIZE`` threshold are discarded. The preprocessor is similar to the one introduced in
[CAM12]_, which is defined by ``FACE_DETECTION_METHOD = None``. The preprocessed frame is the RGB
facial image, which is defined by ``RGB_OUTPUT_FLAG = True``.
"""

#=======================================================================================
# define extractor:

from ..extractor import ImageQualityMeasure

from bob.bio.video.extractor import Wrapper

GALBALLY = True
MSU = True
DTYPE = None

extractor = Wrapper(ImageQualityMeasure(galbally=GALBALLY, msu=MSU, dtype=DTYPE))
"""
In the feature extraction stage the Image Quality Measures are extracted from each frame of the preprocessed RGB video.
The features to be computed are introduced in the following papers: [WHJ15]_ and [CBVM16]_.
"""

#=======================================================================================
# define algorithm:

from bob.pad.base.algorithm import SVMCascadePCA

MACHINE_TYPE = 'ONE_CLASS'
KERNEL_TYPE = 'RBF'
SVM_KWARGS = {'nu': 0.001, 'gamma': 0.5}
N = 2
POS_SCORES_SLOPE = 0.01
FRAME_LEVEL_SCORES_FLAG = True

algorithm = SVMCascadePCA(
    machine_type=MACHINE_TYPE,
    kernel_type=KERNEL_TYPE,
    svm_kwargs=SVM_KWARGS,
    N=N,
    pos_scores_slope=POS_SCORES_SLOPE,
    frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)
"""
The cascade of one-class SVMs with RBF kernel is used to classify the data into *real* and *attack* classes.
One score is produced for each frame of the input video, ``frame_level_scores_flag = True``.
A single SVM in the cascade is trained using two features ``N = 2``.
The positive scores produced by the cascade are reduced by multiplying them with a constant
``pos_scores_slope = 0.01``.
"""
