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

from skimage import transform
from sylib.imageprocessing.image import Image
from sylib.imageprocessing.algorithm_selector import ImageFiltering_abstract
from sylib.imageprocessing.generic_filtering import GenericImageFiltering


def alg_resize(im, params):
    req_h = params['height'].value
    req_w = params['width'].value
    h, w = req_h, req_w
    if params['aspect'].value:
        aspect = im.shape[1] / float(im.shape[0])
        size = min(req_w / aspect, req_h)
        w = int(size * aspect)
        h = int(size)

    shape = (h, w) + im.shape[2:]
    result_im = transform.resize(
        im, shape, order=params['interpolation degree'].value,
        mode='constant', anti_aliasing=True)
    if params['padding'].value:
        pad_h = req_h - h
        pad_w = req_w - w
        padded_im = np.zeros((req_h, req_w) + im.shape[2:])
        x0 = int(pad_w/2)
        x1 = x0 + result_im.shape[1]
        y0 = int(pad_h/2)
        y1 = y0 + result_im.shape[0]
        padded_im[y0:y1, x0:x1] = result_im
        return padded_im
    return result_im


def alg_padding(im, params):
    if len(im.shape) < 3:
        im = im.reshape(im.shape+(1,))
    add_alpha = params['add alpha'].value
    px, py = params['x'].value, params['y'].value
    px, py = int(px), int(py)
    k = params['k'].value
    max_x = im.shape[1]+abs(px)
    max_y = im.shape[0]+abs(py)
    result = np.full((max_y, max_x, im.shape[2]+add_alpha), k)
    if add_alpha:
        result[max(0, py):max(0, py)+im.shape[0],
               max(0, px):max(0, px)+im.shape[1], :-1] = im
        result[max(0, py):max(0, py)+im.shape[0],
               max(0, px):max(0, px)+im.shape[1], -1] = np.ones(im.shape[:2])
    else:
        result[max(0, py):max(0, py)+im.shape[0],
               max(0, px):max(0, px)+im.shape[1]] = im
    return result


def alg_crop_image(im, params):
    x, y = params['x'].value, params['y'].value
    w, h = params['width'].value, params['height'].value
    shape = im.shape
    x, y = min(x, shape[1]), min(y, shape[0])
    w, h = min(w, shape[1]-x), min(h, shape[0]-y)
    return im[y:y+h, x:x+w]


API_URL = 'http://scikit-image.org/docs/0.13.x/api/'
INTERPOLATION_DEGREE_DESC = (
    'Degree of polynomial (0 - 5) used for interpolation.\n'
    '0 - no interpolation, 1 - bi-linear interpolation, '
    '3 - bi-cubic interpolation'
)

TRANSFORM_ALGS = {
    'resize': {
        'description': 'Resizes an image to match the given dimensions',
        'width': 'The new width of the image',
        'height': 'The new height of the image',
        'interpolation degree': INTERPOLATION_DEGREE_DESC,
        'multi_chromatic': True,
        'aspect': 'Preserve aspect ratio (gives smaller size on one axis)',
        'padding': (
            'Adds padding to fill out full width/height after '
            'aspect-correct scaling'),
        'url': API_URL+'skimage.transform.html#skimage.transform.resize',
        'algorithm': alg_resize
    },
    'rescale': {
        'description': 'Rescales an image by a given factor',
        'scale x': 'Scale factor along X direction (horizontal)',
        'scale y': 'Scale factor along Y direction (vertical)',
        'interpolation degree': INTERPOLATION_DEGREE_DESC,
        'multi_chromatic': True,
        'url': API_URL+'skimage.transform.html#skimage.transform.rescale',
        'algorithm': lambda im, par: transform.rescale(
            im, (par['scale y'].value, par['scale x'].value),
            mode='constant',
            multichannel=True,
            anti_aliasing=True,
            order=par['interpolation degree'].value)
    },
    'rotate': {
        'description': 'Rotates an image',
        'angle': 'Angular degrees to rotate clockwise',
        'resize': (
            'If true new image dimensions are calculated '
            'to exactly fit the image'),
        'multi_chromatic': True,
        'url': API_URL+'skimage.transform.html#skimage.transform.rotate',
        'algorithm': lambda im, par: transform.rotate(
            im, par['angle'].value, resize=par['resize'].value)
    },
    'padding': {
        'description': 'Adds a padding to an image',
        'x': (
            'If positive, amount of padding added on the left side. '
            'If negative the amount of padding added on the right side.'),
        'y': ('If positive, amount of padding added on the top.'
              'If negative the amount of padding added on the bottom.'),
        'k': 'Constant value used in padded areas',
        'add alpha': (
            'Adds an alpha with value 1.0 inside image, 0.0 outside'),
        'multi_chromatic': True,
        'algorithm': alg_padding,
    },
    'crop': {
        'description': 'Crops the image to the given rectanglular area',
        'x': 'Left edge of image',
        'y': 'Top edge of image',
        'width': 'Width of image',
        'height': 'Height of image',
        'multi_chromatic': False,
        'algorithm': alg_crop_image,
    },
}

TRANSFORM_PARAMETERS = [
    'x', 'y', 'width', 'height', 'padding', 'aspect', 'interpolation degree',
    'scale x', 'scale y', 'angle', 'resize', 'k', 'add alpha'
]
TRANSFORM_TYPES = {
    'angle': float, 'scale y': float, 'scale x': float, 'k': float,
    'height': int, 'padding': bool, 'width': int, 'aspect': bool,
    'y': int, 'x': int, 'interpolation degree': int,
    'add alpha': bool, 'resize': bool
}
TRANSFORM_DEFAULTS = {
    'angle': 0.0, 'scale y': 1.0, 'scale x': 1.0, 'k': 0.05, 'height': 512,
    'padding': False, 'width': 512, 'aspect': False, 'y': 0, 'x': 0,
    'interpolation degree': 3, 'add alpha': False, 'resize': True
}


class TransformFilter(ImageFiltering_abstract, GenericImageFiltering,
                      node.Node):
    name = 'Transform image'
    icon = 'image_transform.svg'
    description = (
        'Transforms and image into another shape')
    nodeid = 'syip.transform'
    copyright = "(C) 2017 Combine Control Systems AB"

    algorithms = TRANSFORM_ALGS
    options_list = TRANSFORM_PARAMETERS
    options_types = TRANSFORM_TYPES
    options_default = TRANSFORM_DEFAULTS

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
