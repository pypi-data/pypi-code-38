#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""Test Units
"""
import numpy as np

from .. import FaceDetector
import pkg_resources
import bob.io.base

def test_face_detector():
    """
    Test FaceDetector class.
    """

    image = np.zeros((3, 100, 100))
    result = FaceDetector().detect_single_face(image)
    assert result is None

    image = np.ones((3, 100, 100))
    result = FaceDetector().detect_single_face(image)
    assert result is None

    # test on the actual image:
    test_file = pkg_resources.resource_filename('bob.ip.dlib', 'data/test_image.hdf5')
    f = bob.io.base.HDF5File(test_file) #read only
    image = f.read('image') #reads integer
    del f

    result = FaceDetector().detect_single_face(image)
    assert result[0].topleft == (0, 237)
    assert result[0].bottomright == (84, 313)


def test_landmark():
    """
    Test Landmarks
    """

    # test on the actual image:
    test_file = bob.io.base.load(pkg_resources.resource_filename('bob.ip.dlib', 'data/test_image.hdf5'))

    # Testing bob landmarks
    detector = bob.ip.dlib.DlibLandmarkExtraction(bob_landmark_format=False)
    points_dlib = detector(test_file)
    assert len(points_dlib) == 68

    # Testing bob landmarks
    detector = bob.ip.dlib.DlibLandmarkExtraction(bob_landmark_format=True)
    points_dlib = detector(test_file)
    assert all([p in ['leye', 'reye', 'nose', 'mouthleft', 'mouthright'] for p in points_dlib])
    # leye x must be higher than reye y to conform to Bob format
    assert points_dlib['leye'][1] > points_dlib['reye'][1]
