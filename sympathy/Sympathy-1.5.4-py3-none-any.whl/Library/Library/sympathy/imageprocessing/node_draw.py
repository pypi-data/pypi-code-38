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
import skimage
from skimage import draw
from sylib.imageprocessing.image import Image
from sylib.imageprocessing.algorithm_selector import ImageFiltering_abstract


class ImageDraw(ImageFiltering_abstract, node.Node):
    name = 'Draw on Image'
    author = 'Mathias Broxvall'
    copyright = "(C) 2017 Combine Control Systems AB"
    version = '0.1'
    icon = 'image_draw.svg'
    description = 'Annotates an image with drawings based on tabular data.'
    nodeid = 'syip.imagedraw'
    tags = Tags(Tag.ImageProcessing.ImageManipulation)

    @staticmethod
    def column_value(s, table, N):
        """Get the intended parameter value from a string.

        Convert the given parameter string s to a number if possible, or
        return the column with that name from the table
        """
        try:
            return np.ones(N) * float(s)
        except ValueError:
            return table.get_column_to_array(s)

    @staticmethod
    def get_colors(params, table, N):
        """Draw coordinates with color given by parameters"""
        try:
            red = np.ones(N) * float(params['red color'].value)
        except ValueError:
            red = table.get_column_to_array(params['red color'].value)
        try:
            green = np.ones(N) * float(params['green color'].value)
        except ValueError:
            green = table.get_column_to_array(params['green color'].value)
        try:
            blue = np.ones(N) * float(params['blue color'].value)
        except ValueError:
            blue = table.get_column_to_array(params['blue color'].value)
        try:
            alpha = np.ones(N) * float(params['alpha value'].value)
        except ValueError:
            alpha = table.get_column_to_array(params['alpha value'].value)
        colors = [red, green, blue, alpha]
        return colors

    @staticmethod
    def set_colors(image, coords, row, colors):
        if len(image.shape) < 3 or image.shape[2] == 1:
            draw.set_color(image, coords,
                           [colors[0][row]],
                           alpha=colors[3][row])
        elif image.shape[2] == 2:
            draw.set_color(
                image, coords,
                [colors[0][row], colors[1][row]],
                alpha=colors[3][row]
            )
        elif image.shape[2] == 3:
            draw.set_color(
                image, coords,
                [colors[0][row], colors[1][row], colors[2][row]],
                alpha=colors[3][row]
            )
        elif image.shape[2] == 4:
            draw.set_color(
                image, coords,
                [colors[0][row], colors[1][row],
                 colors[2][row], colors[3][row]],
                alpha=colors[3][row]
            )
        else:
            pass

    def alg_circles(image, table, params):
        xs = table.get_column_to_array(params['x'].value)
        ys = table.get_column_to_array(params['y'].value)
        radii  = ImageDraw.column_value(
            params['radius'].value, table, xs.shape[0]
        )
        colors = ImageDraw.get_colors(params, table, ys.shape[0])
        for row in range(ys.shape[0]):
            x, y = draw.circle_perimeter(
                int(ys[row]), int(xs[row]), int(radii[row]), shape=image.shape
            )
            ImageDraw.set_colors(image, (x, y), row, colors)
        return image

    def alg_filled_circles(image, table, params):
        xs = table.get_column_to_array(params['x'].value)
        ys = table.get_column_to_array(params['y'].value)
        radii  = ImageDraw.column_value(
            params['radius'].value, table, xs.shape[0]
        )
        colors = ImageDraw.get_colors(params, table, ys.shape[0])
        for row in range(ys.shape[0]):
            x, y = draw.circle(
                int(ys[row]), int(xs[row]), int(radii[row]), shape=image.shape
            )
            ImageDraw.set_colors(image, (x, y), row, colors)
        return image

    def alg_lines(image, table, params):
        x1s = table.get_column_to_array(params['x'].value)
        y1s = table.get_column_to_array(params['y'].value)
        x2s = table.get_column_to_array(params['x2'].value)
        y2s = table.get_column_to_array(params['y2'].value)
        colors = ImageDraw.get_colors(params, table, x1s.shape[0])
        for row in range(y1s.shape[0]):
            x, y = draw.line(
                int(y1s[row]), int(x1s[row]), int(y2s[row]), int(x2s[row])
            )
            ImageDraw.set_colors(image, (x, y), row, colors)
        return image

    def alg_symbols(image, table, params):
        x0s    = table.get_column_to_array(params['x'].value)
        y0s    = table.get_column_to_array(params['y'].value)
        Ns     = ImageDraw.column_value(
            params['N'].value, table, x0s.shape[0]
        ).astype(np.int)
        radii  = ImageDraw.column_value(
            params['radius'].value, table, x0s.shape[0]
        )
        colors = ImageDraw.get_colors(params, table, x0s.shape[0])
        for row in range(y0s.shape[0]):
            N = Ns[row]
            r = radii[row]
            x0 = int(x0s[row])
            y0 = int(y0s[row])
            convex = N < 0
            N = np.abs(N)
            poly_x = np.array([])
            poly_y = np.array([])
            for n in range(N+1):
                alpha1 = (2*np.pi*(n+0.5))/N
                x1, y1  = int(x0+r*np.sin(alpha1)), int(y0+r*np.cos(alpha1))
                poly_x = np.append(poly_x, x1)
                poly_y = np.append(poly_y, y1)
                if convex:
                    alpha2 = alpha1 + np.pi/N
                    x2 = int(x0+r*np.sin(alpha2)/4.)
                    y2 = int(y0+r*np.cos(alpha2)/4.)
                    poly_x = np.append(poly_x, x2)
                    poly_y = np.append(poly_y, y2)
            ImageDraw.set_colors(
                image, draw.polygon(poly_y, poly_x), row, colors
            )
        return image

    default_parameters = {
        'red color': (
            'A number (0-1) or column name containing colors for first image'
            'channel.'
        ),
        'green color': (
            'A number (0-1) or column name containing colors for second image'
            'channel, ignored for non RGB images'
        ),
        'blue color': (
            'A number (0-1) or column name containing colors for third image'
            'channel, ignored for non RGB images'
        ),
        'alpha value': (
            'A number (0-1) or column name containing alpha values used for'
            'blending the drawings over the image.\n'
            '   1.0 is opaque, 0.0 transparent'
        ),
        'force colors': (
            'If true then forces output to be RGB'
        ),
    }
    algorithms = {
        'circle': dict({
            'description': (
                'Draws (non-filled) circles from given X,Y points with given'
                'radii'
            ),
            'x': 'Column name containing X-coordinates',
            'y': 'Column name containing Y-coordinates',
            'radius': 'Column name containing radii',
            'algorithm': alg_circles,
        }, **default_parameters),
        'symbols': dict({
            'description': (
                'Draws a symbol defined by number of vertices. Negative values'
                'are drawn as convex objects. Eg, triangles have N=3,'
                'squares N=4, hexagons N=6, stars N=-6'
            ),
            'x': 'Column name containing X-coordinates',
            'y': 'Column name containing Y-coordinates',
            'N': 'Column name containing number of vertices',
            'radius': 'Column name containing radii',
            'algorithm': alg_symbols,
        }, **default_parameters),
        'filled circle': dict({
            'description': (
                'Draws filled circles from given X,Y points with given radii'
            ),
            'x': 'Column name containing X-coordinates',
            'y': 'Column name containing Y-coordinates',
            'radius': 'Column name containing radii',
            'algorithm': alg_filled_circles,
        }, **default_parameters),
        'lines': dict({
            'description': (
                'Draws lines from coordinates (X,Y) to coordinates (X2,Y2)'
            ),
            'x': 'Column name containing X-coordinates',
            'y': 'Column name containing Y-coordinates',
            'x2': 'Column name containing X2-coordinates',
            'y2': 'Column name containing Y2-coordinates',
            'algorithm': alg_lines,
        }, **default_parameters),
    }

    options_list    = [
        'x', 'y', 'x2', 'y2', 'radius', 'red color', 'green color',
        'blue color', 'alpha value', 'N', 'force colors',
    ]
    options_types   = {
        'x': str,
        'y': str,
        'x2': str,
        'y2': str,
        'N': str,
        'radius': str,
        'red color': str,
        'green color': str,
        'blue color': str,
        'alpha value': str,
        'force colors': bool,
    }
    options_default = {
        'x': 'X',
        'y': 'Y',
        'x2': 'X2',
        'y2': 'Y2',
        'N': 'N',
        'radius': 'radius',
        'red color': '1.0',
        'green color': '1.0',
        'blue color': '0.5',
        'alpha value': '1.0',
        'force colors': False,
    }

    parameters = node.parameters()
    parameters.set_string(
        'algorithm', value=next(iter(algorithms)), description='', label='Algorithm'
    )
    ImageFiltering_abstract.generate_parameters(
        parameters, options_types, options_default
    )

    inputs = Ports([
        Image('Image to draw on', name='image'),
        Port.Table('Table used for drawing', name='table'),
    ])
    outputs = Ports([
        Image('Resulting image', name='output'),
    ])
    __doc__ = ImageFiltering_abstract.generate_docstring(
        description, algorithms, options_list, inputs, outputs
    )

    def execute(self, node_context):

        image  = node_context.input['image'].get_image()
        table  = node_context.input['table']
        params = node_context.parameters
        alg_name = params['algorithm'].value
        alg      = self.algorithms[alg_name]['algorithm']

        if len(image.shape) < 3:
            image = image.reshape(image.shape+(1,))

        if params['force colors'].value:
            if image.shape[2] == 1:
                image = skimage.color.gray2rgb(image[:,:,0])
            elif image.shape[2] >= 3:
                image = image[:,:,:3]

        result   = alg(image, table, params)
        node_context.output['output'].set_image(result)
