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
from sympathy.utils import port

from skimage import io, data
from sylib.imageprocessing.image import Image
import sylib.imageprocessing
import numpy as np
import os.path

class LoadImage(node.Node):
    """
    Loads an image from a file given by a datasource.
    """
    name = 'Load Image'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'image_load.svg'
    description = 'Loads an image from a datasource'
    nodeid = 'syip.loadimage'
    tags = Tags(Tag.ImageProcessing.IO)

    parameters = node.parameters()
    parameters.set_boolean(
        'as_greyscale', label='As greyscale',
        description='Transforms image to greyscale if not already such',
        value=False)

    inputs = Ports(
        [Port.Datasource('Source of image data. Must be a file on disk',
                         name='source')])
    outputs = Ports(
        [Image('Output image', name='image')])

    def execute(self, node_context):

        source = node_context.input['source']
        if source.decode_type() != 'FILE':
            raise NotImplementedError(
                'Image loading from databases not implemented.')
        source_path = source.decode_path()
        as_greyscale = node_context.parameters['as_greyscale'].value
        image = io.imread(source_path, as_gray=as_greyscale)
        if image.dtype == 'uint8':
            image = image / 256.0
        node_context.output['image'].set_image(image)

class LoadImageList(node.Node):
    """
    Loads a list of images from a file given a list of datasources.
    """
    name = 'Load Image List'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'image_load.svg'
    description = 'Loads an image from a datasource'
    nodeid = 'syip.loadimage_list'
    tags = Tags(Tag.ImageProcessing.IO)

    parameters = node.parameters()
    parameters.set_boolean(
        'as_greyscale', label='As greyscale',
        description='Transforms image to greyscale if not already such',
        value=False)

    inputs = Ports(
        [port.CustomPort('[datasource]', 'Source of image data. Must be a file on disk',
                         name='source')])
    outputs = Ports(
        [port.CustomPort('[image]','Output image', name='image')])

    def execute(self, node_context):

        for idx, source in enumerate(node_context.input['source']):
            self.set_progress((100*idx) / len(node_context.input['source']))
            if source.decode_type() != 'FILE':
                raise NotImplementedError(
                    'Image loading from databases not implemented.')
            source_path = source.decode_path()
            as_greyscale = node_context.parameters['as_greyscale'].value
            image = io.imread(source_path, as_gray=as_greyscale)
            if image.dtype == 'uint8':
                image = image / 256.0

            image_obj = sylib.imageprocessing.image.File()
            image_obj.set_image(image)
            node_context.output['image'].append(image_obj)

class ExampleImage(node.Node):
    """
    Loads an image from the built-in default example images in scikit-image
    """
    name = 'Example Image'
    author = 'Mathias Broxvall'
    copyright = '(C) 2017 Combine Control Systems AB'
    version = '0.1'
    icon = 'image_examples.svg'
    description = (
        'Loads an image from the built-in default example images in '
        'scikit-image')
    nodeid = 'syip.exampleimage'
    tags = Tags(Tag.ImageProcessing.IO)

    parameters = node.parameters()
    parameters.set_string(
        'source', value='coins', label='Image',
        description='Selected predefined image',
        editor=node.Util.combo_editor(
            sorted([
                'astronaut', 'camera', 'candy', 'checkerboard', 'chelsea (cat)', 'clock',
                'coffee', 'coins', 'horse', 'hubble deep field', 'page',
                'motorcycle_left', 'motorcycle_right',
                'immunohistochemistry', 'moon', 'rocket', 'text']))
    )

    outputs = Ports([Image('Output image', name='output')])

    def execute(self, node_context):
        source_name = node_context.parameters['source'].value
        if source_name == 'astronaut':
            im = data.astronaut()
        elif source_name == 'camera':
            im = data.camera()
        elif source_name == 'checkerboard':
            im = data.checkerboard()
        elif source_name == 'chelsea (cat)':
            im = data.chelsea()
        elif source_name == 'clock':
            im = data.clock()
        elif source_name == 'coffee':
            im = data.coffee()
        elif source_name == 'coins':
            im = data.coins()
        elif source_name == 'horse':
            im = data.horse()
        elif source_name == 'hubble deep field':
            im = data.hubble_deep_field()
        elif source_name == 'immunohistochemistry':
            im = data.immunohistochemistry()
        elif source_name == 'moon':
            im = data.moon()
        elif source_name == 'rocket':
            im = data.rocket()
        elif source_name == 'text':
            im = data.text()
        elif source_name == 'page':
            im = data.page()
        elif source_name == 'motorcycle_left':
            im = data.stereo_motorcycle()[0]
        elif source_name == 'motorcycle_right':
            im = data.stereo_motorcycle()[1]
        elif source_name == 'candy':
            path = os.path.join(
                os.path.dirname(sylib.imageprocessing.__file__),
                "candy.png")
            im = io.imread(path, as_gray=False)
        else:
            im = np.zeros((512, 512, 3))

        if im.dtype == 'uint8':
            im = im/256.0

        node_context.output['output'].set_image(im)
