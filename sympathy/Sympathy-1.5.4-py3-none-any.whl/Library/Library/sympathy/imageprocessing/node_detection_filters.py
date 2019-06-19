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
#     * Neither the name of Combine Control Systems AB nor the
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
from sympathy.api.nodeconfig import Ports

from skimage import filters, feature
from sylib.imageprocessing.image import Image
from sylib.imageprocessing.algorithm_selector import ImageFiltering_abstract
from sylib.imageprocessing.generic_filtering import GenericImageFiltering


def alg_prewitt(im, params):
    method = params['horizontal/vertical'].value
    if method == 'horizontal':
        return filters.prewitt_h(im)
    elif method == 'vertical':
        return filters.prewitt_v(im)
    else:
        return filters.prewitt(im)


def alg_scharr(im, params):
    method = params['horizontal/vertical'].value
    if method == 'horizontal':
        return filters.scharr_h(im)
    elif method == 'vertical':
        return filters.scharr_v(im)
    else:
        return filters.scharr(im)


def alg_sobel(im, params):
    method = params['horizontal/vertical'].value
    if method == 'horizontal':
        return filters.sobel_h(im)
    elif method == 'vertical':
        return filters.sobel_v(im)
    else:
        return filters.sobel(im)


def alg_roberts(im, params):
    method = params['positive/negative diagonal'].value
    if method == 'positive':
        return filters.roberts_pos_diag(im)
    elif method == 'negative':
        return filters.roberts_neg_diag(im)
    else:
        return filters.roberts(im)


API_URL = 'http://scikit-image.org/docs/0.13.x/api/'

EDGE_DETECTORS = {
    'canny': {
        'description': 'Canny edge detection.',
        'sigma': 'Standard deviation of gaussian kernel (default 1.0)',
        'multi_chromatic': False,
        'url': API_URL+'skimage.feature.html#skimage.feature.canny',
        'algorithm': (
            lambda im, par: feature.canny(im, sigma=par['sigma'].value))
    },
    'prewitt': {
        'description': (
            'Find edges using the Prewitt transform as one of, or '
            'combination of horizontal and vertical prewitt convolutions'),
        'horizontal/vertical': (
            'Select orientation for transform, '
            'if both then mean square of both will be used'),
        'multi_chromatic': False,
        'url': API_URL+'skimage.filters.html#skimage.filters.prewitt_h',
        'algorithm': alg_prewitt
    },
    'scharr': {
        'description': (
            'Find edges using the Scharr transform as one of, or '
            'combination of horizontal and vertical prewitt convolutions.'
            '\nThe Scharr operator has a better rotation invariance than '
            'other edge filters such as the Sobel or the Prewitt '
            'operators'),
        'horizontal/vertical': (
            'Select orientation for transform, '
            'if both then mean square of both will be used'),
        'multi_chromatic': False,
        'url': API_URL+'skimage.filters.html#skimage.filters.scharr_h',
        'algorithm': alg_scharr
    },
    'sobel': {
        'description': (
            'Find edges using the Sobel transform as one of, or '
            'combination of horizontal and vertical prewitt '
            'convolutions.'),
        'horizontal/vertical': (
            'Select orientation for transform, '
            'if both then mean square of both will be used'),
        'multi_chromatic': False,
        'url': API_URL+'skimage.filters.html#skimage.filters.sobel_h',
        'algorithm': alg_sobel
    },
    'roberts': {
        'description': "Find edges using Robert's cross operator.",
        'positive/negative diagonal': 'Select orientation for transform',
        'multi_chromatic': False,
        'url': API_URL+'skimage.filters.html#skimage.filters.roberts_pos_diag',
        'algorithm': alg_roberts
    },
    'laplace': {
        'description': "Find edges using the Laplace operator.",
        'kernel size': 'Kernel size of the discrete Laplacian operator',
        'multi_chromatic': False,
        'url': API_URL+'skimage.filters.html#skimage.filters.laplace',
        'algorithm': (
            lambda im, par: filters.laplace(
                im, ksize=par['kernel size'].value))
    },
}
CORNER_DETECTORS = {
    'FAST': {
        'description': (
            'Corner detection using the FAST '
            '(Feature from Accelerated Segment Test) method.'),
        'n': (
            'Number of points out of 16 that should be all brighter or'
            'darker than test point. (default 12)'),
        'threshold': (
            'Threshold used in determining wheter the pixels are darker or'
            'brighter (default 0.15).\nDecrease threshold when more '
            'corners are desired'),
        'multi_chromatic': False,
        'url': API_URL+'skimage.feature.html#skimage.feature.corner_fast',
        'algorithm': (
            lambda im, par: feature.corner_fast(
                im, n=par['n'].value, threshold=par['threshold'].value))
    },
    'harris': {
        'description': 'Compute corner harris response image.',
        'harris method': (
            'Method to compute response image from auto-correlation'
            'matrix'),
        'k': (
            'Sensitivity factor to separate corners from edges, typically '
            'in range [0, 0.2]. Small values of k result in detection of '
            'sharp corners.'),
        'eps': 'Normalisation factor (Nobles corner measure)',
        'sigma': (
            'Standard deviation used for the Gaussian kernel, which is '
            'used as weighting function for the auto-correlation matrix.'),
        'multi_chromatic': False,
        'url': API_URL+'skimage.feature.html#skimage.feature.corner_harris',
        'algorithm': (
            lambda im, par: feature.corner_harris(
                im,
                k=par['k'].value,
                eps=par['eps'].value,
                sigma=par['sigma'].value,
                method=par['harris method'].value))
    },
    'KR': {
        'description': (
            'Compute Kitchen-Rosenfeld corner measure response image'),
        'border mode': 'Method for handling values outside the borders',
        'k': 'Value outside image borders when method constant is used.',
        'multi_chromatic': False,
        'url': (
            API_URL + 'skimage.feature.html' +
            '#skimage.feature.corner_kitchen_rosenfeld'),
        'algorithm': (
            lambda im, par: feature.corner_kitchen_rosenfeld(
                im, cval=par['k'].value, mode=par['border mode'].value))
    },
    'moravec': {
        'description': (
            'Compute Moravec corner measure response image.\n\n '
            'This is one of the simplest corner detectors and is '
            'comparatively fast but has several limitations '
            '(e.g. not rotation invariant).'),
        'window size': 'Size of window used during calculations',
        'multi_chromatic': False,
        'url': API_URL+'skimage.feature.html#skimage.feature.corner_moravec',
        'algorithm': (
            lambda im, par: feature.corner_moravec(
                im, window_size=par['window size'].value))
    },
    'ST': {
        'description': (
            'Compute Shi-Tomasi (Kanade-Tomasi) corner measure response'
            'image. Uses information from auto-correlation matrix'),
        'sigma': (
            'Standard deviation used for the Gaussian kernel, which is '
            'used as weighting function for the auto-correlation matrix.'),
        'multi_chromatic': False,
        'url': (
            API_URL+'skimage.feature.html#skimage.feature.corner_shi_tomasi'),
        'algorithm': (
            lambda im, par: feature.corner_shi_tomasi(
                im, sigma=par['sigma'].value))
    },
}

