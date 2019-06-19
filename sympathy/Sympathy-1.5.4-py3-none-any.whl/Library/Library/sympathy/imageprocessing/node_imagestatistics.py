# Copyright (c) 2017, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
Some of the docstrings for this module have been
extracted from the `scikit-image <http://scikit-image.org/>`_ library
and are covered by their respective licenses.
"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
from sympathy.api import node
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api.exceptions import sywarn
import numpy as np
from skimage import feature, exposure, transform
from sylib.imageprocessing.image import Image
from sylib.imageprocessing.algorithm_selector import (
    ImageFiltering_abstract)


def alg_cdf(im, params, result):
    result.set_name("Cumulative Distribution Function")
    channels = 1 if len(im.shape) < 3 else im.shape[2]
    for channel in range(channels):
        cdf, bins = exposure.cumulative_distribution(
            im[:, :, channel], nbins=params['bins'].value)
        result.set_column_from_array("{0}_cdf".format(channel), cdf)
        result.set_column_from_array("{0}_bins".format(channel), bins)


def alg_histogram(im, params, result):
    result.set_name("Histogram")
    channels = 1 if len(im.shape) < 3 else im.shape[2]
    for channel in range(channels):
        hist, bins = np.histogram(
            im[:, :, channel], bins=params['bins'].value,
            range=(params['min value'].value, params['max value'].value))
        # hist, bins = exposure.histogram(
        #     im[:, :, channel].astype(float), nbins=params['bins'].value)
        result.set_column_from_array("{0}_hist".format(channel), hist)
        result.set_column_from_array("{0}_bins".format(channel), bins[1:])


def alg_blob_dog(im, params, result):
    result.set_name("Blobs")
    if len(im.shape) == 3:
        im = im[:, :, 0]
    A = feature.blob_dog(im,
                         min_sigma=params['min sigma'].value,
                         max_sigma=params['max sigma'].value,
                         sigma_ratio=params['sigma_ratio'].value,
                         threshold=params['threshold'].value,
                         overlap=params['overlap'].value)
    if len(A.shape) < 2:
        result.set_column_from_array("Y", np.array([]))
        result.set_column_from_array("X", np.array([]))
        result.set_column_from_array("sigma", np.array([]))
    else:
        result.set_column_from_array("Y", A[:, 0])
        result.set_column_from_array("X", A[:, 1])
        result.set_column_from_array("sigma", A[:, 2])


def alg_blob_doh(im, params, result):
    result.set_name("Blobs")
    if len(im.shape) == 3:
        im = im[:, :, 0]
    A = feature.blob_doh(im,
                         min_sigma=params['min sigma'].value,
                         max_sigma=params['max sigma'].value,
                         num_sigma=params['num sigma'].value,
                         threshold=params['threshold'].value,
                         log_scale=params['log scale'].value,
                         overlap=params['overlap'].value)
    if len(A.shape) < 2:
        result.set_column_from_array("Y", np.array([]))
        result.set_column_from_array("X", np.array([]))
        result.set_column_from_array("sigma", np.array([]))
    else:
        result.set_column_from_array("Y", A[:, 0])
        result.set_column_from_array("X", A[:, 1])
        result.set_column_from_array("sigma", A[:, 2])


def alg_blob_log(im, params, result):
    result.set_name("Blobs")
    if len(im.shape) == 3:
        im = im[:, :, 0]
    A = feature.blob_log(im,
                         min_sigma=params['min sigma'].value,
                         max_sigma=params['max sigma'].value,
                         num_sigma=params['num sigma'].value,
                         threshold=params['threshold'].value,
                         log_scale=params['log scale'].value,
                         overlap=params['overlap'].value)
    if len(A.shape) < 2:
        result.set_column_from_array("Y", np.array([]))
        result.set_column_from_array("X", np.array([]))
        result.set_column_from_array("sigma", np.array([]))
    else:
        result.set_column_from_array("Y", A[:, 0])
        result.set_column_from_array("X", A[:, 1])
        result.set_column_from_array("sigma", A[:, 2])


def alg_corner_peaks(im, params, result):
    result.set_name("Peaks")
    if len(im.shape) == 3:
        im = im[:, :, 0]
    A = feature.corner_peaks(im,
                             min_distance=params['min distance'].value,
                             threshold_rel=params['threshold'].value)
    if len(A.shape) < 2:
        result.set_column_from_array("Y", np.array([]))
        result.set_column_from_array("X", np.array([]))
        result.set_column_from_array("intensity", np.array([]))
    else:
        result.set_column_from_array("Y", A[:, 0])
        result.set_column_from_array("X", A[:, 1])
        result.set_column_from_array("intensity", im[A[:, 0], A[:, 1]])


