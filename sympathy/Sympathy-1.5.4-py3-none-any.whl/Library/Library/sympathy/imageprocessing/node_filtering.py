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
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, deprecated_node

import numpy as np
import matplotlib.pyplot as plt
from skimage import filters, feature, exposure, color, morphology, transform
from sylib.imageprocessing.image import Image
from sylib.imageprocessing.algorithm_selector import ImageFiltering_abstract
from sylib.imageprocessing.color import grayscale_transform
from sympathy.api.exceptions import SyNodeError, sywarn
import scipy.ndimage.filters


def table_to_image(table):
    data = [column.data for column in table.cols()]
    return np.column_stack(data)


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
        im, shape, order=params['interpolation degree'].value)
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


def alg_convolution(im, params, tables):
    if len(tables) == 0:
        raise SyNodeError(
            'Convolution filters require second input for kernel '
            '(right-click node to create new input)')
    kernel = table_to_image(tables[0])
    return scipy.ndimage.filters.convolve(
        im, kernel, mode=params['border mode'].value,
        cval=params['k'].value)


def alg_generic_colourspace(im, params, tables):
    if len(tables) == 0:
        raise SyNodeError(
            'Generic colourspace conversion require second table input '
            '(right-click node to create new input)')
    conv = table_to_image(tables[0])
    print("Conv: ", conv)
    rows = conv.shape[0]
    out = np.zeros(im.shape[:2]+(rows,))
    for out_ch in range(rows):
        out[:, :, out_ch] = np.dot(im, conv[out_ch, :])
    return out


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


