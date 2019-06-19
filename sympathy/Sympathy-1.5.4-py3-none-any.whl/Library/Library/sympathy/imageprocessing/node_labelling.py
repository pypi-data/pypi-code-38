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
from sympathy.api.nodeconfig import Ports, Tag, Tags

from skimage import morphology
from sylib.imageprocessing.image import Image


class ImageLabelling(node.Node):
    name = 'Label image'
    icon = 'image_labelling.svg'  #
    description = (
        'Creates integer image with separate labels for each connected '
        'region with same values in input image')
    nodeid = 'syip.labelling'
    copyright = "(C) 2018 Combine Control Systems AB"
    tags = Tags(Tag.ImageProcessing.Segmentation)

    parameters = node.parameters()
    parameters.set_boolean(
        'diagonal', value=False,
        description='Allow connections along diagonal',
        label='Diagonal neighbourhood')

    inputs = Ports([
        Image('source image to label', name='source'),
    ])
    outputs = Ports([
        Image('result after labelling', name='result'),
    ])

    def execute(self, node_context):
        params = node_context.parameters
        image = node_context.input['source'].get_image()
        im = morphology.label(
            image,
            connectivity=2 if params['diagonal'].value else 1)
        node_context.output['result'].set_image(im)
