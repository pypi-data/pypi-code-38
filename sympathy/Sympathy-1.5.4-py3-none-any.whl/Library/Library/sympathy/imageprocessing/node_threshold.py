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
import numpy as np

from sympathy.api import node
from sympathy.api.nodeconfig import Ports, Tag, Tags

from skimage import filters
from sylib.imageprocessing.image import Image
from sylib.imageprocessing.algorithm_selector import ImageFiltering_abstract
from sylib.imageprocessing.generic_filtering import GenericImageFiltering


API_URL = 'http://scikit-image.org/docs/0.13.x/api/'


def alg_auto_threshold(im, params):
    method = params['auto threshold method'].value
    fns = {
        'otsu': filters.threshold_otsu,
        'yen': filters.threshold_yen,
        'isodata': filters.threshold_isodata,
        'li': filters.threshold_li,
        'minimum': filters.threshold_minimum,
        'mean': filters.threshold_mean,
        'triangle': filters.threshold_triangle,
        'median': lambda x: np.median(x)
    }
    fn = fns[method]
    return im > fn(im)


THRESHOLD_ALGS = {
    'basic': {
        'description': 'Compares each channel with a threshold',
        'threshold': 'Threshold value to compare with',
        'multi_chromatic': False,
        'algorithm': lambda im, par: im >= par['threshold'].value
    },
    'automatic': {
        'description': (
            'Performs global thresholding based a selection of automatic '
            'algorithms with none or few parameters'),
        'auto threshold method': (
            'Method used for calculating threshold'),
        'url': (
            API_URL+'skimage.filters.html'),
        'algorithm': alg_auto_threshold,
        'multi_chromatic': False,
    },
    'adaptive': {
        'description': (
            'Applies an adaptive threshold to an array.\n\n'
            'Also known as local or dynamic thresholding where the '
            'threshold value is the weighted mean for the local '
            'neighborhood of a pixel subtracted by a constant.'),
        'kernel size': (
            'Size of blocks used during threshold check.\n'
            'Must be an odd number. (default 3)'),
        'threshold method': (
            'Method used for calculating adaptive threshold'),
        'offset': (
            'Constant subtracted from weighted mean of neighborhood '
            'to calculate the local threshold value. (default 0.0)'),
        'sigma': (
            'Standard deviation of gaussian kernel when method '
            'gaussian is used.'),
        'multi_chromatic': False,
        'url': (
            API_URL+'skimage.filters.html#skimage.filters.threshold_local'),
        'algorithm': lambda im, par: im > filters.threshold_local(
            im, par['kernel size'].value,
            method=par['threshold method'].value,
            offset=par['offset'].value,
            param=par['sigma'].value)
    },
}

THRESHOLD_PARAMETERS = [
    'threshold method', 'auto threshold method', 'threshold',
    'kernel size', 'offset', 'sigma',
]
THRESHOLD_TYPES = {
    'threshold method': ['gaussian', 'mean', 'median'],
    'auto threshold method': [
        'otsu', 'yen', 'isodata', 'li', 'minimum', 'mean', 'triangle', 'median'
    ],
    'offset': float, 'threshold': float, 'kernel size': int, 'sigma': float
}
THRESHOLD_DEFAULTS = {
    'threshold': 0.15, 'kernel size': 21, 'sigma': 21.0,
    'auto threshold method': 'otsu', 'offset': 0.0
}


class ThresholdImage(ImageFiltering_abstract, GenericImageFiltering,
                     node.Node):
    name = 'Threshold image'
    icon = 'image_threshold.svg'
    description = (
        'Applies a threshold to an image giving a boolean output')
    nodeid = 'syip.threshold'
    copyright = "(C) 2017 Combine Control Systems AB"
    tags      = Tags(Tag.ImageProcessing.Segmentation)

    algorithms = THRESHOLD_ALGS
    options_list = THRESHOLD_PARAMETERS
    options_types = THRESHOLD_TYPES
    options_default = THRESHOLD_DEFAULTS

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
