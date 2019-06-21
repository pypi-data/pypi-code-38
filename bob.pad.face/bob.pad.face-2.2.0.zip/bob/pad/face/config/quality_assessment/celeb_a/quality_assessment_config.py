#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quality assessment configuration file for the CelebA database to be used
with quality assessment script.

Note: this config checks the quality of the preprocessed(!) data. Here the
preprocessed data is sored in ``.hdf5`` files, as a frame container with
one frame. Frame contains a BW image of the facial regions of the size
64x64 pixels.

The config file MUST contain at least the following functions:

``load_datafile(file_name)`` - returns the ``data`` given ``file_name``, and

``assess_quality(data, **assess_quality_kwargs)`` - returns ``True`` for good
quality ``data``, and ``False`` for low quality data, and

``assess_quality_kwargs`` - a dictionary with kwargs for ``assess_quality()``
function.

@author: Olegs Nikisins
"""

# =============================================================================
# Import here:

import pkg_resources

import cv2

from bob.bio.video.preprocessor import Wrapper

import numpy as np

from bob.pad.face.config.quality_assessment.celeb_a.quality_assessment_config_128 import detect_eyes_in_bw_image, load_datafile, assess_quality


# =============================================================================
face_size = 64
eyes_distance=((face_size + 1) / 2.)
eyes_center=(face_size / 4., (face_size - 0.5) / 2.)

eyes_expected = [[eyes_center[0], eyes_center[1]-eyes_distance/2.],
                 [eyes_center[0], eyes_center[1]+eyes_distance/2.]]

assess_quality_kwargs = {}
assess_quality_kwargs["eyes_expected"] = eyes_expected
assess_quality_kwargs["threshold"] = 7

