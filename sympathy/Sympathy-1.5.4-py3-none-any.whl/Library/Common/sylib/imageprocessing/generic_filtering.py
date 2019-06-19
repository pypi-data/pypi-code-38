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

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
from sympathy.api.nodeconfig import Tag, Tags
import numpy as np

class GenericImageFiltering(object):
    """
    Generic class for implementing all image processing nodes that takes
    a simple image and paramter list as inputs and outputs an image
    """

    version   = '0.1'
    author    = 'Mathias Broxvall'
    copyright = "(C) 2017 Combine Control Systems AB"
    tags      = Tags(Tag.ImageProcessing.ImageManipulation)

    def execute(self, node_context):
        params = node_context.parameters
        source = node_context.input['source'].get_image()

        if len(source.shape) == 3 and source.shape[2] > 1:
            is_multichannel = True
        else:
            is_multichannel = False

        alg_dict = self.algorithms[params['algorithm'].value]
        alg = alg_dict['algorithm']
        multi_chromatic = alg_dict['multi_chromatic']
        if (is_multichannel and not multi_chromatic):
            # Process each channel one by one
            # Process first channel separately to get the Width/Height of it
            res0       = alg(source[:, :, 0], params)
            res        = np.zeros(res0.shape[:2]+source.shape[2:])
            res[:, :, 0] = res0
            for channel in range(1, source.shape[2]):
                res[:, :, channel] = alg(source[:, :, channel], params)
            node_context.output['result'].set_image(res)
        else:
            # Process all channels at once
            if len(source.shape) == 3 and source.shape[2] == 1:
                source = source.reshape(source.shape[:2])
            node_context.output['result'].set_image(alg(source, params))