def alg_peak_local_max(im, params, result):
    result.set_name("Peaks")
    if len(im.shape) == 3:
        im = im[:, :, 0]
    A = feature.peak_local_max(
        im,
        min_distance=params['min distance'].value,
        threshold_abs=params['threshold'].value,
        threshold_rel=params['threshold relative'].value)
    if len(A.shape) < 2:
        result.set_column_from_array("Y", np.array([]))
        result.set_column_from_array("X", np.array([]))
        result.set_column_from_array("intensity", np.array([]))
    else:
        result.set_column_from_array("Y", A[:, 0])
        result.set_column_from_array("X", A[:, 1])
        result.set_column_from_array("intensity", im[A[:, 0], A[:, 1]])


def alg_daisy(im, params, result):
    result.set_name("Features")
    if len(im.shape) == 3:
        im = im[:, :, 0]
    A = feature.daisy(im,
                      step=params['step'].value,
                      radius=params['radius'].value,
                      rings=params['rings'].value,
                      histograms=params['histograms'].value,
                      orientations=params['orientations'].value,
                      normalization=params['daisy normalization'].value)
    xx, yy = np.meshgrid(np.arange(A.shape[1]), np.arange(A.shape[0]))
    xx_cor = xx * params['step'].value + params['radius'].value
    yy_cor = yy * params['step'].value + params['radius'].value
    result.set_column_from_array("X", xx_cor.ravel())
    result.set_column_from_array("Y", yy_cor.ravel())
    for f in range(A.shape[2]):
        result.set_column_from_array(
            "f{0}".format(f), A[yy.ravel(), xx.ravel(), f])


def alg_prob_hough_lines(im, params, result):
    threshold = params['threshold'].value
    int_threshold = int(round(threshold))

    if abs(threshold - float(int_threshold)) > 1e-6:
        sywarn('Threshold parameters requires an integer value. '
               'Using rounding value: {} instead of original: {}.'.format(
                   int_threshold, threshold))

    result.set_name("Lines")
    if len(im.shape) > 2:
        im = im[:, :, 0]
    lines = transform.probabilistic_hough_line(
        im,
        threshold=int_threshold,
        line_length=params['line length'].value,
        line_gap=params['line gap'].value,
        theta=np.linspace(
            params['min theta'].value,
            params['max theta'].value, params['num theta'].value))
    x0s = [start[0] for start, end in lines]
    y0s = [start[1] for start, end in lines]
    x1s = [end[0] for start, end in lines]
    y1s = [end[1] for start, end in lines]
    result.set_column_from_array("x0", np.array(x0s))
    result.set_column_from_array("y0", np.array(y0s))
    result.set_column_from_array("x1", np.array(x1s))
    result.set_column_from_array("y1", np.array(y1s))


def alg_information(im, params, result):
    prefix = params['prefix'].value
    result.set_name("Information")
    result.set_column_from_array("{0}width".format(prefix),
                                 np.array([im.shape[1]]))
    result.set_column_from_array("{0}height".format(prefix),
                                 np.array([im.shape[0]]))
    channels = im.shape[2] if len(im.shape) == 3 else 1
    result.set_column_from_array("{0}channels".format(prefix),
                                 np.array([channels]))
    for c in range(channels):
        result.set_column_from_array("{0}min_ch{1}".format(prefix, c),
                                     np.array([np.min(im[:, :, c])]))
        result.set_column_from_array("{0}max_ch{1}".format(prefix, c),
                                     np.array([np.max(im[:, :, c])]))
        result.set_column_from_array("{0}sum_ch{1}".format(prefix, c),
                                     np.array([np.sum(im[:, :, c])]))


def alg_orb(im, params, result):
    result.set_name("Features")
    if len(im.shape) == 3:
        im = im[:, :, 0]
    orb = feature.ORB(n_keypoints=params['N'].value,
                      fast_n=params['fast n'].value,
                      fast_threshold=params['fast threshold'].value,
                      harris_k=params['harris k'].value,
                      downscale=params['downscale'].value)
    orb.detect_and_extract(im)
    descriptors = orb.descriptors
    keypoints = orb.keypoints
    result.set_column_from_array('X', keypoints[:, 1]*1)
    result.set_column_from_array('Y', keypoints[:, 0]*1)
    for i in range(descriptors.shape[1]):
        result.set_column_from_array('f{}'.format(i), descriptors[:, i]*1)


