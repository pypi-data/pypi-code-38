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
import matplotlib.pyplot as plt

from sympathy.api import node
from sympathy.api.nodeconfig import Ports
from sympathy.api.exceptions import sywarn, SyDataError

from skimage import color, exposure
from sylib.imageprocessing.image import Image
from sylib.imageprocessing.algorithm_selector import ImageFiltering_abstract
from sylib.imageprocessing.generic_filtering import GenericImageFiltering
from sylib.imageprocessing.color import grayscale_transform


API_URL = 'http://scikit-image.org/docs/0.13.x/api/'


def alg_greyscale(im, params):
    if len(im.shape) == 2:
        result = im
    elif im.shape[2] == 3 and params['luminance preserving'].value:
        result = im.dot(grayscale_transform)
    elif (im.shape[2] == 4 and
          params['luminance preserving'].value and
          params['preserve alpha'].value):
        result = np.zeros(im.shape[:2]+(2,))
        result[:, :, 0] = im[:, :, :3].dot(grayscale_transform)
        result[:, :, 1] = im[:, :, 3]
    elif im.shape[2] == 4 and not params['preserve alpha'].value:
        result = im[:, :, :3].dot(grayscale_transform)
    else:
        result = im.mean(axis=2).reshape(im.shape[:2]+(1,))
    return result


def alg_colourmap(im, params):
    if len(im.shape) >= 3 and im.shape[2] != 1:
        sywarn('Colourmap expects a single-channel input')
    if len(im.shape) >= 3:
        im = im[:, :, 0]
    cmap = plt.get_cmap(params['cmap'].value)
    try:
        cols = np.array(cmap.colors)
    except AttributeError:
        cols = cmap(np.linspace(0.0, 1.0, 256))
        if cols.shape[-1] == 4:
            cols = cols[:, :3]
    minv = np.nanmin(im)
    maxv = np.nanmax(im)
    im[np.isnan(im)] = minv
    im = np.round((len(cols)-1) * (im-minv) / (maxv-minv)).astype(np.int)
    return cols[im.ravel()].reshape(im.shape[:2]+(cols.shape[-1],))

def alg_hsv2rgb(im, params):
    if len(im.shape) != 3 or im.shape[2] != 3:
        raise SyDataError('Invalid number of channels in input image. '
                          'Must have exactly 3 channels.')
    max_val = np.max(im[:,:,2])
    if max_val >= 1.0 and max_val <= 1.0+1e-5:
        # Avoid error with value channel very close to 1.0
        # For this case the user probably meant to have it clipped
        # instead of wrap around
        im[:,:,2] = np.minimum(im[:,:,2], 1.0 - 1e-5)
    return color.hsv2rgb(im)

COLORSPACE_CONVERTERS = {
    'hsv2rgb': {
        'description': (
            'Interprets input channels as Hue-Saturation-Value (HSV) '
            'and outputs Red-Green-Blue (RGB) channels.'),
        'multi_chromatic': True,
        'url': API_URL+'skimage.color.html#skimage.color.hsv2rgb',
        'algorithm': alg_hsv2rgb
    },
    'rgb2hsv': {
        'description': (
            'Interprets input channels as Red-Green-Blue (RGB) '
            'and outputs Hue-Saturation-Value (HSV) channels.'),
        'multi_chromatic': True,
        'url': API_URL+'skimage.color.html#skimage.color.rgb2hsv',
        'algorithm': lambda im, par: color.rgb2hsv(im)
    },
    'rgb2xyz': {
        'description': (
            'Interprets input channels as sRGB and outputs '
            'CIE XYZ channels.'),
        'multi_chromatic': True,
        'url': API_URL+'skimage.color.html#skimage.color.rgb2xyz',
        'algorithm': lambda im, par: color.rgb2xyz(im)
    },
    'xyz2rgb': {
        'description': ('Interprets input channels as CIE XYZ '
                        'and outputs sRGB channels.'),
        'multi_chromatic': True,
        'url': API_URL+'skimage.color.html#skimage.color.xyz2rgb',
        'algorithm': lambda im, par: color.xyz2rgb(im)
    },
    'rgb2lab': {
        'description': (
            'Interprets input channels as sRGB and outputs '
            'CIE LAB channels.'),
        'multi_chromatic': True,
        'url': API_URL+'skimage.color.html#skimage.color.rgb2lab',
        'illuminant': 'CIE standard illumination spectrum',
        'observer': 'Aperture angle of observer',
        'algorithm': lambda im, par: (
            color.rgb2lab(im,
                          illuminant=par['illuminant'].value,
                          observer=par['observer'].value)),
    },
    'lab2rgb': {
        'description': (
            'Interprets input channels as sRGB and outputs '
            'CIE LAB channels.'),
        'multi_chromatic': True,
        'url': API_URL+'skimage.color.html#skimage.color.rgb2lab',
        'illuminant': 'CIE standard illumination spectrum',
        'observer': 'Aperture angle of observer',
        'algorithm': lambda im, par: (
            color.lab2rgb(im,
                          illuminant=par['illuminant'].value,
                          observer=par['observer'].value)),
    },
    'grey2cmap': {
        'description': (
            'Converts greyscale values after normalization and scaling '
            'from 0 - 255 into a matplotlib colourmap.'),
        'cmap': 'The colormap to use in conversion',
        'multi_chromatic': True,
        'algorithm': alg_colourmap,
        'url': ('https://matplotlib.org/'
                'examples/color/colormaps_reference.html')
    },
    'greyscale': {
        'description': 'Transforms RGB images into greyscale',
        'luminance preserving': (
            'Use weighted average based on separate luminosity of '
            'red-green-blue receptors in human eye.\nOnly works for three '
            'channel images'),
        'preserve alpha': (
            'Passes through channel 4 (alpha), '
            'otherwise it is treated as another channel affecting output'),
        'multi_chromatic': True,
        'algorithm': alg_greyscale
    },
}

