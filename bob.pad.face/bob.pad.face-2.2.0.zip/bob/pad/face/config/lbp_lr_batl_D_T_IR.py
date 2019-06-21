#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This file contains configurations to run LBP and SVM based face PAD baseline.
The settings are tuned for the Replay-attack database.
The idea of the algorithm is introduced in the following paper: [CAM12]_.
However some settings are different from the ones introduced in the paper.
"""

#=======================================================================================
sub_directory = 'lbp_svm'
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

from ..preprocessor.FaceCropAlign import auto_norm_image as _norm_func

FACE_SIZE = 64 # The size of the resulting face
RGB_OUTPUT_FLAG = False # Gray-scale output
USE_FACE_ALIGNMENT = False # use annotations
MAX_IMAGE_SIZE = None # no limiting here
FACE_DETECTION_METHOD = None # use annotations
MIN_FACE_SIZE = 50 # skip small faces
NORMALIZATION_FUNCTION = _norm_func
NORMALIZATION_FUNCTION_KWARGS = {}
NORMALIZATION_FUNCTION_KWARGS = {'n_sigma':3.0, 'norm_method':'MAD'}

_image_preprocessor = FaceCropAlign(face_size = FACE_SIZE,
                                   rgb_output_flag = RGB_OUTPUT_FLAG,
                                   use_face_alignment = USE_FACE_ALIGNMENT,
                                   max_image_size = MAX_IMAGE_SIZE,
                                   face_detection_method = FACE_DETECTION_METHOD,
                                   min_face_size = MIN_FACE_SIZE,
                                   normalization_function = NORMALIZATION_FUNCTION,
                                   normalization_function_kwargs = NORMALIZATION_FUNCTION_KWARGS)

_frame_selector = FrameSelector(selection_style = "all")

preprocessor = Wrapper(preprocessor = _image_preprocessor,
                       frame_selector = _frame_selector)
"""
In the preprocessing stage the face is cropped in each frame of the input video given facial annotations.
The size of the face is normalized to ``FACE_SIZE`` dimensions. The faces with the size
below ``MIN_FACE_SIZE`` threshold are discarded. The preprocessor is similar to the one introduced in
[CAM12]_, which is defined by ``FACE_DETECTION_METHOD = None``.
"""

#=======================================================================================
# define extractor:

from ..extractor import LBPHistogram

from bob.bio.video.extractor import Wrapper

LBPTYPE = 'uniform'
ELBPTYPE = 'regular'
RAD = 1
NEIGHBORS = 8
CIRC = False
DTYPE = None

extractor = Wrapper(LBPHistogram(
    lbptype=LBPTYPE,
    elbptype=ELBPTYPE,
    rad=RAD,
    neighbors=NEIGHBORS,
    circ=CIRC,
    dtype=DTYPE))
"""
In the feature extraction stage the LBP histograms are extracted from each frame of the preprocessed video.

The parameters are similar to the ones introduced in [CAM12]_.
"""

#=======================================================================================
# define algorithm:

from bob.pad.base.algorithm import LogRegr

C = 1.  # The regularization parameter for the LR classifier
FRAME_LEVEL_SCORES_FLAG = True  # Return one score per frame

algorithm = LogRegr(
    C=C, frame_level_scores_flag=FRAME_LEVEL_SCORES_FLAG)
"""
The Logistic Regression is used to classify the data into *real* and *attack* classes.
One score is produced for each frame of the input video, ``frame_level_scores_flag = True``.
The sub-sampling of training data is not used here, sub-sampling flags have default ``False``
values.
"""
