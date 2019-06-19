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
from skimage import transform
from sylib.imageprocessing.image import Image
from sylib.imageprocessing.algorithm_selector import ImageFiltering_abstract


class ExtractData(ImageFiltering_abstract, node.Node):
    name = 'Extract Image Data'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'image_and_table_to_table.svg'
    description = (
        'Extracts table data from an image based on tabular input data')
    nodeid = 'syip.extractdata'
    tags = Tags(Tag.ImageProcessing.Extract)

    def alg_integrate(im, table, params, result):
        def clamp(arr, axis):
            return np.maximum(0,
                              np.minimum(arr.astype('int'), im.shape[axis]-1))

        result.set_name("Image integrals")
        channels = 1 if len(im.shape) < 3 else im.shape[2]
        for channel in range(channels):
            start_coords = zip(
                clamp(table.get_column_to_array(params['start y'].value), 0),
                clamp(table.get_column_to_array(params['start x'].value), 1)
            )
            end_coords = zip(
                clamp(table.get_column_to_array(params['end y'].value), 0),
                clamp(table.get_column_to_array(params['end x'].value), 1)
            )
            start_coords = list(start_coords)
            end_coords = list(end_coords)
            integrals = transform.integrate(
                im[:, :, channel], start_coords, end_coords
            )
            result.set_column_from_array(
                "ch{0}_integral".format(channel), integrals
            )

    def alg_pixelvalue(im, table, params, result):
        result.set_name("Image pixels")
        channels = 1 if len(im.shape) < 3 else im.shape[2]
        for channel in range(channels):
            xs = table.get_column_to_array(params['x'].value).astype('int')
            ys = table.get_column_to_array(params['y'].value).astype('int')
            values = im[ys, xs, channel]
            result.set_column_from_array("ch{0}_values".format(channel), values)

    algorithms = {
        'integrate': {
            'description': (
                'Computes the integral on all points in a square between two'
                'corner points,\nmust have an integral image as input.'
                'Operates on each channel separately'
            ),
            'start x': (
                'Column containing starting points on X axis for integral'
            ),
            'start y': (
                'Column containing starting points on Y axis for integral'
            ),
            'end x': 'Column containing ending points on X axis for integral',
            'end y': 'Column containing ending points on X axis for integral',
            'algorithm': alg_integrate
        },
        'pixel values': {
            'description': (
                'Extracts the pixel values at positions given by X and Y'
                'table rows'
            ),
            'x': 'Column containing X coordinates of the points to extract',
            'y': 'Column containing Y coordinates of the points to extract',
            'algorithm': alg_pixelvalue
        },
    }
    options_list    = [
        'start x', 'start y', 'end x', 'end y', 'x', 'y',
    ]
    options_types   = {
        'x': str,
        'y': str,
        'start x': str,
        'start y': str,
        'end x': str,
        'end y': str,
    }
    options_default = {
        'x': 'x',
        'y': 'y',
        'start x': 'x0',
        'start y': 'y0',
        'end x': 'x1',
        'end y': 'y1',
    }

    parameters = node.parameters()
    parameters.set_string(
        'algorithm', value=next(iter(algorithms)),
        description='', label='Algorithm'
    )
    ImageFiltering_abstract.generate_parameters(
        parameters, options_types, options_default
    )

    inputs = Ports([
        Image('Source image to extract data from', name='source_im'),
        Port.Table(
            'Table with parameters for data extraction', name='source_table'
        ),
    ])
    outputs = Ports([
        Port.Table('Table with results', name='result'),
    ])
    __doc__ = ImageFiltering_abstract.generate_docstring(
        description, algorithms, options_list, inputs, outputs
    )

    def execute(self, node_context):
        source_im = node_context.input['source_im'].get_image()
        source_table = node_context.input['source_table']
        params = node_context.parameters
        alg_name = params['algorithm'].value

        if len(source_im.shape) < 3:
            source_im = source_im.reshape(source_im.shape+(1,))

        alg = self.algorithms[alg_name]['algorithm']
        result = node_context.output['result']
        result.set_name('Statistics')
        alg(source_im, source_table, params, result)
