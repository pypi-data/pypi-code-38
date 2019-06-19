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
from sympathy.api.nodeconfig import Ports, Tag, Tags

import numpy as np
from skimage import morphology, filters
from sylib.imageprocessing.image import Image
from sylib.imageprocessing.algorithm_selector import ImageFiltering_abstract


class ImageMorphology(ImageFiltering_abstract, node.Node):
    name = 'Morphological Image Operations'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'image_morphology.svg'
    description = (
        'Performs one of a selection of morphological or rank operations on a '
        'target image (top) that uses a given structuring element (bottom). '
        'Other morphological operations can be found under the "filter" node')
    nodeid = 'syip.imagemorphology'
    tags = Tags(Tag.ImageProcessing.ImageManipulation)

    dilation = (
        'Morphological dilation sets a pixel at *(i,j)* to the maximum over '
        'all pixels in the neighborhood defined by\nthe structuring element '
        'centered at *(i,j)*. Dilation enlarges bright regions and shrinks '
        'dark regions.')
    erosion = ('Morphological erosion sets a pixel at *(i,j)* to the minimum '
               'over all pixels in the neighborhood centered at *(i,j)*. '
               'Erosion shrinks bright regions and enlarges dark regions.')
    closing = ('The morphological closing on an image is defined as a '
               'dilation followed by an erosion.\nClosing can remove small '
               'dark spots and connect small bright cracks.')
    opening = ('The morphological opening on an image is defined as a erosion '
               'followed by a dilation.\Opening can remove small white spots '
               'and connect small dark cracks.')

    def alg_median(target, se, par):
        if np.issubdtype(target.dtype, np.float):
            maxval = np.max(target)
            minval = np.min(target)
            target = (target - minval) * 256 / (maxval - minval)
            result = filters.median(target.astype('uint8'), se)
            return result * (maxval - minval) / 256.0 + minval
        else:
            return filters.median(target, se)

    api = 'http://scikit-image.org/docs/0.13.x/api/'
    algorithms = {
        'binary, closing': {
            'description': (
                'Perform morphological closing on image. Target and '
                'structuring element must be binary\n\n' + closing),
            'multi_chromatic': False,
            'algorithm': (
                lambda target, se, par: morphology.binary_closing(target, se))
        },
        'binary, dilation': {
            'description': (
                'Perform morphological dilation on image. Target and '
                'structuring element must be binary\n\n' + dilation),
            'multi_chromatic': False,
            'algorithm': (
                lambda target, se, par: morphology.binary_dilation(target, se))
        },
        'binary, erosion': {
            'description': (
                'Perform morphological erosion on image. Target and '
                'structuring element must be binary\n\n' + erosion),
            'multi_chromatic': False,
            'algorithm': (
                lambda target, se, par: morphology.binary_erosion(target, se))
        },
        'binary, opening': {
            'description': (
                'Perform morphological opening on image. Target and '
                'structuring element must be binary\n\n'+opening),
            'multi_chromatic': False,
            'algorithm': (
                lambda target, se, par: morphology.binary_opening(target, se))
        },
        'grey, closing': {
            'description': (
                'Perform greyscale morphological closing on image.\n\n' +
                closing),
            'multi_chromatic': False,
            'algorithm': lambda target, se, par: morphology.closing(target, se)
        },
        'grey, opening': {
            'description': (
                'Perform greyscale morphological opening on image.\n\n' +
                opening),
            'multi_chromatic': False,
            'algorithm': lambda target, se, par: morphology.opening(target, se)
        },
        'grey, dilation': {
            'description': (
                'Return greyscale morphological dilation of an image.\n\n' +
                dilation),
            'multi_chromatic': False,
            'algorithm': lambda target, se, par: morphology.dilation(target, se)
        },
        'grey, erosion': {
            'description': (
                'Return greyscale morphological erosion of an image.\n\n' +
                erosion),
            'multi_chromatic': False,
            'algorithm': lambda target, se, par: morphology.erosion(target, se)
        },
        'tophat, black': {
            'description': (
                'Return morphological black-tophat of image.\n\nThe black top '
                'hat of an image is defined as its morphological closing '
                'minus the original image.\nThis operation returns the dark '
                'spots of the image that are smaller than the structuring '
                'element.\nNote that dark spots in the original image are '
                'bright spots after the black top hat.'),
            'multi_chromatic': False,
            'algorithm': (
                lambda target, se, par: morphology.black_tophat(target, se))
        },
        'tophat, white': {
            'description': (
                'Return morphological white-tophat of image.\n\n'
                'The white top hat of an image is defined as the image minus '
                'its morphological opening.\nThis operation returns the white '
                'spots of the image that are smaller than the structuring '
                'element.'),
            'multi_chromatic': False,
            'algorithm': (
                lambda target, se, par: morphology.white_tophat(target, se))
        },
        'median': {
            'description': (
                'Return the median of the neighborhood defined by sweeping '
                'the structuring element over the image.\nWhen used on '
                'non-integer datatypes they are first cast into uint8\nThis '
                'operation functions as a filter suitable to removing salt '
                'and pepper noise'),
            'multi_chromatic': False,
            'algorithm': alg_median
        },
        'autolevel': {
            'description': (
                'Stretches the local histogram defined by structuring element '
                'to cover the full range'),
            'p0': 'Defines the lower percentile (0..1) included in histogram',
            'p1': 'Defines the upper percentile (0..1) included in histogram',
            'multi_chromatic': False,
            'url': (
                api + 'skimage.filters.rank.html' +
                '#skimage.filters.rank.autolevel'),
            'algorithm': (lambda target, se, par:
                          filters.rank.autolevel_percentile(
                              target, se, p0=par['p0'].value,
                              p1=par['p1'].value) / 256.0)
        },

    }

    options_list    = ['p0', 'p1', ]
    options_types   = {
        'p0': float,
        'p1': float,
    }
    options_default = {
        'p0': 0.25,
        'p1': 0.75,
    }

    parameters = node.parameters()
    parameters.set_string(
        'algorithm',
        value=next(iter(algorithms)), description='', label='Algorithm')
    ImageFiltering_abstract.generate_parameters(
        parameters, options_types, options_default)

    inputs = Ports([
        Image('Target image', name='target'),
        Image('Structuring element', name='structuring_element'),
    ])
    outputs = Ports([
        Image('Resulting image', name='output'),
    ])

    __doc__ = ImageFiltering_abstract.generate_docstring(
        description, algorithms, options_list, inputs, outputs)

    def execute(self, node_context):

        target = node_context.input['target'].get_image()
        se     = node_context.input['structuring_element'].get_image()

        params   = node_context.parameters
        alg_name = params['algorithm'].value
        alg      = self.algorithms[alg_name]['algorithm']

        if len(target.shape) == 3 and target.shape[2] > 1:
            multichannel_image = True
        else:
            multichannel_image = False

        alg = self.algorithms[alg_name]['algorithm']
        if len(se.shape) == 3 and se.shape[2] == 1:
            se = se.reshape(se.shape[:2])
        if len(target.shape) == 3 and target.shape[2] == 1:
            target = target.reshape(target.shape[:2])

        if (multichannel_image and
            not self.algorithms[alg_name]['multi_chromatic']):
            im1         = alg(target[:, :, 0], se, params)
            im          = np.zeros(im1.shape[:2] + (target.shape[2],))
            im[:, :, 0] = im1
            for channel in range(1, target.shape[2]):
                im[:, :, channel] = alg(target[:, :, channel], se, params)
        else:
            im = alg(target, se, params)
        node_context.output['output'].set_image(im)