@deprecated_node('1.6.0', 'a specific Image Manipulation node')
class ImageFiltering_deprecated(ImageFiltering_abstract, node.Node):
    name = 'Filter Image (deprecated)'
    author = 'Mathias Broxvall'
    copyright = "(C) 2017 Combine Control Systems AB"
    version = '0.1'
    icon = 'image_filtering.svg'
    description = (
        'Filters one image into another using one of a number of predefined'
        'filtering operations. The implemented filters are to a large extent'
        'based on `scikit-image`, but some filters are not from this package.'
        '\n\n'
        'This node is DEPRECATED, use instead the more specific nodes such as:'
        'Edge Detection, Corner Detection, Threshold, etc.')
    nodeid = 'syip.imagefiltering'
    tags = Tags(Tag.ImageProcessing.ImageManipulation)

    convex_hull_desc = (
        'The convex hull is the set of pixels included in the smallest convex'
        'polygon that surround all white pixels in the input image.'
    )
    interpolation_degree_desc = (
        'Degree of polynomial (0 - 5) used for interpolation.\n'
        '0 - no interpolation, 1 - bi-linear interpolation, '
        '3 - bi-cubic interpolation'
    )
    api = 'http://scikit-image.org/docs/0.13.x/api/'
    algorithms = {
        'canny': {
            'description': 'Canny edge detection.',
            'sigma': 'Standard deviation of gaussian kernel (default 1.0)',
            'multi_chromatic': False,
            'url': api+'skimage.feature.html#skimage.feature.canny',
            'algorithm': (
                lambda im, par: feature.canny(im, sigma=par['sigma'].value))
        },
        'corner, FAST': {
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
            'url': api+'skimage.feature.html#skimage.feature.corner_fast',
            'algorithm': (
                lambda im, par: feature.corner_fast(
                    im, n=par['n'].value, threshold=par['threshold'].value))
        },
        'corner, harris': {
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
            'url': api+'skimage.feature.html#skimage.feature.corner_harris',
            'algorithm': (
                lambda im, par: feature.corner_harris(
                    im,
                    k=par['k'].value,
                    eps=par['eps'].value,
                    sigma=par['sigma'].value,
                    method=par['harris method'].value))
        },
        'corner, KR': {
            'description': (
                'Compute Kitchen-Rosenfeld corner measure response image'),
            'border mode': 'Method for handling values outside the borders',
            'k': 'Value outside image borders when method constant is used.',
            'multi_chromatic': False,
            'url': (
                api + 'skimage.feature.html' +
                '#skimage.feature.corner_kitchen_rosenfeld'),
            'algorithm': (
                lambda im, par: feature.corner_kitchen_rosenfeld(
                    im, cval=par['k'].value, mode=par['border mode'].value))
        },
        'corner, moravec': {
            'description': (
                'Compute Moravec corner measure response image.\n\n '
                'This is one of the simplest corner detectors and is '
                'comparatively fast but has several limitations '
                '(e.g. not rotation invariant).'),
            'window size': 'Size of window used during calculations',
            'multi_chromatic': False,
            'url': api+'skimage.feature.html#skimage.feature.corner_moravec',
            'algorithm': (
                lambda im, par: feature.corner_moravec(
                    im, window_size=par['window size'].value))
        },
        'corner, ST': {
            'description': (
                'Compute Shi-Tomasi (Kanade-Tomasi) corner measure response'
                'image. Uses information from auto-correlation matrix'),
            'sigma': (
                'Standard deviation used for the Gaussian kernel, which is '
                'used as weighting function for the auto-correlation matrix.'),
            'multi_chromatic': False,
            'url': (
                api+'skimage.feature.html#skimage.feature.corner_shi_tomasi'),
            'algorithm': (
                lambda im, par: feature.corner_shi_tomasi(
                    im, sigma=par['sigma'].value))
        },
        'gaussian': {
            'description': 'Two-dimensional Gaussian filter',
            'sigma-x': 'Standard deviation of gaussian filter along X-axis',
            'sigma-y': 'Standard deviation of gaussian filter along Y-axis',
            'border mode': 'Determines how the array borders are handled',
            'k': 'Value outside image borders when method constant is used.',
            'multi_chromatic': False,
            'url': api+'skimage.filters.html#skimage.filters.gaussian',
            'algorithm': (
                lambda im, par: filters.gaussian(
                    im, cval=par['k'].value, mode=par['border mode'].value,
                    sigma=(par['sigma-x'].value, par['sigma-y'].value)))
        },
        'edges, prewitt': {
            'description': (
                'Find edges using the Prewitt transform as one of, or '
                'combination of horizontal and vertical prewitt convolutions'),
            'horizontal/vertical': (
                'Select orientation for transform, '
                'if both then mean square of both will be used'),
            'multi_chromatic': False,
            'url': api+'skimage.filters.html#skimage.filters.prewitt_h',
            'algorithm': alg_prewitt
        },
        'edges, scharr': {
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
            'url': api+'skimage.filters.html#skimage.filters.scharr_h',
            'algorithm': alg_scharr
        },
        'edges, sobel': {
            'description': (
                'Find edges using the Sobel transform as one of, or '
                'combination of horizontal and vertical prewitt '
                'convolutions.'),
            'horizontal/vertical': (
                'Select orientation for transform, '
                'if both then mean square of both will be used'),
            'multi_chromatic': False,
            'url': api+'skimage.filters.html#skimage.filters.sobel_h',
            'algorithm': alg_sobel
        },
        'edges, roberts': {
            'description': "Find edges using Robert's cross operator.",
            'positive/negative diagonal': 'Select orientation for transform',
            'multi_chromatic': False,
            'url': api+'skimage.filters.html#skimage.filters.roberts_pos_diag',
            'algorithm': alg_roberts
        },
        'edges, laplace': {
            'description': "Find edges using the Laplace operator.",
            'kernel size': 'Kernel size of the discrete Laplacian operator',
            'multi_chromatic': False,
            'url': api+'skimage.filters.html#skimage.filters.laplace',
            'algorithm': (
                lambda im, par: filters.laplace(
                    im, ksize=par['kernel size'].value))
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
            'algorithm': (
                lambda im, par: (
                    im.astype(np.float)-np.min(im))/(np.max(im)-np.min(im)))
        },
        'adjust, gamma correction': {
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
            'url': api+'skimage.exposure.html#skimage.exposure.adjust_gamma',
            'algorithm': (
                lambda im, par: exposure.adjust_gamma(
                    im, gamma=par['gamma'].value, gain=par['scale'].value))
        },
        'adjust, log correction': {
            'description': (
                'Applies the correction:  '
                'Vout = scale log(1 + Vin)\n'
                'Processes each channel separately'),
            'scale': 'Constant scale factor applied after gamma correction',
            'inverse': (
                'Perform inverse log-correction instead (default false):\n'
                'Vout = scale (2^Vin - 1)'),
            'multi_chromatic': False,
            'url': api+'skimage.exposure.html#skimage.exposure.adjust_log',
            'algorithm': (
                lambda im, par: exposure.adjust_log(
                    im, gain=par['scale'].value, inv=par['inverse'].value))
        },
        'adjust, sigmoid': {
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
            'url': api+'skimage.exposure.html#skimage.exposure.adjust_sigmoid',
            'algorithm': (
                lambda im, par: exposure.adjust_sigmoid(
                    im, gain=par['gain'].value, cutoff=par['cutoff'].value,
                    inv=par['inverse'].value))
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
        'adjust, histogram equalization': {
            'description': (
                'Improves contrast by stretching and equalizing the histogram'
            ),
            'bins': 'Number of bins in computed histogram (default 256)',
            'multi_chromatic': True,
            'url': api+'skimage.exposure.html#skimage.exposure.equalize_hist',
            'algorithm': (
                lambda im, par: exposure.equalize_hist(
                    im, nbins=par['bins'].value))
        },
        'adjust, adaptive histogram': {
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
                api + 'skimage.exposure.html' +
                '#skimage.exposure.equalize_adapthist'),
            'algorithm': (
                lambda im, par: exposure.equalize_adapthist(
                    im, kernel_size=par['adaptive kernel size'].value,
                    clip_limit=par['sigma'].value, nbins=par['bins'].value))
        },
        'color, hsv2rgb': {
            'description': (
                'Interprets input channels as Hue-Saturation-Value (HSV) '
                'and outputs Red-Green-Blue (RGB) channels.'),
            'multi_chromatic': True,
            'url': api+'skimage.color.html#skimage.color.hsv2rgb',
            'algorithm': lambda im, par: color.hsv2rgb(im)
        },
        'color, rgb2hsv': {
            'description': (
                'Interprets input channels as Red-Green-Blue (RGB) '
                'and outputs Hue-Saturation-Value (HSV) channels.'),
            'multi_chromatic': True,
            'url': api+'skimage.color.html#skimage.color.rgb2hsv',
            'algorithm': lambda im, par: color.rgb2hsv(im)
        },
        'color, rgb2xyz': {
            'description': (
                'Interprets input channels as sRGB and outputs '
                'CIE XYZ channels.'),
            'multi_chromatic': True,
            'url': api+'skimage.color.html#skimage.color.rgb2xyz',
            'algorithm': lambda im, par: color.rgb2xyz(im)
        },
        'color, xyz2rgb': {
            'description': ('Interprets input channels as CIE XYZ '
                            'and outputs sRGB channels.'),
            'multi_chromatic': True,
            'url': api+'skimage.color.html#skimage.color.xyz2rgb',
            'algorithm': lambda im, par: color.xyz2rgb(im)
        },
        'color, generic': {
            'description': (
                'Generic conversion from one colour space to another. '
                'Requires secondary input (right click to add) with table.'
                'Each row row of table corresponds to one output colour. '
                'Number of columns must match number of channels in input '
                'image.'),
            'multi_chromatic': True,
            'operands': True,
            'algorithm': alg_generic_colourspace
        },
        'color, grey2cmap': {
            'description': (
                'Converts greyscale values after normalization and scaling '
                'from 0 - 255 into a matplotlib colourmap.'),
            'cmap': 'The colormap to use in conversion',
            'multi_chromatic': True,
            'algorithm': alg_colourmap,
            'url': ('https://matplotlib.org/'
                    'examples/color/colormaps_reference.html')
        },
        'threshold, basic': {
            'description': 'Compares each channel with a threshold',
            'threshold': 'Threshold value to compare with',
            'multi_chromatic': False,
            'algorithm': lambda im, par: im >= par['threshold'].value
        },
        'threshold, automatic': {
            'description': (
                'Performs global thresholding based a selection of automatic '
                'algorithms with none or few parameters'),
            'auto threshold method': (
                'Method used for calculating threshold'),
            'url': (
                api+'skimage.filters.html'),
            'algorithm': alg_auto_threshold,
            'multi_chromatic': False,
        },
        'threshold, adaptive': {
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
                api+'skimage.filters.html#skimage.filters.threshold_local'),
            'algorithm': lambda im, par: im > filters.threshold_local(
                im, par['kernel size'].value,
                method=par['threshold method'].value,
                offset=par['offset'].value,
                param=par['sigma'].value)
        },
        'convex hull, image': {
            'description': (
                'Computes the convex hull of a binary image.\n' +
                convex_hull_desc),
            'multi_chromatic': False,
            'url': (
                api+'skimage.morphology.html'
                '#skimage.morphology.convex_hull_image'),
            'algorithm': lambda im, par: morphology.convex_hull_image(im)
        },
        'convex hull, objects': {
            'description': (
                'Computes the convex hull of each object in a binary image.\n' +
                convex_hull_desc +
                '\nThis function uses labeling to define unique objects, finds'
                'the convex hull of each using convex_hull_image,\nand '
                'combines these regions with logical OR. Be aware the convex'
                'hulls of unconnected objects may overlap in the result'),
            'multi_chromatic': False,
            'url': (
                api + 'skimage.morphology.html'
                '#skimage.morphology.convex_hull_object'),
            'algorithm': lambda im, par: morphology.convex_hull_object(im)
        },
        'morphology, skeletonize': {
            'description': (
                'Returns the skeleton of a binary image. '
                'Thinning is used to reduce each connected component in a '
                'binary image to a single-pixel wide skeleton.'),
            'multi_chromatic': False,
            'url': (
                api+'skimage.morphology.html#skimage.morphology.skeletonize'),
            'algorithm': lambda im, par: morphology.skeletonize(im)
        },
        'morphology, labeling': {
            'description': (
                'Creates a unique integer label for each connected component '
                'in an integer valued or binary image.'),
            'diagonal neighborhood': (
                'If true then also consider diagonals for connectivity'),
            'multi_chromatic': False,
            'url': api+'skimage.morphology.html#skimage.morphology.label',
            'algorithm': lambda im, par: morphology.label(
                im,
                connectivity=2 if par['diagonal neighborhood'].value else 1)
        },
        'morphology, remove small holes': {
            'description': (
                'Removes small holes from an integer or boolean image.'),
            'diagonal neighborhood': (
                'If true then also consider diagonals for connectivity'),
            'n': 'Maximum size in pixels of areas to remove (default 64)',
            'multi_chromatic': False,
            'url': (
                api+'skimage.morphology.html'
                '#skimage.morphology.remove_small_holes'),
            'algorithm': lambda im, par: morphology.remove_small_holes(
                im, min_size=par['n'].value,
                connectivity=2 if par['diagonal neighborhood'].value else 1)
        },
        'morphology, remove small objects': {
            'description': (
                'Removes connected components smaller than the given size.'),
            'diagonal neighborhood': (
                'If true then also consider diagonals for connectivity'),
            'n': 'Maximum size in pixels of areas to remove (default 64)',
            'multi_chromatic': False,
            'url': (
                api+'skimage.morphology.html'
                '#skimage.morphology.remove_small_objects'),
            'algorithm': lambda im, par: morphology.remove_small_objects(
                im, min_size=par['n'].value,
                connectivity=2 if par['diagonal neighborhood'].value else 1)
        },
        'transform, to integer': {
            'description': 'Converts all channels into integer data',
            'multi_chromatic': True,
            'algorithm': lambda im, par: im.astype('int64')
        },
        'transform, resize': {
            'description': 'Resizes an image to match the given dimensions',
            'width': 'The new width of the image',
            'height': 'The new height of the image',
            'interpolation degree': interpolation_degree_desc,
            'multi_chromatic': True,
            'aspect': 'Preserve aspect ratio (gives smaller size on one axis)',
            'padding': (
                'Adds padding to fill out full width/height after '
                'aspect-correct scaling'),
            'url': api+'skimage.transform.html#skimage.transform.resize',
            'algorithm': alg_resize
        },
        'transform, rescale': {
            'description': 'Rescales an image by a given factor',
            'scale x': 'Scale factor along X direction (horizontal)',
            'scale y': 'Scale factor along Y direction (vertical)',
            'interpolation degree': interpolation_degree_desc,
            'multi_chromatic': True,
            'url': api+'skimage.transform.html#skimage.transform.rescale',
            'algorithm': lambda im, par: transform.rescale(
                im, (par['scale y'].value, par['scale x'].value),
                mode='constant',
                multichannel=True,
                anti_aliasing=True,
                order=par['interpolation degree'].value)
        },
        'transform, rotate': {
            'description': 'Rotates an image',
            'angle': 'Angular degrees to rotate clockwise',
            'resize': (
                'If true new image dimensions are calculated '
                'to exactly fit the image'),
            'multi_chromatic': True,
            'url': api+'skimage.transform.html#skimage.transform.rotate',
            'algorithm': lambda im, par: transform.rotate(
                im, par['angle'].value, resize=par['resize'].value)
        },
        'transform, padding': {
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
        'transform, crop': {
            'description': 'Crops the image to the given rectanglular area',
            'x': 'Left edge of image',
            'y': 'Top edge of image',
            'width': 'Width of image',
            'height': 'Height of image',
            'multi_chromatic': False,
            'algorithm': alg_crop_image,
        },
        'integral image': {
            'description': (
                'Creates the integral image of the input.\n'
                'An integral image contains at coordinate (m,n) the sum of '
                'all values above and to the left of it.\n '
                '  S(m,n) = sum(im[0:m, 0:n])'),
            'multi_chromatic': False,
            'url': (
                api+'skimage.feature.html'
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
                api+'skimage.feature.html'
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
        'convolution': {
            'description': (
                'Convolves the input image with a kernel given by second '
                'input as a table (right-click on node to add second '
                'operand input)'),
            'border mode': 'Method for handling border of image',
            'k': 'Value to give as input at borders when mode=constant',
            'multi_chromatic': False,
            'operands': True,
            'algorithm': alg_convolution,
        },

        # 'threshold, histogram min': {
        #     'description': ('The histogram of the image is computed and '
        #                     'smoothed until there are only two maxima. Then '
        #                     'the minimum in between is the threshold value'),
        #     'bins': 'Number of bins in computed histogram (default 256)',
        #     'histogram selection': 'Selected threshold from histogram',
        #     'multi_chromatic': False,
        #     'url': (
        #         api+'skimage.filters.html'
        #         '#threshold-minimum'),
        #     'algorithm': lambda im, par: im > filters.threshold_minimum (
        #         im, nbins=par['bins'].value,
        #         bias=par['histogram selection'].value)
        # },
        # 'thin': {
        #     'description': (
        #         'Performs morphological thinning of binary image by making '
        #         'multiple passes over the image,\nremoving pixels matching a'
        #         'set of criteria designed to thin connected regions while '
        #         'preserving connectivity'),
        #     'url': (
        #         api+'skimage.morphology'
        #         '#thin'),
        #     'multi_chromatic': False,
        #     'algorithm': lambda im, par: morphology.thin(im)
        # },

    }

    options_list = [
        'x', 'y', 'width', 'height', 'n', 'sigma',
        'sigma-x', 'sigma-y', 'threshold', 'eps', 'window size',
        'border mode', 'k', 'harris method', 'horizontal/vertical',
        'scale', 'offset', 'gamma', 'positive/negative diagonal',
        'kernel size', 'adaptive kernel size', 'luminance preserving',
        'preserve alpha', 'maximum', 'minimum', 'inverse', 'cutoff',
        'gain', 'bins', 'threshold method', 'histogram selection',
        'diagonal neighborhood', 'interpolation degree', 'scale x',
        'scale y', 'angle', 'resize', 'add alpha', 'aspect', 'padding', 'cmap',
        'auto threshold method']
    options_types   = {
        'n': int,
        'width': int,
        'height': int,
        'x': int,
        'y': int,
        'aspect': bool,
        'interpolation degree': int,
        'scale x': float,
        'scale y': float,
        'sigma': float,
        'sigma-x': float,
        'sigma-y': float,
        'scale': float,
        'offset': float,
        'gamma': float,
        'threshold': float,
        'eps': float,
        'k': float,
        'angle': float,
        'resize': bool,
        'window size': int,
        'kernel size': int,
        'adaptive kernel size': int,
        'luminance preserving': bool,
        'preserve alpha': bool,
        'maximum': float,
        'minimum': float,
        'inverse': bool,
        'cutoff': float,
        'gain': float,
        'bins': int,
        'diagonal neighborhood': bool,
        'border mode': ['constant', 'reflect', 'wrap', 'nearest', 'mirror'],
        'harris method': ['k', 'eps'],
        'horizontal/vertical': ['horizontal', 'vertical', 'both'],
        'positive/negative diagonal': ['default', 'positive', 'negative'],
        'threshold method': ['gaussian', 'mean', 'median'],
        'histogram selection': ['min', 'mid', 'max'],
        'add alpha': bool,
        'padding': bool,
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
        'auto threshold method': [
            'otsu', 'yen', 'isodata', 'li', 'minimum', 'mean', 'triangle',
            'median'],
    }
    options_default = {
        'n': 12, 'width': 512, 'height': 512, 'x': 0, 'y': 0,
        'sigma': 1.0, 'sigma-x': 1.0, 'sigma-y': 1.0, 'threshold': 0.15,
        'eps': 1e-6, 'k': 0.05, 'window size': 1, 'scale': 1.0, 'offset': 0.0,
        'gamma': 1.0, 'kernel size': 3, 'adaptive kernel size': 4,
        'luminance preserving': True, 'preserve alpha': True, 'maximum': 1.0,
        'minimum': 0.0, 'inverse': False, 'cutoff': 0.5, 'gain': 10.0,
        'bins': 256, 'diagonal neighborhood': False, 'scale x': 1.0,
        'scale y': 1.0, 'interpolation degree': 3, 'angle': 0.0,
        'resize': True, 'add alpha': False, 'aspect': False, 'padding': False,
        'cmap': 'viridis',
        'auto threshold method': 'otsu',
    }

    parameters = node.parameters()
    parameters.set_string('algorithm', value=next(iter(algorithms)),
                          description='', label='Algorithm')
    ImageFiltering_abstract.generate_parameters(parameters, options_types,
                                                options_default)

    inputs = Ports([
        Image('source image to filter', name='source'),
        Port.Custom('table', 'Filter operands', name='operand', n=(0, 1)),
    ])
    outputs = Ports([
        Image('result after filtering', name='result'),
    ])
    __doc__ = ImageFiltering_abstract.generate_docstring(
        description, algorithms, options_list, inputs, outputs)

    def execute(self, node_context):
        source_obj = node_context.input['source']
        source = source_obj.get_image()
        params = node_context.parameters
        alg_name = params['algorithm'].value
        operands = node_context.input.group('operand')

        if len(source.shape) == 3 and source.shape[2] > 1:
            multichannel_image = True
        else:
            multichannel_image = False

        alg = self.algorithms[alg_name]['algorithm']
        if (multichannel_image and
            not self.algorithms[alg_name]['multi_chromatic']):
            # Process each channel separately
            if 'operands' in self.algorithms[alg_name]:
                im1       = alg(source[:, :, 0], params, operands)
            else:
                im1       = alg(source[:, :, 0], params)
            im        = np.zeros(im1.shape[:2]+(source.shape[2],))
            im[:, :, 0] = im1
            for channel in range(1, source.shape[2]):
                if 'operands' in self.algorithms[alg_name]:
                    im[:, :, channel] = (
                        alg(source[:, :, channel], params, operands))
                else:
                    if len(operands) != 0:
                        sywarn('Selected algorithm {} does not use the '
                               'additional operand passed to it'
                               .format(alg_name))
                    im[:, :, channel] = alg(source[:, :, channel], params)

        else:
            # Process all channels at once
            if len(source.shape) == 3 and source.shape[2] == 1:
                source = source.reshape(source.shape[:2])
            if 'operands' in self.algorithms[alg_name]:
                im = alg(source, params, operands)
            else:
                if len(operands) != 0:
                    sywarn('Selected algorithm {} does not use the additional '
                           'operand passed to it'.format(alg_name))
                im = alg(source, params)

        node_context.output['result'].set_image(im)


class ImageFiltering2(ImageFiltering_abstract, node.Node):
    name = 'Filter Image, Dual Output'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'image_filtering_dual.svg'
    description = 'Filters one image using algorithms with two images as output'
    nodeid = 'syip.imagefiltering2'
    tags = Tags(Tag.ImageProcessing.ImageManipulation)

    def alg_hessian_eigenval(im, par):
        hrr, hrc, hcc = feature.hessian_matrix(im, sigma=par['sigma'].value)
        return feature.hessian_matrix_eigvals(hrr, hrc, hcc)

    algorithms = {
        'corner_foerstner': {
            'description': (
                'Computes Foerstner corner measure response images. Outputs '
                'error eclipse sizes (top) and roundness or error eclipse '
                '(bottom).'),
            'sigma': 'Standard deviation of gaussian kernel (default 1.0)',
            'multi_chromatic': False,
            'algorithm': lambda im, par: feature.corner_foerstner(
                im, sigma=par['sigma'].value)
        },
        'hessian eigenvalues': {
            'description': (
                'Computes the eigenvalues of the hessian matrix for each '
                'pixel. Returns larger eigenvalue in first output image and '
                'smaller in second'),
            'multi_chromatic': False,
            'sigma': (
                'Standard deviation of gaussian kernel (default 3.0) used for '
                'calculating Hessian.\nApproximation is not reliable for '
                'sigma < 3.0'),
            'algorithm': alg_hessian_eigenval
        },
    }

    options_list    = ['n', 'sigma', 'threshold']
    options_types   = {'n': int, 'sigma': float, 'threshold': float}
    options_default = {'n': 12, 'sigma': 1.0, 'threshold': 0.15}

    parameters = node.parameters()
    parameters.set_string(
        'algorithm', value=next(iter(algorithms)), description='', label='Algorithm')
    ImageFiltering_abstract.generate_parameters(
        parameters, options_types, options_default)

    inputs = Ports(
        [Image('source image to filter', name='source'), ]
    )
    outputs = Ports([
        Image('result after filtering', name='resultA'),
        Image('result after filtering', name='resultB'),
    ])
    __doc__ = ImageFiltering_abstract.generate_docstring(
        description, algorithms, options_list, inputs, outputs)

    def execute(self, node_context):
        source_obj = node_context.input['source']
        source = source_obj.get_image()
        params = node_context.parameters
        alg_name = params['algorithm'].value

        if len(source.shape) == 3 and source.shape[2] > 1:
            multichannel_image = True
        else:
            multichannel_image = False

        alg = self.algorithms[alg_name]['algorithm']
        if (multichannel_image and
            not self.algorithms[alg_name]['multi_chromatic']):
            # Process each channel separately
            imA1, imB1 = alg(source[:, :, 0], params)
            imA = np.zeros(imA1.shape[:2]+(source.shape[2],))
            imB = np.zeros(imB1.shape[:2]+(source.shape[2],))
            imA[:, :, 0] = imA1
            imB[:, :, 0] = imA1
            for channel in range(1, source.shape[2]):
                result = alg(source[:, :, channel], params)
                imA[:, :, channel], imB[:, :, channel] = result
        else:
            # Process all channels at once
            if len(source.shape) == 3 and source.shape[2] == 1:
                source = source.reshape(source.shape[:2])
            imA, imB = alg(source, params)

        node_context.output['resultA'].set_image(imA)
        node_context.output['resultB'].set_image(imB)
