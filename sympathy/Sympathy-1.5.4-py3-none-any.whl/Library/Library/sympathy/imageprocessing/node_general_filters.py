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
from sympathy.api.nodeconfig import Ports

from skimage import filters, transform, feature
from sylib.imageprocessing.image import Image
from sylib.imageprocessing.algorithm_selector import ImageFiltering_abstract
from sylib.imageprocessing.generic_filtering import GenericImageFiltering


API_URL = 'http://scikit-image.org/docs/0.13.x/api/'


def alg_center_image(im, params):
    x_weights = np.ones(im.shape[:2]) * np.arange(im.shape[1])
    y_weights = (
        np.ones((im.shape[1], im.shape[0])) * np.arange(im.shape[0])
    ).transpose()
    if len(im.shape) < 3:
        im = im.reshape(im.shape+(1,))
    channels = im.shape[2]
    x_w_sum, y_w_sum = 0, 0
    x_sum, y_sum = 0, 0
    for channel in range(channels):
        x_w_sum += np.sum(im[:, :, channel] * x_weights)
        y_w_sum += np.sum(im[:, :, channel] * y_weights)
        x_sum += np.sum(im[:, :, channel])
        y_sum += np.sum(im[:, :, channel])
    xpos = x_w_sum / x_sum
    ypos = y_w_sum / y_sum
    dx = int(xpos - im.shape[1]/2)
    dy = int(ypos - im.shape[0]/2)
    out = np.zeros(im.shape)
    if dx < 0 and dy < 0:
        out[-dy:, -dx:, :] = im[:dy, :dx, :]
    elif dx < 0 and dy >= 0:
        out[:-dy, -dx:, :] = im[dy:, :dx, :]
    elif dx >= 0 and dy < 0:
        out[-dy:, :-dx, :] = im[:dy, dx:, :]
    elif dx >= 0 and dy >= 0:
        out[:-dy, :-dx, :] = im[dy:, dx:, :]
    return out


GENERAL_ALGS = {
    'to integer': {
        'description': 'Converts all channels into integer data',
        'multi_chromatic': True,
        'algorithm': lambda im, par: im.astype('int64')
    },
    'gaussian': {
        'description': 'Two-dimensional Gaussian filter',
        'sigma-x': 'Standard deviation of gaussian filter along X-axis',
        'sigma-y': 'Standard deviation of gaussian filter along Y-axis',
        'border mode': 'Determines how the array borders are handled',
        'k': 'Value outside image borders when method constant is used.',
        'multi_chromatic': False,
        'url': API_URL+'skimage.filters.html#skimage.filters.gaussian',
        'algorithm': (
            lambda im, par: filters.gaussian(
                im, cval=par['k'].value, mode=par['border mode'].value,
                sigma=(par['sigma-x'].value, par['sigma-y'].value)))
    },
    'scale/offset': {
        'description': (
            'Adds a scale and/or an offset to each channel equally'),
        'scale': 'Scale factor applied to image before offset',
        'offset': 'Offset applied to image after scale',
        'multi_chromatic': True,
        'algorithm': (
            lambda im, par: im*par['scale'].value + par['offset'].value)
    },
    'normalize': {
        'description': (
            'Adds a (positive) scale and offset so that smallest/highest '
            'value in image becomes 0 and 1 respectively.\n '
            'Operates on each channel separately'),
        'multi_chromatic': False,
        'minimum': 'Minimum value after normalization',
        'maximum': 'Maximum value after normalization',
        'algorithm': (
            lambda im, par:
                ((im.astype(np.float)-np.min(im))/(np.max(im)-np.min(im))) *
                (par['maximum'].value-par['minimum'].value) +
                par['minimum'].value
        )
    },
    'clamp': {
        'description': (
            'Restricts the output values to a given maximum/minimum'),
        'maximum': 'The maximum output value that can be passed through',
        'minimum': 'The minimum output value that can be passed through',
        'multi_chromatic': True,
        'algorithm': (
            lambda im, par: np.maximum(
                np.minimum(im, par['maximum'].value),
                par['minimum'].value))
    },
    'integral image': {
        'description': (
            'Creates the integral image of the input.\n'
            'An integral image contains at coordinate (m,n) the sum of '
            'all values above and to the left of it.\n '
            '  S(m,n) = sum(im[0:m, 0:n])'),
        'multi_chromatic': False,
        'url': (
            API_URL+'skimage.feature.html'
            '#skimage.feature.hessian_matrix_det'),
        'algorithm': lambda im, par: transform.integral_image(im)
    },
    'hessian determinant': {
        'description': (
            'Computes an approximation of the determinant of the '
            'hessian matrix for each pixel.'),
        'multi_chromatic': False,
        'sigma': (
            'Standard deviation of gaussian kernel (default 3.0) used '
            'for calculating Hessian.\nApproximation is not reliable '
            'for sigma < 3.0'),
        'url': (
            API_URL+'skimage.feature.html'
            '#skimage.feature.hessian_matrix_det'),
        'algorithm': lambda im, par: feature.hessian_matrix_det(
            im, sigma=par['sigma'].value)
    },
    'center image': {
        'description': (
            'Shifts image so that center of mass lies in center of image'),
        'multi_chromatic': True,
        'algorithm': alg_center_image
    },
    'abs': {
        'description': (
            'Computes absolute value or complex magnitude of image'),
        'multi_chromatic': False,
        'algorithm': lambda im, par: np.abs(im)
    },
    'real': {
        'description': (
            'Gives the real valued part of a complex image'),
        'multi_chromatic': False,
        'algorithm': lambda im, par: np.real(im)
    },
    'imag': {
        'description': (
            'Gives the imaginary part of a complex image'),
        'multi_chromatic': False,
        'algorithm': lambda im, par: np.imag(im)
    },
    'angle': {
        'description': (
            'Gives the phase angle of a complex image'),
        'multi_chromatic': False,
        'algorithm': lambda im, par: np.angle(im)
    },
}

GENERAL_PARAMETERS = [
    'sigma-x', 'sigma-y', 'border mode', 'k', 'scale', 'offset',
    'minimum', 'maximum', 'sigma'
]
GENERAL_TYPES = {
    'scale': float, 'k': float, 'sigma-y': float, 'sigma-x': float,
    'maximum': float,
    'border mode': ['constant', 'reflect', 'wrap', 'nearest', 'mirror'],
    'minimum': float, 'offset': float, 'sigma': float
}
GENERAL_DEFAULTS = {
    'scale': 1.0, 'k': 0.05, 'sigma-y': 1.0, 'sigma-x': 1.0,
    'maximum': 1.0, 'minimum': 0.0, 'offset': 0.0, 'sigma': 1.0
}


class GeneralImageFiltering(ImageFiltering_abstract, GenericImageFiltering,
                            node.Node):
    name = 'Filter image'
    icon = 'image_filtering.svg'
    description = (
        'Applies simple filtering or scaling algorithms on an image. For more '
        'complex operations see the more specialized image manipulation nodes')
    nodeid = 'syip.general_filters'

    algorithms = GENERAL_ALGS
    options_list = GENERAL_PARAMETERS
    options_types = GENERAL_TYPES
    options_default = GENERAL_DEFAULTS

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
