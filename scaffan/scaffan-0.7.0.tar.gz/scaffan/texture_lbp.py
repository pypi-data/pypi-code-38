# /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Modul is used for texrure analysis.
"""

from loguru import logger
import numpy as np
import skimage.feature
import matplotlib.pyplot as plt

# settings for LBP
radius = 2
n_points = 8 * radius
method = "uniform"


def kullback_leibler_divergence(p, q):
    p = np.asarray(p)
    q = np.asarray(q)
    filt = np.logical_and(p != 0, q != 0)
    return np.sum(p[filt] * np.log2(p[filt] / q[filt]))


def lbp_fv(img):  # , n_points, radius, METHOD):
    """

    :param img: img in range 0.0-1.0
    :return:
    """
    img = (img * 255).astype(np.uint8)
    lbp = skimage.feature.local_binary_pattern(img, n_points, radius, method)
    n_bins = int(lbp.max() + 1)
    hist, _ = np.histogram(lbp, density=True, bins=n_bins, range=(0, n_bins))
    return hist


# def match(refs, img):
#     best_score = 10
#     best_name = None
#     if type(refs) is dict:
#         itms = refs.items()
#     elif type(refs) is list:
#         itms = refs
#     else:
#         ValueError("Wrong type for 'refs'")
#
#     for name, ref in itms:
#         ref_hist, _ = np.histogram(ref, density=True, bins=n_bins,
#                                    range=(0, n_bins))
#         score = kullback_leibler_divergence(hist, ref_hist)
#         if score < best_score:
#             best_score = score
#             best_name = name
#     return best_name


def show_lbp(lbp):
    n_bins = int(lbp.max() + 1)
    plt.hist(lbp.ravel(), range=(0, n_bins), bins=n_bins, normed=True)
    plt.xlim(xmax=n_points + 2)


class KLDClassifier:
    def __init__(self):
        pass

    def fit(self, data, target):

        self.data = data
        self.target = target
        # self.refs = list(zip(data, target))
        pass

    def predict_one(self, hist):
        best_score = np.inf
        for name, ref_hist in zip(self.target, self.data):
            score = kullback_leibler_divergence(hist, ref_hist)
            if score < best_score:
                best_score = score
                best_name = name
        return best_name

    def predict(self, x):
        out = [None] * len(x)
        for i, hist in enumerate(x):
            out[i] = self.predict_one(hist)

        return out
