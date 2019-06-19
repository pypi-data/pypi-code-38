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
from sympathy.api import node
from sympathy.api.nodeconfig import Ports

from skimage import morphology
from sylib.imageprocessing.image import Image
from sylib.imageprocessing.algorithm_selector import ImageFiltering_abstract
from sylib.imageprocessing.generic_filtering import GenericImageFiltering


API_URL = 'http://scikit-image.org/docs/0.13.x/api/'
CONVEX_HULL_DESC = (
    'The convex hull is the set of pixels included in the smallest convex'
    'polygon that surround all white pixels in the input image.'
)


def _remove_small_holes(im, area_threshold, connectivity):
    """
    Handling for renamed parameter in remove_small_holes.
    """
    try:
        return morphology.remove_small_holes(
            im, area_threshold=area_threshold, connectivity=connectivity)
    except TypeError:
        # scikit-image <= 0.13.
        return morphology.remove_small_holes(
            im, min_size=area_threshold, connectivity=connectivity)


MORPHOLOGY_ALGS = {
    'labeling': {
        'description': (
            'Creates a unique integer label for each connected component '
            'in an integer valued or binary image.'),
        'diagonal neighborhood': (
            'If true then also consider diagonals for connectivity'),
        'multi_chromatic': False,
        'url': API_URL+'skimage.morphology.html#skimage.morphology.label',
        'algorithm': lambda im, par: morphology.label(
            im,
            connectivity=2 if par['diagonal neighborhood'].value else 1)
    },
    'remove small holes': {
        'description': (
            'Removes small holes from an integer or boolean image.'),
        'diagonal neighborhood': (
            'If true then also consider diagonals for connectivity'),
        'n': 'Maximum size in pixels of areas to remove (default 64)',
        'multi_chromatic': False,
        'url': (
            API_URL+'skimage.morphology.html'
            '#skimage.morphology.remove_small_holes'),
        'algorithm': lambda im, par: _remove_small_holes(
            im, area_threshold=par['n'].value,
            connectivity=2 if par['diagonal neighborhood'].value else 1)
    },
    'remove small objects': {
        'description': (
            'Removes connected components smaller than the given size.'),
        'diagonal neighborhood': (
            'If true then also consider diagonals for connectivity'),
        'n': 'Maximum size in pixels of areas to remove (default 64)',
        'multi_chromatic': False,
        'url': (
            API_URL+'skimage.morphology.html'
            '#skimage.morphology.remove_small_objects'),
        'algorithm': lambda im, par: morphology.remove_small_objects(
            im, min_size=par['n'].value,
            connectivity=2 if par['diagonal neighborhood'].value else 1)
    },
    'skeletonize': {
        'description': (
            'Returns the skeleton of a binary image. '
            'Thinning is used to reduce each connected component in a '
            'binary image to a single-pixel wide skeleton.'),
        'multi_chromatic': False,
        'url': (
            API_URL+'skimage.morphology.html#skimage.morphology.skeletonize'),
        'algorithm': lambda im, par: morphology.skeletonize(im)
    },
    'convex hull, image': {
        'description': (
            'Computes the convex hull of a binary image.\n' +
            CONVEX_HULL_DESC),
        'multi_chromatic': False,
        'url': (
            API_URL+'skimage.morphology.html'
            '#skimage.morphology.convex_hull_image'),
        'algorithm': lambda im, par: morphology.convex_hull_image(im)
    },
    'convex hull, objects': {
        'description': (
            'Computes the convex hull of each object in a binary image.\n' +
            CONVEX_HULL_DESC +
            '\nThis function uses labeling to define unique objects, finds'
            'the convex hull of each using convex_hull_image,\nand '
            'combines these regions with logical OR. Be aware the convex'
            'hulls of unconnected objects may overlap in the result'),
        'multi_chromatic': False,
        'url': (
            API_URL + 'skimage.morphology.html'
            '#skimage.morphology.convex_hull_object'),
        'algorithm': lambda im, par: morphology.convex_hull_object(im)
    },
}
MORPHOLOGY_PARAMETERS = ['diagonal neighborhood', 'n']
MORPHOLOGY_TYPES = {
    'n': int,
    'diagonal neighborhood': bool,
}
MORPHOLOGY_DEFAULTS = {
    'n': 12,
    'diagonal neighborhood': False,
}

class MorphologySingleInput(ImageFiltering_abstract, GenericImageFiltering,
                            node.Node):
    name = 'Morphology (single input)'
    icon = 'image_filtering.svg'
    description = (
        'Uses morphology based algorithms with a built-in structuring element')
    nodeid = 'syip.morphology_single_input'
    copyright = "(C) 2017 Combine Control Systems AB"

    algorithms = MORPHOLOGY_ALGS
    options_list = MORPHOLOGY_PARAMETERS
    options_types = MORPHOLOGY_TYPES
    options_default = MORPHOLOGY_DEFAULTS

    parameters = node.parameters()
    parameters.set_string('algorithm', value=next(iter(algorithms)),
                          description='', label='Algorithm')
    ImageFiltering_abstract.generate_parameters(parameters, options_types,
                                                options_default)
    inputs = Ports([Image('source image to filter', name='source')])
    outputs = Ports([Image('result after filtering', name='result')])
    __doc__ = ImageFiltering_abstract.generate_docstring(
        description, algorithms, options_list, inputs, outputs)