def alg_censur(im, params, result):
    result.set_name("Features")
    if len(im.shape) == 3:
        im = im[:, :, 0]
    orb = feature.CENSURE(min_scale=params['min scale'].value,
                          max_scale=params['max scale'].value,
                          mode=params['censure mode'].value,
                          non_max_threshold=params['non max threshold'].value,
                          line_threshold=params['line threshold'].value)
    orb.detect(im)
    keypoints = orb.keypoints
    scales = orb.keypoints
    result.set_column_from_array('X', keypoints[:, 1])
    result.set_column_from_array('Y', keypoints[:, 0])
    result.set_column_from_array('scale', scales[:, 0])


def alg_censur_daisy(im, params, result):
    result.set_name("Features")
    if len(im.shape) == 3:
        im = im[:, :, 0]
    daisy = feature.daisy(im,
                          step=params['step'].value,
                          radius=params['radius'].value,
                          rings=params['rings'].value,
                          histograms=params['histograms'].value,
                          orientations=params['orientations'].value,
                          normalization=params['daisy normalization'].value)

    orb = feature.CENSURE(min_scale=params['min scale'].value,
                          max_scale=params['max scale'].value,
                          mode=params['censure mode'].value,
                          non_max_threshold=params['non max threshold'].value,
                          line_threshold=params['line threshold'].value)
    orb.detect(im)

    step = params['step'].value
    radius = params['radius'].value
    keypoints = orb.keypoints
    scales = orb.scales

    Xs = keypoints[:, 1]
    Ys = keypoints[:, 0]

    DXs = np.clip(np.array(np.round((Xs - radius) / step), dtype=int),
                  0, daisy.shape[1]-1)
    DYs = np.clip(np.array(np.round((Ys - radius) / step), dtype=int),
                  0, daisy.shape[0]-1)
    features = daisy[DYs, DXs, :]
    result.set_column_from_array('X', keypoints[:, 1])
    result.set_column_from_array('Y', keypoints[:, 0])
    result.set_column_from_array('scale', scales)
    for f in range(daisy.shape[2]):
        result.set_column_from_array(
            "f{0}".format(f), features[:, f])


