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

import os
import numpy as np
from sympathy.api import typeutil
from sympathy.utils import port

# Full path to the directory where this file is located.
_directory = os.path.abspath(os.path.dirname(__file__))


@typeutil.typeutil(
    'sytypealias image = (meta_table: sytable, image_table: sytable)')
class File(typeutil.TypeAlias):
    """Represents images loaded into Sympathy."""

    def _extra_init(self, gen, data, filename, mode, scheme, source):
        pass

    @classmethod
    def viewer(cls):
        from . import image_viewer
        return image_viewer.ImageViewer

    @classmethod
    def icon(cls):
        return os.path.join(_directory, 'port_image.svg')

    def source(self, other, shallow=False):
        """
        Update self with a deepcopy of the data from other, without keeping the
        old state.

        self and other must be of the exact same type.
        """
        self._data.source(other._data, shallow=shallow)

    def set_image(self, image):
        if len(image.shape) < 3:
            image = image.reshape(image.shape+(1,))
        self._data.meta_table.set_column("shape", np.r_[image.shape])
        self._data.image_table.set_column("image", image.ravel())

    def get_image(self):
        if ('shape' in self._data.meta_table.columns() and
            'image' in self._data.image_table.columns()):
            shape = self._data.meta_table.get_column('shape')
            image = self._data.image_table.get_column('image').reshape(shape)
            return image
        else:
            return np.zeros((1, 1, 1))

    @property
    def width(self):
        if 'shape' in self._data.meta_table.columns():
            shape = self._data.meta_table.get_column('shape')
            return shape[1]
        else:
            return 1

    @property
    def height(self):
        if 'shape' in self._data.meta_table.columns():
            shape = self._data.meta_table.get_column('shape')
            return shape[0]
        else:
            return 1

    def names(self, kind=None, **kwargs):
        res = []
        if kind == 'calc':
            res = ['.get_image()']
        return res

    def types(self, kind=None, **kwargs):
        res = []
        if kind == 'calc':
            res = [self.get_image().dtype]
        return res


def Image(description, name=None, n=None):
    return port.CustomPort('image', description, name=name)

def Images(description, name=None, n=None):
    return port.CustomPort('[image]', description, name=name)
