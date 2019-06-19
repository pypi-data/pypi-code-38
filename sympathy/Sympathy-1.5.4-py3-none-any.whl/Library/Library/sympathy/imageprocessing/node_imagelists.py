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
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags

import numpy as np
from sylib.imageprocessing.image import Image
from sylib.imageprocessing.image import File as ImageFile
from sylib.imageprocessing.algorithm_selector import (
    ImageFiltering_abstract)


class ImageToList(ImageFiltering_abstract, node.Node):
    name = 'Image to List'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'image_list.svg'
    description = ('Generates a list of images based on algorithms operating '
                   'on one image')
    nodeid = 'syip.image2list'
    tags = Tags(Tag.ImageProcessing.Layers)

    def alg_from_labels(im, results, par):
        if not np.issubdtype(im.dtype, np.integer):
            # Early return, input is not a labeled image
            return
        if len(im.shape) == 3:
            im = im[:, :, 0]
        for value in range(np.min(im), np.max(im)+1):
            mask = im == value
            if value == 0 and not par['do background'].value:
                pass
            elif np.sum(mask) > 0:
                new_image = ImageFile()
                new_image.set_image(mask)
                results.append(new_image)

    def alg_from_channels(im, results, par):
        if len(im.shape) < 3:
            im = im.reshape(im.shape + (1,))
        channels = im.shape[2]
        for channel in range(channels):
            new_image = ImageFile()
            new_image.set_image(im[:, :, channel])
            results.append(new_image)

    algorithms = {
        'from labels': {
            'description': ('Generates an image mask selecting each label in '
                            'an image once'),
            'do background': 'If true include the background object (ID=0)',
            'multi_chromatic': False,
            'algorithm': alg_from_labels},
        'from channels': {
            'description': ('Generates a list of grayscale images from each '
                            'channel in input image'),
            'multi_chromatic': True,
            'algorithm': alg_from_channels}}

    options_list = ['do background']
    options_types = {'do background': bool}
    options_default = {'do background': True}

    parameters = node.parameters()
    parameters.set_string('algorithm', value=next(iter(algorithms)),
                          description='', label='Algorithm')
    ImageFiltering_abstract.generate_parameters(parameters, options_types,
                                                options_default)

    inputs = Ports([
        Image('source image', name='source')])
    outputs = Ports([
        Port.Custom('[image]', 'Resulting list of images', name='results')])
    __doc__ = ImageFiltering_abstract.generate_docstring(
        description, algorithms, options_list, inputs, outputs)

    def execute(self, node_context):
        image = node_context.input['source'].get_image()
        params = node_context.parameters
        alg_name = params['algorithm'].value
        results = node_context.output['results']
        alg = self.algorithms[alg_name]['algorithm']
        alg(image, results, params)


class ListToImage(ImageFiltering_abstract, node.Node):
    name = 'List to Image'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'image_list2image.svg'
    description = 'Generates an image based on a list of images'
    nodeid = 'syip.list2image'
    tags = Tags(Tag.ImageProcessing.Layers)

    def alg_concatenate(images, par):
        max_x, max_y = 0, 0
        channels = 0
        if len(images) == 0:
            return np.zeros((1, 1, 1))
        dtype = images[0].get_image().dtype
        for im_obj in images:
            im = im_obj.get_image()
            max_x = max(max_x, im.shape[1])
            max_y = max(max_y, im.shape[0])
            if len(im.shape) > 2:
                channels += im.shape[2]
            else:
                channels += 1
        result = np.zeros((max_y, max_x, channels), dtype=dtype)
        ch = 0
        for im_obj in images:
            im = im_obj.get_image()
            if len(im.shape) < 3:
                im = im.reshape(im.shape + (1,))
            result[:im.shape[0], :im.shape[1], ch:ch+im.shape[2]] = im
            ch += im.shape[2]
        return result

    algorithms = {
        'concatenate channels': {
            'description': ('Generates an image by concatenating all channels '
                            'in the input images. Resulting datatype given by '
                            'first image in the list'),
            'multi_chromatic': True,
            'algorithm': alg_concatenate}}

    options_list = ['do background']
    options_types = {'do background': bool}
    options_default = {'do background': True}

    parameters = node.parameters()
    parameters.set_string('algorithm', value=next(iter(algorithms)),
                          description='', label='Algorithm')
    ImageFiltering_abstract.generate_parameters(parameters, options_types,
                                                options_default)

    inputs = Ports([
        Port.Custom('[image]', 'Input list of images', name='inputs')
    ])
    outputs = Ports([
        Image('result image', name='result'),
    ])
    __doc__ = ImageFiltering_abstract.generate_docstring(
        description,
        algorithms, options_list, inputs, outputs)

    def execute(self, node_context):
        params = node_context.parameters
        output = node_context.output['result']
        inputs = node_context.input['inputs']

        alg_name = params['algorithm'].value
        alg = self.algorithms[alg_name]['algorithm']
        im = alg(inputs, params)
        output.set_image(im)