EDGE_DETECTOR_PARAMETERS = [
    'sigma', 'horizontal/vertical', 'positive/negative diagonal', 'kernel size',
]
EDGE_DETECTOR_TYPES = {
    'horizontal/vertical': ['horizontal', 'vertical', 'both'],
    'kernel size': int,
    'positive/negative diagonal': ['default', 'positive', 'negative'],
    'sigma': float
}
EDGE_DETECTOR_DEFAULTS = {
    'kernel size': 3,
    'sigma': 1.0
}

CORNER_DETECTOR_PARAMETERS = [
    'n', 'threshold', 'harris method', 'k', 'eps', 'sigma',
    'border mode', 'window size'
]
CORNER_DETECTOR_TYPES = {
    'border mode': ['constant', 'reflect', 'wrap', 'nearest', 'mirror'],
    'eps': float,
    'harris method': ['k', 'eps'],
    'k': float,
    'n': int,
    'sigma': float,
    'threshold': float,
    'window size': int,
}
CORNER_DETECTOR_DEFAULTS = {
    'eps': 1e-06,
    'k': 0.05,
    'n': 12,
    'sigma': 1.0,
    'threshold': 0.15,
    'window size': 1,
}


class EdgeDetection(ImageFiltering_abstract, GenericImageFiltering, node.Node):
    name = 'Edge detection'
    icon = 'image_edges.svg'
    description = (
        'Detects edges in the incoming image')
    nodeid = 'syip.edge_detection'
    copyright = "(C) 2017 Combine Control Systems AB"

    algorithms = EDGE_DETECTORS
    options_list = EDGE_DETECTOR_PARAMETERS
    options_types = EDGE_DETECTOR_TYPES
    options_default = EDGE_DETECTOR_DEFAULTS

    parameters = node.parameters()
    parameters.set_string('algorithm', value=next(iter(algorithms)),
                          description='', label='Algorithm')
    ImageFiltering_abstract.generate_parameters(parameters, options_types,
                                                options_default)
    inputs = Ports([
        Image('source image to filter', name='source'),
    ])
    outputs = Ports([
        Image('result after filtering', name='result'),
    ])
    __doc__ = ImageFiltering_abstract.generate_docstring(
        description, algorithms, options_list, inputs, outputs)


class CornerDetection(ImageFiltering_abstract, GenericImageFiltering,
                      node.Node):
    name = 'Corner detection'
    icon = 'image_corners.svg'
    description = (
        'Detects corners in the incoming image')
    nodeid = 'syip.corner_detection'
    copyright = "(C) 2017 Combine Control Systems AB"

    algorithms = CORNER_DETECTORS
    options_list = CORNER_DETECTOR_PARAMETERS
    options_types = CORNER_DETECTOR_TYPES
    options_default = CORNER_DETECTOR_DEFAULTS

    parameters = node.parameters()
    parameters.set_string('algorithm', value=next(iter(algorithms)),
                          description='', label='Algorithm')
    ImageFiltering_abstract.generate_parameters(parameters, options_types,
                                                options_default)
    inputs = Ports([Image('source image to filter', name='source')])
    outputs = Ports([Image('result after filtering', name='result')])
    __doc__ = ImageFiltering_abstract.generate_docstring(
        description, algorithms, options_list, inputs, outputs)
