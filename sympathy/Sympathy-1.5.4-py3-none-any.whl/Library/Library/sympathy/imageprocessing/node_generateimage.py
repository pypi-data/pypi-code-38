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

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
from sympathy.api import node
from sympathy.api.nodeconfig import Ports, Tag, Tags

import numpy as np
from skimage import morphology
from sylib.imageprocessing.image import Image
from sylib.imageprocessing.algorithm_selector import ImageFiltering_abstract


def alg_gaussian(par):
    width = par['width'].value
    height = par['height'].value
    cx = par['x'].value
    cy = par['y'].value

    # vxx = par['varxx'].value
    # vxy = par['varxy'].value
    # vyy = par['varyy'].value
    p        = par['p'].value
    sigma_x  = par['sigma-x'].value
    sigma_y  = par['sigma-y'].value
    rotation = par['rotation'].value
    cos_t = np.cos(rotation)
    sin_t = np.sin(rotation)
    sin_2t = np.sin(2*rotation)
    vxx = (cos_t * cos_t / (2 * sigma_x * sigma_x)
           + sin_t * sin_t / (2 * sigma_y * sigma_y))
    vyy = (sin_t * sin_t / (2 * sigma_x * sigma_x)
           + cos_t * cos_t / (2 * sigma_y * sigma_y))
    vxy = (- sin_2t / (4 * sigma_x * sigma_x)
           + sin_2t / (4 * sigma_y * sigma_y))

    scale = par['scale'].value
    xx = np.array([[x - cx for x in range(width)] for _ in range(height)])
    yy = np.array([[y - cy for _ in range(width)] for y in range(height)])
    return scale * np.exp(-np.power(vxx*xx*xx + 2.0*vxy*xx*yy + vyy*yy*yy, p))


class ImageGenerate(ImageFiltering_abstract, node.Node):
    name = 'Generate Image'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'image_generate.svg'
    description = 'Generates an image or structuring element of a given size'
    nodeid = 'syip.imagegenerate'
    tags = Tags(Tag.ImageProcessing.IO)

    algorithms = {
        'empty': {
            'description': 'Generates an empty image of a given size',
            'width': 'Width of generated image',
            'height': 'Height of generated image',
            'channels': 'Number of channels in generated image',
            'k': 'Value for all pixels in all channels',
            'algorithm': lambda par: np.full((par['height'].value,
                                               par['width'].value,
                                               par['channels'].value), par['k'].value)
        },
        'disk': {
            'description': 'Generates an circular binary structuring element',
            'size': 'Radius of the disk',
            'algorithm': lambda par: morphology.disk(par['size'].value)
        },
        'diamond': {
            'description': (
                'Generates a diamond-shaped binary structuring element.\n\n'
                'A pixel is part of the neighborhood if the city '
                'block/Manhattan distance between it and the center of the'
                'neighborhood is no greater than radius.'),
            'size': 'Radius of the disk',
            'algorithm': lambda par: morphology.diamond(par['size'].value)
        },
        'square': {
            'description': (
                'Generates a square-shaped binary structuring element.'),
            'size': 'Size of the square',
            'algorithm': lambda par: morphology.square(par['size'].value)
        },
        'star': {
            'description': (
                'Generates a star-shaped binary structuring element.\n'
                'The star has 8 vertices and is an overlap of a square of '
                'size 2n + 1 with its 45 degree rotated version. The slanted '
                'sides are 45 or 135 degrees to the horizontal axis.'),
            'size': 'Size "N" of the square',
            'algorithm': lambda par: morphology.star(par['size'].value)
        },
        'octagon': {
            'description': (
                'Generates an octagon-shaped binary structuring element.'),
            'size': 'Size of horizontal/vertial parts of the octagon',
            'other size': 'Size of diagonal parts of the octagon',
            'algorithm': (
                lambda par: morphology.octagon(par['size'].value,
                                               par['other size'].value))
        },
        'rectangle': {
            'description': (
                'Generates a rectangle-shaped binary structuring element.'),
            'width': 'Width of rectangle',
            'height': 'Height of rectangle',
            'algorithm': lambda par: morphology.rectangle(par['height'].value,
                                                          par['width'].value)
        },
        'gaussian': {
            'description': (
                'Generates an elliptical Gaussian from the given variance matrix.'),
            'width': 'Width of rectangle',
            'height': 'Height of rectangle',
            'x': 'Center point along x axis',
            'y': 'Center point along y axis',
            'scale': 'Multiplier for output',
            'sigma-x': 'Variation along first axis before rotation',
            'sigma-y': 'Variation along first axis before rotation',
            'rotation': 'Rotation given in radians',
            'p': 'Super-gaussian exponent (default 1)',
            'algorithm': alg_gaussian
        },
    }

    options_list    = [
        'width', 'height', 'size', 'channels', 'k', 'other size',
        'sigma-x', 'sigma-y', 'rotation', 'scale', 'x', 'y', 'p'
    ]
    options_types   = {
        'width': int,
        'height': int,
        'sigma-x': float,
        'sigma-y': float,
        'rotation': float,
        'scale': float,
        'x': float,
        'y': float,
        'k': float,
        'p': float,
        'size': int,
        'other size': int,
        'channels': int,
    }
    options_default = {
        'width': 16,
        'height': 16,
        'sigma-x': 0.5,
        'sigma-y': 0.5,
        'rotation': 0.0,
        'scale': 1.0,
        'x': 0.0,
        'y': 0.0,
        'k': 0.0,
        'p': 1.0,
        'size': 5,
        'other size': 5,
        'channels': 1,
    }

    parameters = node.parameters()
    parameters.set_string(
        'algorithm', value=next(iter(algorithms)), description='', label='Algorithm')
    ImageFiltering_abstract.generate_parameters(
        parameters, options_types, options_default)

    outputs = Ports([
        Image('Resulting image', name='output'),
    ])
    __doc__ = ImageFiltering_abstract.generate_docstring(
        description, algorithms, options_list, None, outputs)

    def execute(self, node_context):

        params = node_context.parameters
        alg_name = params['algorithm'].value
        alg      = self.algorithms[alg_name]['algorithm']
        result   = alg(params)
        node_context.output['output'].set_image(result)
