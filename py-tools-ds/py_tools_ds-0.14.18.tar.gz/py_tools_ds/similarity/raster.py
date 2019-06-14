# -*- coding: utf-8 -*-

import numpy as np
from skimage.measure import compare_ssim as ssim

__author__ = "Daniel Scheffler"


def calc_ssim(image0, image1, dynamic_range=None, win_size=None, gaussian_weights=False):
    """Calculates Mean Structural Similarity Index between two images.

    :param image0:
    :param image1:
    :param dynamic_range:
    :param win_size:
    :param gaussian_weights:
    :return:
    """
    if image0.dtype != image1.dtype:
        image0 = image0.astype(np.int16)
        image1 = image1.astype(np.int16)

    return ssim(image0, image1, data_range=dynamic_range, win_size=win_size, gaussian_weights=gaussian_weights)