COLORRANGE_CONVERTERS = {
    'gamma correction': {
        'description': (
            'Applies the correction:  '
            'Vout = scale Vin^gamma\nProcesses each channel separately'
        ),
        'scale': 'Constant scale factor applied after gamma correction',
        'gamma': (
            'Gamma factor applied to image.\n<1 increases intensities of '
            'mid-tones,\n>1 decreases intensities of mid-tones'
        ),
        'multi_chromatic': False,
        'url': API_URL+'skimage.exposure.html#skimage.exposure.adjust_gamma',
        'algorithm': (
            lambda im, par: exposure.adjust_gamma(
                im, gamma=par['gamma'].value, gain=par['scale'].value))
    },
    'log correction': {
        'description': (
            'Applies the correction:  '
            'Vout = scale log(1 + Vin)\n'
            'Processes each channel separately'),
        'scale': 'Constant scale factor applied after gamma correction',
        'inverse': (
            'Perform inverse log-correction instead (default false):\n'
            'Vout = scale (2^Vin - 1)'),
        'multi_chromatic': False,
        'url': API_URL+'skimage.exposure.html#skimage.exposure.adjust_log',
        'algorithm': (
            lambda im, par: exposure.adjust_log(
                im, gain=par['scale'].value, inv=par['inverse'].value))
    },
    'sigmoid': {
        'description': (
            'Performs Sigmoid correction on input image. '
            'Also known as contrast adjustment.\n'
            'Vout = 1/(1+exp(gain*(cutoff-Vin)))\n'
            'Processes each channel separately'),
        'cutoff': (
            'Shifts the characteristic curve for the sigmoid horizontally'
            '(default 0.5)'),
        'gain': (
            'Gain of sigmoid, affects rise time of curve (default 10.0)'),
        'inverse': (
            'Perform negative sigmoid correction instead (default false)'),
        'multi_chromatic': False,
        'url': API_URL+'skimage.exposure.html#skimage.exposure.adjust_sigmoid',
        'algorithm': (
            lambda im, par: exposure.adjust_sigmoid(
                im, gain=par['gain'].value, cutoff=par['cutoff'].value,
                inv=par['inverse'].value))
    },
    'histogram equalization': {
        'description': (
            'Improves contrast by stretching and equalizing the histogram'
        ),
        'bins': 'Number of bins in computed histogram (default 256)',
        'multi_chromatic': True,
        'url': API_URL+'skimage.exposure.html#skimage.exposure.equalize_hist',
        'algorithm': (
            lambda im, par: exposure.equalize_hist(
                im, nbins=par['bins'].value))
    },
    'adaptive histogram': {
        'description': (
            'Improves contrast by stretching and equalizing the histogram'
            'in a sliding window over the image'),
        'adaptive kernel size': (
            'Size of the sliding window. '
            'Must evenly divide both image width and height.'),
        'sigma': ('Clipping limit (normalized between 0 and 1). '
                  'Higher values give more contrast. (default 1.0)'),
        'bins': 'Number of bins in computed histogram (default 256)',
        'multi_chromatic': True,
        'url': (
            API_URL + 'skimage.exposure.html' +
            '#skimage.exposure.equalize_adapthist'),
        'algorithm': (
            lambda im, par: exposure.equalize_adapthist(
                im, kernel_size=par['adaptive kernel size'].value,
                clip_limit=par['sigma'].value, nbins=par['bins'].value))
    },
}

