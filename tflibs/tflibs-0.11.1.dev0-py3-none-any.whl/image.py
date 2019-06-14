"""
    Image utils
    ~~~~~~~~~~~
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import cv2
import numpy as np


def encode(arr, ext='.png'):
    """
    Encodes numpy.ndarray into string

    :param numpy.ndarray arr: numpy.ndarray of an image
    :param ext:
    :return: encoded string
    :rtype: str
    """
    return cv2.imencode(ext, arr[:, :, ::-1])[1].tostring()


def decode(string):
    """
    Decodes jpeg string into numpy.ndarray

    :param str string: jpeg encoded string
    :return: numpy.ndarray of a decoded image
    :rtype: numpy.ndarray
    """
    return cv2.imdecode(np.fromstring(string, np.uint8), cv2.IMREAD_COLOR)[:, :, ::-1]


def resize(img, dsize):
    """
    Resizes numpy.ndarray image to target size

    :param numpy.ndarray img: numpy.ndarray of an image
    :param tuple dsize: Target size (height, width)
    :return: Resized image
    :rtype: numpy.ndarray
    """
    (height, width) = dsize

    return cv2.resize(img, dsize=(height, width))
