# Copyright (c) 2018, Combine Control Systems AB
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

import numpy as np
import matplotlib as mpl
import matplotlib.cm as cm

from sympathy.api import node as synode
from sympathy.platform.exceptions import SyError
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sylib.figure import colors


class ColormapLookup(synode.Node):

    version = '0.1'
    name = 'Colormap lookup'
    icon = 'colourmap.svg'
    description = 'Maps input values into colours based on a colourmap.'
    nodeid = 'org.sysess.sympathy.visualize.colormap_lookup'
    tags = Tags(Tag.Visual.Figure)

    inputs = Ports([Port.Table('Input data', name='input')])
    outputs = Ports([Port.Table('Output data', name='output')])

    parameters = synode.parameters()
    parameters.set_string(
        'colormap', value='viridis', label='Colormap',
        description=(
            'Colormap used for converting the input values'),
        editor=synode.Util.combo_editor(options=list(colors.COLORMAPS.keys())))
    parameters.set_float(
        'vmin', value=0.0, label='vmin',
        description=(
            'First (lowest) value that should be mapped to colors'))
    parameters.set_float(
        'vmax', value=1.0, label='vmax',
        description=(
            'Last (highest) value that should be mapped to colors'))
    parameters.set_string(
        'suffix', value='', label='Suffix',
        description=('Suffix added to each column name when '
                     'generating the output names'))

    def execute(self, node_context):
        in_tbl = node_context.input['input']
        out_tbl = node_context.output['output']
        suffix = node_context.parameters['suffix'].value
        vmin = node_context.parameters['vmin'].value
        vmax = node_context.parameters['vmax'].value
        colormap_name = node_context.parameters['colormap'].value
        colormap = cm.get_cmap(colors.COLORMAPS[colormap_name])

        norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)

        for col in in_tbl.cols():
            try:
                data = (colormap(norm(col.data)) * 255)[:, :3].astype(int)
            except TypeError:
                raise SyError("Colormap node requires all input "
                              "columns to be numerical.")
            as_strings = ['#{:0>2X}{:0>2X}{:0>2X}'
                          .format(*list(c))
                          for c in data]
            out_tbl.set_column_from_array(col.name+suffix,
                                          np.array(as_strings))
