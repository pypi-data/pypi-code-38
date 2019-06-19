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

from sylib.machinelearning.ensemble import EnsembleDescriptor

class PipelineDescriptor(EnsembleDescriptor):

    def __init__(self, **kwargs):
        super(PipelineDescriptor, self).__init__(**kwargs)
        self.set_steps([], [])

    def set_steps(self, names, descs):
        self._descs = descs
        self._names = names

    def set_x_names(self, x_names):
        for name, d, s in self.get_models():
            d.set_x_names(x_names)
            if d.y_names is None:
                break
            x_names = d.y_names

    def set_y_names(self, y_names):
        for name, d, s in list(self.get_models())[::-1]:
            d.set_y_names(y_names)
            if d.x_names is None:
                break
            y_names = d.x_names

    @property
    def y_names(self):
        if not self.has_models():
            return None

        _, desc, _ = list(self.get_models())[-1]
        return desc.y_names

    @property
    def x_names(self):
        if not self.has_models():
            return None

        _, desc, _ = list(self.get_models())[0]
        return desc.x_names

    def post_fit(self, skl):
        for name, d, s in self.get_models():
            d.skl = s
            d.post_fit(s)
        # Post fit operations may have updated x/y names - so propagate again
        self.set_x_names(list(self.get_models())[0][1].x_names)
        self.set_y_names(list(self.get_models())[-1][1].y_names)

    def has_models(self):
        return len(list(self.get_models())) > 0

    def get_models(self):
        return zip(self._names, self._descs, [skl for _, skl in self.skl.steps])