COLORSPACE_PARAMETERS = ['cmap', 'luminance preserving', 'illuminant', 'observer']
COLORSPACE_TYPES = {
    'cmap': ['viridis', 'Accent', 'Blues', 'BrBG', 'BuGn', 'BuPu',
             'CMRmap', 'Dark2', 'GnBu', 'Greens', 'Greys', 'OrRd',
             'Oranges', 'PRGn', 'Paired', 'Pastel1', 'Pastel2', 'PiYG',
             'PuBu', 'PuBuGn', 'PuOr', 'PuRd', 'Purples', 'RdBu', 'RdGy',
             'RdPu', 'RdYlBu', 'RdYlGn', 'Reds', 'Set1', 'Set2', 'Set3',
             'Spectral', 'Vega10', 'Vega20', 'Vega20b', 'Vega20c',
             'Wistia', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd', 'afmhot',
             'autumn', 'binary', 'bone', 'brg', 'bwr', 'cool', 'coolwarm',
             'copper', 'cubehelix', 'gist_earth', 'gist_gist_gray',
             'gist_gist_heat', 'gist_gist_ncar', 'gist_nbow', 'gist_stern',
             'gist_gist_yarg', 'gist_gnuplot', 'gnuplot2', 'gray', 'hot',
             'hsv', 'inferno', 'jet', 'magma', 'nipy_spectral',
             'nipy_ocean', 'pink', 'plasma', 'prism', 'rainbow',
             'seismic', 'spectral', 'spring', 'summer', 'tab10',
             'tab20', 'tab20b', 'tab20c', 'terrain', 'winter'],
    'illuminant': ['A', 'D50', 'D55', 'D65', 'D75', 'E'],
    'observer': ['2', '10'],
    'luminance preserving': bool,
}
COLORSPACE_DEFAULTS = {
    'cmap': 'viridis', 'luminance preserving': True,
    'illuminant': 'D65', 'observer': '2',
}

COLORRANGE_PARAMETERS = [
    'scale', 'gamma', 'inverse', 'cutoff', 'gain', 'bins',
    'adaptive kernel size', 'sigma',
]
COLORRANGE_TYPES = {
    'gamma': float, 'inverse': bool,
    'adaptive kernel size': int, 'cutoff': float, 'scale': float,
    'gain': float, 'sigma': float, 'bins': int}
COLORRANGE_DEFAULTS = {
    'gamma': 1.0, 'inverse': False,
    'adaptive kernel size': 4, 'cutoff': 0.5,
    'scale': 1.0, 'gain': 10.0, 'sigma': 1.0, 'bins': 256
}


class ColorSpaceConversion(ImageFiltering_abstract, GenericImageFiltering,
                           node.Node):
    name = 'Color space conversion'
    icon = 'image_colorspace.svg'
    description = (
        'Converts each pixel in a multi-channel image into another '
        'colour space')
    nodeid = 'syip.color_space_conversion'
    copyright = "(C) 2017 Combine Control Systems AB"

    algorithms = COLORSPACE_CONVERTERS
    options_list = COLORSPACE_PARAMETERS
    options_types = COLORSPACE_TYPES
    options_default = COLORSPACE_DEFAULTS

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


class ColorRangeConversion(ImageFiltering_abstract, GenericImageFiltering,
                           node.Node):
    name = 'Color range conversion'
    icon = 'image_color_range.svg'
    description = (
        'Changes the range and distribution of values for all pixels')
    nodeid = 'syip.color_range_conversion'
    copyright = "(C) 2017 Combine Control Systems AB"

    algorithms = COLORRANGE_CONVERTERS
    options_list = COLORRANGE_PARAMETERS
    options_types = COLORRANGE_TYPES
    options_default = COLORRANGE_DEFAULTS

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




