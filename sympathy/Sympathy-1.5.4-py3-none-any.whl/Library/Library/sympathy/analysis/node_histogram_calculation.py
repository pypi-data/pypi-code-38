# -*- coding: utf-8 -*-
# Copyright (c) 2016, Combine Control Systems AB
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

from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust
from sympathy.api.exceptions import SyConfigurationError


class HistogramCalculation(synode.Node):
    """
    This node takes a table and calculates a histogram from one of its columns.

    The output consists of bin edges and bin values and can for instance be
    used in a histogram plot in the node :ref:`Figure`.

    Masked values in the data column are ignored. Masked values in the weights
    column are treated as 1.
    """
    author = 'Magnus Sandén <magnus.sanden@combine.se'
    copyright = "(C) 2016 Combine Control Systems AB"
    version = '0.1'
    icon = 'histogram_calculation.svg'
    name = 'Histogram calculation'
    description = 'Calculate the histogram of a given signal.'
    nodeid = 'org.sysess.sympathy.dataanalysis.histogramcalc'
    tags = Tags(Tag.Analysis.Statistic)

    parameters = synode.parameters()
    combo_editor = synode.editors.combo_editor(edit=True)
    combo_editor_w_empty = synode.editors.combo_editor(
        include_empty=True, edit=True)
    parameters.set_list('data_column', label="Data column:",
                        description='Column to create histogram for.',
                        editor=combo_editor)
    parameters.set_list('weights_column', label="Weights column:",
                        description=('If you choose a weights column, '
                                     'each value in the data column only '
                                     'contributes its associated weight '
                                     'towards the bin count, instead of 1.'),
                        editor=combo_editor_w_empty)
    parameters.set_integer('bins', label="Bins:", value=10,
                           description='Number of bins.')
    parameters.set_boolean('auto_range', label="Auto range", value=True,
                           description=('When checked, use data range as '
                                        'histogram range.'))
    parameters.set_float('x_min', label="X min:", value=0.0,
                         description='Minimum x value.')
    parameters.set_float('x_max', label="X max:", value=1.0,
                         description='Maximum x value.')
    parameters.set_boolean('normed', label="Density",
                           description=('When checked, the result is the '
                                        'value of the probability density '
                                        'function at each bin, normalized '
                                        'such that the integral of the '
                                        'histogram is 1.'))

    controllers = synode.controller(
        when=synode.field('auto_range', 'checked'),
        action=(synode.field('x_min', 'disabled'),
                synode.field('x_max', 'disabled')))

    inputs = Ports([Port.Table('Input data', name='in')])
    outputs = Ports([Port.Table('Histogram data', name='out')])

    def update_parameters(self, parameters):
        parameters['weights_column'].editor['include_empty'] = True

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['data_column'],
               node_context.input['in'])
        adjust(node_context.parameters['weights_column'],
               node_context.input['in'])

    def execute(self, node_context):
        parameters = node_context.parameters
        bins = parameters['bins'].value
        density = parameters['normed'].value
        data_column = parameters['data_column'].selected
        auto_range = parameters['auto_range'].value
        if not data_column:
            raise SyConfigurationError('Please choose a data column.')
        if auto_range:
            range_ = None
        else:
            x_min = parameters['x_min'].value
            x_max = parameters['x_max'].value
            range_ = x_min, x_max

        data = node_context.input['in'].get_column_to_array(data_column)
        weights_column = parameters['weights_column'].selected
        if not weights_column:
            weights = None
        else:
            weights = node_context.input['in'].get_column_to_array(
                weights_column)

        # Handle masked arrays
        if isinstance(weights, np.ma.MaskedArray):
            weights.fill(1)
        if isinstance(data, np.ma.MaskedArray):
            mask = data.mask
            data = data.compressed()
            if weights is not None:
                weights = weights[np.logical_not(mask)]

        bin_values, bin_edges = np.histogram(
            data, bins=bins, density=density, weights=weights, range=range_)

        node_context.output['out'].set_column_from_array(
            "Bin values", bin_values)
        node_context.output['out'].set_column_from_array(
            "Bin min edges", bin_edges[:-1])
        node_context.output['out'].set_column_from_array(
            "Bin max edges", bin_edges[1:])