class ImageStatistics(ImageFiltering_abstract, node.Node):
    name = 'Image Statistics'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'image_to_table.svg'
    description = (
        'Extracts tabular data from an image using one of a selection of '
        'algorithms. The implemented filters are to a large extent based on '
        '`scikit-image`, but some filters are not from this package.')
    nodeid = 'syip.imagestatistics'
    tags = Tags(Tag.ImageProcessing.Extract)

    algorithms = {
        'cdf': {
            'description': (
                'Computes the cumulative distribution function (cdf) over all '
                'pixels.\nReturns cdf value and bin-center for a number of '
                'bins. Processes each channel separately and returns separate '
                'columns'),
            'bins': 'Number of bins for processing',
            'algorithm': alg_cdf},
        'histogram': {
            'description': (
                'Computes the histogram over all pixels.\nReturns histogram '
                'count and bin-center for a number of bins. Processes each '
                'channel separately and returns separate columns'),
            'bins': 'Number of bins for processing',
            'min value': 'Lower end of range for bins',
            'max value': 'Upper end of range for bins',
            'algorithm': alg_histogram
        },
        'blob, DoG': {
            'description': (
                'Detects blobs in a grayscale image using the Difference of '
                'Gaussians (DoG) method. Returns table with X,Y positions\n'
                'and the standard deviation of the gaussian kernel that '
                'detected each blob. Operates only on first channel of image.'
                '\nThe radius of each blob is approximately sqrt(2) sigma. '
                'Operates only on first channel of image'),
            'min sigma': (
                'Minimum standard deviation for Gaussian kernels. Keep low to '
                'detect smaller blobs (default 1)'),
            'max sigma': (
                'Maximum standard deviation for Gaussian kernels. Keep high '
                'to detect larger blobs (default 50)'),
            'sigma_ratio': (
                'The ratio between the standard deviation of Gaussian Kernels '
                'used for computing the Difference of Gaussians (default 1.6)'
            ),
            'threshold': (
                'The absolute lower bound for scale space maxima. Local '
                'maxima smaller than thresh are ignored. Reduce this to '
                'detect blobs with less intensities. (default 2.0)'),
            'overlap': (
                'A value between 0 and 1. If the area of two blobs overlaps '
                'by a fraction greater than threshold, the smaller blob is '
                'eliminated. (default 0.5)'),
            'algorithm': alg_blob_dog
        },
        'blob, DoH': {
            'description': (
                'Detects blobs in a grayscale image using the Determinant of '
                'Hessian (DoH) method. Returns table with X,Y positions\nand '
                'the standard deviation of the gaussian kernel used for the '
                'hessian matrix which detected each blob.\nThe radius of each '
                'blob is approximately sigma. Operates only on first channel '
                'of image'),
            'min sigma': (
                'Minimum standard deviation for Gaussian kernels. '
                'Keep low to detect smaller blobs (default 1)'),
            'max sigma': (
                'Maximum standard deviation for Gaussian kernels. Keep high '
                'to detect larger blobs (default 50)'),
            'num sigma': (
                'The number of intermediate values for Sigma to consider '
                '(default 10)'),
            'threshold': (
                'The absolute lower bound for scale space maxima. Local '
                'maxima smaller than thresh are ignored. Reduce this to '
                'detect blobs with less intensities. (default 0.01)'),
            'overlap': (
                'A value between 0 and 1. If the area of two blobs overlaps '
                'by a fraction greater than threshold, the smaller blob is '
                'eliminated. (default 0.5)'),
            'log scale': (
                'If true then interpolation of intermediate values for '
                'Sigma are interpolated in a logrithmic scale, otherwise '
                'linear interpolation is used'),
            'algorithm': alg_blob_doh
        },
        'blob, LoG': {
            'description': (
                'Detects blobs in a grayscale image using the Laplacian of '
                'Gaussian method. Returns table with X,Y positions\nand the '
                'standard deviation of the gaussian kernel used for detecting '
                'each blob.\nThe radius of each blob is approximately sqrt(2) '
                'sigma. Operates only on first channel of image'),
            'min sigma': (
                'Minimum standard deviation for Gaussian kernels. Keep low to '
                'detect smaller blobs (default 1)'),
            'max sigma': (
                'Maximum standard deviation for Gaussian kernels. Keep high '
                'to detect larger blobs (default 50)'),
            'num sigma': (
                'The number of intermediate values for Sigma to consider '
                '(default 10)'),
            'threshold': (
                'The absolute lower bound for scale space maxima. Local '
                'maxima smaller than thresh are ignored. Reduce this to '
                'detect blobs with less intensities. (default 0.2)'),
            'overlap': (
                'A value between 0 and 1. If the area of two blobs overlaps '
                'by a fraction greater than threshold, the smaller blob is '
                'eliminated. (default 0.5)'),
            'log scale': (
                'If true then interpolation of intermediate values for Sigma '
                'are interpolated in a logrithmic scale, otherwise linear '
                'interpolation is used'),
            'algorithm': alg_blob_log
        },
        'peaks, corners': {
            'description': (
                'Gives a table with coordinates of corners in a corner '
                'measure response image.\nSuppresses multiple connected peaks '
                'with same accumulator value. Operates only on first channel '
                'of image'),
            'min distance': 'Minimum distance between two corners',
            'threshold': (
                'Threshold for minimum intenstity of peaks expressed as '
                'fraction of image maximum (default 0.1)'),
            'algorithm': alg_corner_peaks
        },
        'peaks, local max': {
            'description': (
                'Gives a table with coordinates of the peaks in an image\n'
                'Peaks are local maxima in a region defined by "min '
                'distance". Operates only on first channel of image'),
            'min distance': 'Minimum distance between two corners',
            'threshold': (
                'Threshold for minimum intenstity of peaks expressed as '
                'absolute values (default 0)'),
            'threshold relative': (
                'Threshold for minimum intenstity of peaks expressed as '
                'fraction of image maximum (default 0)'),
            'algorithm': alg_peak_local_max
        },
        'features, daisy': {
            'description': (
                'Extracts all (densely) DAISY features into a table.\nDAISY '
                'is a feature descriptor similar to SIFT formulated in a way '
                'that allows for fast dense extraction.\nTypically, this is '
                'practical for bag-of-features image representations. '
                'Operates only on first channel of image'),
            'step': 'Distance between descriptor sampling points (default 4)',
            'radius': 'Radius in pixels of the outermost ring (default 15)',
            'rings': 'Number of rings (default 3)',
            'histograms': 'Number of histograms sampled per ring (default 8)',
            'orientations': 'Number of orientations per histogram (default 8)',
            'daisy normalization': 'Method for normalizing descriptors',
            'algorithm': alg_daisy
        },
        'features, orb': {
            'description': (
                'Oriented FAST and rotated BRIEF feature detector '
                'and binary descriptor extractor.'),
            'N': ('Number of keypoints to be returned. The best N keypoints '
                  'will be returned, or all found keypoints if fewer.'),
            'fast n': (
                'The n parameter in skimage.feature.corner_fast (9)'),
            'fast threshold': (
                'The threshold parameter in feature.corner_fast. '
                'Decrease the threshold when more corners are desired (0.08)'),
            'harris k': (
                'The k parameter in skimage.feature.corner_harris. '
                'Sensitivity factor to separate corners from edges. (0.04)'),
            'downscale': (
                'Downscale factor for the image pyramid (1.2)'),
            'algorithm': alg_orb
        },
        'features, CENSURE+DAISY': {
            'description': (
                'Combines the CENSUR keypoint detector with a DAISY feature '
                'extractor at the detected keypoints -- picking the closest '
                'DAISY feature if non are at the exact keypoint locations'
            ),
            'step': 'DAISY: Distance between descriptor samples (default 4)',
            'radius': 'DAISY: Radius of the outermost ring (default 15)',
            'rings': 'DAISY: Number of rings (default 3)',
            'histograms': 'DAISY: Number of histograms per ring (default 8)',
            'orientations': 'DAISY: Orientations per histogram (default 8)',
            'daisy normalization': 'DAISY: Method for normalizing descriptors',

            'min scale': 'CENSURE: Minimum scale to extract keypoints from.',
            'max scale': (
                'CENSURE: Maximum scale to extract keypoints from. '
                'The keypoints will be extracted from all the scales except '
                'the first and the last i.e. from the scales in the range '
                '[min_scale + 1, max_scale - 1]. The filter sizes for '
                'different scales is such that the two adjacent scales '
                'comprise of an octave.'),
            'mode': (
                'CENSURE: Bi-level filter used to get the scales of the input '
                'image. Possible values are DoB, Octagon and STAR. The '
                'three modes represent the shape of the bi-level filters '
                'i.e. box(square), octagon and star respectively. For '
                'instance, a bi-level octagon filter consists of a smaller '
                'inner octagon and a larger outer octagon with the filter '
                'weights being uniformly negative in both the inner octagon '
                'while uniformly positive in the difference region. Use STAR '
                'and Octagon for better features and DoB for better '
                'performance.'),
            'non max threshold': (
                'CENSURE: Threshold value for maximas and minimas with '
                'a weak magnitude response obtained after Non-Maximal '
                'Suppression.'),
            'line threshold': (
                'CENSURE: Threshold for interest points which have ratio of '
                'principal curvatures greater than this value.'),
            'algorithm': alg_censur_daisy,
        },
        'keypoints, CENSURE': {
            'description': (
                'CENSURE keypoint detector.'
            ),
            'min scale': 'Minimum scale to extract keypoints from.',
            'max scale': (
                'Maximum scale to extract keypoints from. '
                'The keypoints will be extracted from all the scales except '
                'the first and the last i.e. from the scales in the range '
                '[min_scale + 1, max_scale - 1]. The filter sizes for '
                'different scales is such that the two adjacent scales '
                'comprise of an octave.'),
            'mode': (
                'Type of bi-level filter used to get the scales of the input '
                'image. Possible values are DoB, Octagon and STAR. The '
                'three modes represent the shape of the bi-level filters '
                'i.e. box(square), octagon and star respectively. For '
                'instance, a bi-level octagon filter consists of a smaller '
                'inner octagon and a larger outer octagon with the filter '
                'weights being uniformly negative in both the inner octagon '
                'while uniformly positive in the difference region. Use STAR '
                'and Octagon for better features and DoB for better '
                'performance.'),
            'non max threshold': (
                'Threshold value used to suppress maximas and minimas with '
                'a weak magnitude response obtained after Non-Maximal '
                'Suppression.'),
            'line threshold': (
                'Threshold for rejecting interest points which have ratio of '
                'principal curvatures greater than this value.'),
            'algorithm': alg_censur,
        },
        'features, probabilistic hough lines': {
            'description': (
                'Return lines from a progressive probabilistic line Hough '
                'transform.'),
            'threshold': 'Threshold for hough accumulators',
            'line length': ('Minimum accepted length of detected lines. '
                            'Increase parameter to extract only longer lines'),
            'line gap': (
                'Maximum gap between pixels to still form a line. Increase '
                'the parameter to merge broken lines more aggresively.'),
            'min theta': 'Minium angle in radians for lines, default -pi/2',
            'max theta': 'Maximum angle in radians for lines, default +pi/2',
            'num theta': 'Number of theta samples in the given range',
            'algorithm': alg_prob_hough_lines,
        },
        'meta': {
            'description': (
                'Returns meta information about image: width, '
                'height, channels, min_value, max_value, sum'),
            'prefix': 'Prefix added before column names',
            'algorithm': alg_information,
        },
    }
    options_list = [
        'N', 'bins', 'min sigma', 'max sigma', 'num sigma', 'sigma_ratio',
        'threshold', 'overlap', 'log scale', 'min distance',
        'threshold relative', 'step', 'radius', 'rings', 'histograms',
        'orientations', 'daisy normalization', 'line length', 'line gap',
        'min theta', 'max theta', 'num theta', 'prefix',
        'fast threshold', 'fast n', 'harris k', 'downscale',
        'min scale', 'max scale', 'censure mode', 'non max threshold',
        'line threshold', 'min value', 'max value',
    ]
    options_types = {
        'N': int,
        'fast n': int,
        'fast threshold': float,
        'harris k': float,
        'downscale': float,
        'bins': int,
        'min distance': int,
        'min sigma': float,
        'max sigma': float,
        'sigma_ratio': float,
        'threshold': float,
        'overlap': float,
        'num sigma': int,
        'log scale': bool,
        'threshold relative': float,
        'step': int, 'radius': int, 'rings': int, 'histograms': int,
        'orientations': int,
        'daisy normalization': ['l1', 'l2', 'daisy', 'off'],
        'line length': int,
        'line gap': int,
        'min theta': float,
        'max theta': float,
        'num theta': int,
        'prefix': str,
        'min scale': int,
        'max scale': int,
        'censure mode': ['DoB', 'Octagon', 'STAR'],
        'non max threshold': float,
        'line threshold': float,
        'min value': float,
        'max value': float,
    }
    options_default = {
        'N': 64,
        'fast n': 9,
        'fast threshold': 0.08,
        'harris k': 0.04,
        'downscale': 1.2,
        'bins': 256,
        'min distance': 1,
        'min sigma': 1.0,
        'max sigma': 50.0,
        'sigma_ratio': 1.6,
        'threshold': 2.0,
        'overlap': 0.5,
        'num sigma': 10,
        'log scale': False,
        'threshold relative': 0.0,
        'step': 4,
        'radius': 15,
        'rings': 3,
        'histograms': 8,
        'orientations': 8,
        'line length': 50,
        'line gap': 10,
        'min theta': -np.pi/2,
        'max theta': +np.pi/2,
        'num theta': 100,
        'prefix': "",
        'min scale': 1,
        'max scale': 7,
        'censure mode': 'DoB',
        'non max threshold': 0.15,
        'line threshold': 10.0,
        'min value': 0.0,
        'max value': 1.0,
    }

    parameters = node.parameters()
    parameters.set_string('algorithm', value=next(iter(algorithms)),
                          description='', label='Algorithm')
    ImageFiltering_abstract.generate_parameters(
        parameters, options_types, options_default)

    inputs = Ports([
        Image('Image to extract statistics from', name='source'),
    ])
    outputs = Ports([
        Port.Table('Table with results', name='result'),
    ])
    __doc__ = ImageFiltering_abstract.generate_docstring(
        description, algorithms, options_list, inputs, outputs)

    def execute(self, node_context):
        source_obj = node_context.input['source']
        source = source_obj.get_image()
        params = node_context.parameters
        alg_name = params['algorithm'].value

        if len(source.shape) < 3:
            source = source.reshape(source.shape+(1,))

        alg = self.algorithms[alg_name]['algorithm']
        result = node_context.output['result']
        result.set_name('Statistics')
        alg(source, params, result)


