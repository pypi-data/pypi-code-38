#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quality assessment configuration file for the CelebA database to be used
with quality assessment script.

Note: this config checks the quality of the preprocessed(!) data. Here the
preprocessed data is sored in ``.hdf5`` files, as a frame container with
one frame. Frame contains a BW image of the facial regions of the size
128x128 pixels.

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

import bob.ip.color

# =============================================================================
def detect_eyes_in_bw_image(image):
    """
    Detect eyes in the image using OpenCV.

    **Parameters:**

    ``image`` : 2D :py:class:`numpy.ndarray`
        A BW image to detect the eyes in.

    **Returns:**

    ``eyes`` : 2D :py:class:`numpy.ndarray`
        An array containing coordinates of the bounding boxes of detected eyes.
        The dimensionality of the array:
        ``num_of_detected_eyes x coordinates_of_bbx``
    """

    eye_model = pkg_resources.resource_filename('bob.pad.face.config',
                                                'quality_assessment/models/eye_detector.xml')

    eye_cascade = cv2.CascadeClassifier(eye_model)

    if len(image.shape) == 3:

        image = bob.ip.color.rgb_to_gray(image)

    eyes = eye_cascade.detectMultiScale(image)

    return eyes


# =============================================================================
def load_datafile(file_name):
    """
    Load data from file given filename. Here the data file is an hdf5 file
    containing a framecontainer with one frame. The data in the frame is
    a BW image of the facial region.

    **Parameters:**

    ``file_name`` : str
        Absolute name of the file.

    **Returns:**

    ``data`` : 2D :py:class:`numpy.ndarray`
        Data array containing the image of the facial region.
    """

    frame_container = Wrapper().read_data(file_name)

    data = frame_container[0][1]

    return data


# =============================================================================
face_size = 128
eyes_distance=((face_size + 1) / 2.)
eyes_center=(face_size / 4., (face_size - 0.5) / 2.)

eyes_expected = [[eyes_center[0], eyes_center[1]-eyes_distance/2.],
                 [eyes_center[0], eyes_center[1]+eyes_distance/2.]]

assess_quality_kwargs = {}
assess_quality_kwargs["eyes_expected"] = eyes_expected
assess_quality_kwargs["threshold"] = 10


# =============================================================================
def assess_quality(data, eyes_expected, threshold):
    """
    Assess the quality of the data sample, which in this case is an image of
    the face of the size (face_size x face_size) pixels. The quality assessment is based on the
    eye detection. If two eyes are detected, and they are located in the
    pre-defined positions, then quality is good, otherwise the quality is low.

    **Parameters:**

    ``data`` : 2D :py:class:`numpy.ndarray`
        Data array containing the image of the facial region. The size of the
        image is (face_size x face_size).

    ``eyes_expected`` : list
        A list containing expected coordinates of the eyes. The format is
        as follows:
        [ [left_y, left_x], [right_y, right_x] ]

    ``threshold`` : int
        A maximum allowed distance between expected and detected centers of
        the eyes.

    **Returns:**

    ``quality_flag`` : bool
        ``True`` for good quality data, ``False`` otherwise.
    """

    quality_flag = False

    eyes = detect_eyes_in_bw_image(data)

    if isinstance(eyes, np.ndarray):

        if eyes.shape[0] == 2: # only consider the images with two eyes detected

            # coordinates of detected centers of the eyes: [ [left_y, left_x], [right_y, right_x] ]:
            eyes_detected = []
            for (ex,ey,ew,eh) in eyes:
                eyes_detected.append( [ey + eh/2., ex + ew/2.] )

            dists = [] # dits between detected and expected:
            for a, b in zip(eyes_detected, eyes_expected):
                dists.append( np.linalg.norm(np.array(a)-np.array(b)) )

            max_dist = np.max(dists)

            if max_dist < threshold:

                quality_flag = True

    return quality_flag


