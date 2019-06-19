# -*- coding:utf-8 -*-
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
import itertools
import collections
import six

import numpy as np
from six.moves import range as range_

from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust
from sympathy.api.exceptions import SyConfigurationError


class IHeatMapAccumulator(object):
    def __init__(self):
        self._value = None

    def add_data(self, data):
        raise NotImplementedError

    def value(self):
        return self._value


class CountAccumulator(IHeatMapAccumulator):
    def add_data(self, data):
        if not self._value:
            self._value = 0
        self._value += data.size


class SumAccumulator(IHeatMapAccumulator):
    def add_data(self, data):
        if not self._value:
            self._value = 0
        self._value += data.sum()


class MinAccumulator(IHeatMapAccumulator):
    def add_data(self, data):
        if not data.size:
            return
        if self._value is None:
            self._value = data.min()
        else:
            self._value = min(self._value, data.min())


class MaxAccumulator(IHeatMapAccumulator):
    def add_data(self, data):
        if not data.size:
            return
        if self._value is None:
            self._value = data.max()
        else:
            self._value = max(self._value, data.max())


class MeanAccumulator(IHeatMapAccumulator):
    def __init__(self):
        self._sum = 0
        self._count = 0

    def add_data(self, data):
        self._sum += data.sum()
        self._count += data.size

    def value(self):
        if self._count:
            return self._sum / self._count
        else:
            return None


class MedianAccumulator(IHeatMapAccumulator):
    def __init__(self):
        self._values = []

    def add_data(self, data):
        self._values.append(data)

    def value(self):
        if self._values:
            return np.ma.median(np.vstack(self._values))
        else:
            return None


REDUCTION_FUNCTIONS = collections.OrderedDict([
    ('Count (histogram)', CountAccumulator),
    ('Sum', SumAccumulator),
    ('Min', MinAccumulator),
    ('Max', MaxAccumulator),
    ('Mean', MeanAccumulator),
    ('Median', MedianAccumulator)])


class HeatmapCalculation(synode.Node):
    """
    This node calculates a 2D histogram or other heatmap of a given signal.

    The output consists of bin edges and bin values and can for instance be
    used in a heatmap plot in the node :ref:`Figure`.

    This node ignores any rows in the input where one or more of the selected
    columns are masked.
    """

    author = 'Magnus Sandén <magnus.sanden@combine.se'
    copyright = "(C) 2016 Combine Control Systems AB"
    version = '0.1'
    icon = 'heatmap_calculation.svg'
    name = 'Heatmap calculation'
    description = ('Calculate a 2d histogram or other heatmap of a given'
                   'signal.')
    nodeid = 'org.sysess.sympathy.dataanalysis.heatmapcalc'
    tags = Tags(Tag.Analysis.Statistic)

    parameters = synode.parameters()
    combo_editor = synode.Util.combo_editor(edit=True)
    reduction_editor = synode.Util.combo_editor(
        options=list(REDUCTION_FUNCTIONS.keys()))
    parameters.set_string('x_data_column', label="X data column:",
                          editor=combo_editor,
                          description='Select X axis data')
    parameters.set_string('y_data_column', label="Y data column:",
                          editor=combo_editor,
                          description='Select Y axis data')
    parameters.set_string('z_data_column', label="Z data column:",
                          description='The data points of the z data are '
                                      'placed in bins according to the '
                                      'cooresponding values of x and y. They '
                                      'are then reduced to a single bin value '
                                      'using the selected reduction function. '
                                      'For "{}" no z data column is needed.'
                                      ''.format(
                                          list(REDUCTION_FUNCTIONS.keys())[0]),
                          editor=combo_editor)
    parameters.set_string('reduction', label="Reduction function:",
                          value=list(REDUCTION_FUNCTIONS.keys())[0],
                          description='A function used on all the z data '
                                      'points in a bin. For "{}" no z data '
                                      'column is needed.'.format(
                                          list(REDUCTION_FUNCTIONS.keys())[0]),
                          editor=reduction_editor)
    parameters.set_integer('x_bins', label="X Bins:", value=10,
                           description='Number of bins on the x axis')
    parameters.set_integer('y_bins', label="Y Bins:", value=10,
                           description='Number of bins on the y axis')
    parameters.set_boolean('auto_range', label="Auto range", value=True,
                           description=('When checked, use data range as '
                                        'histogram range'))
    parameters.set_float(
        'x_min', label="X min:", value=0.0, description='Set minimum X value')
    parameters.set_float(
        'x_max', label="X max:", value=1.0, description='Set maximum X value')
    parameters.set_float(
        'y_min', label="Y min:", value=0.0, description='Set minimum Y value')
    parameters.set_float(
        'y_max', label="Y max:", value=1.0, description='Set maximum Y value')

    controllers = (synode.controller(
        when=synode.field('auto_range', 'checked'),
        action=(synode.field('x_min', 'disabled'),
                synode.field('x_max', 'disabled'),
                synode.field('y_min', 'disabled'),
                synode.field('y_max', 'disabled'))),
        synode.controller(
            when=synode.field(
                'reduction', 'value', list(REDUCTION_FUNCTIONS.keys())[0]),
            action=synode.field('z_data_column', 'disabled')))

    inputs = Ports([Port.Table('Input data', name='in')])
    outputs = Ports([Port.Table('Heatmap data', name='out')])

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['x_data_column'],
               node_context.input['in'])
        adjust(node_context.parameters['y_data_column'],
               node_context.input['in'])
        adjust(node_context.parameters['z_data_column'],
               node_context.input['in'])

    def execute(self, node_context):
        parameters = node_context.parameters
        x_bins = parameters['x_bins'].value
        y_bins = parameters['y_bins'].value
        x_data_column = parameters['x_data_column'].value
        y_data_column = parameters['y_data_column'].value
        z_data_column = parameters['z_data_column'].value
        auto_range = parameters['auto_range'].value

        if x_data_column is None or y_data_column is None or (
                z_data_column is None and
                list(REDUCTION_FUNCTIONS.keys())[0] !=
                parameters['reduction'].value):
            raise SyConfigurationError('Please choose a data column.')

        x_data = node_context.input['in'].get_column_to_array(x_data_column)
        y_data = node_context.input['in'].get_column_to_array(y_data_column)
        if (list(REDUCTION_FUNCTIONS.keys())[0] ==
                parameters['reduction'].value):
            z_data = np.zeros_like(x_data)
        else:
            z_data = node_context.input['in'].get_column_to_array(
                z_data_column)

        # Handle masked arrays
        mask = np.zeros(x_data.shape, dtype=bool)
        if isinstance(x_data, np.ma.MaskedArray):
            mask |= x_data.mask
        if isinstance(y_data, np.ma.MaskedArray):
            mask |= y_data.mask
        if isinstance(z_data, np.ma.MaskedArray):
            mask |= z_data.mask
        if np.any(mask):
            mask = np.logical_not(mask)
            x_data = x_data[mask]
            y_data = y_data[mask]
            z_data = z_data[mask]

        if auto_range:
            x_min = min(x_data)
            x_max = max(x_data)
            y_min = min(y_data)
            y_max = max(y_data)
        else:
            x_min = parameters['x_min'].value
            x_max = parameters['x_max'].value
            y_min = parameters['y_min'].value
            y_max = parameters['y_max'].value

        x_bin_edges = np.linspace(x_min, x_max, x_bins + 1)
        y_bin_edges = np.linspace(y_min, y_max, y_bins + 1)
        Accumulator = REDUCTION_FUNCTIONS[parameters['reduction'].value]  # noqa
        values_buffer = np.empty((x_bins, y_bins), dtype=object)

        x_bin_indices = np.digitize(x_data, x_bin_edges)
        y_bin_indices = np.digitize(y_data, y_bin_edges)

        # Digitize puts values on bin edges in the right bin, but for the
        # rightmost bin this is not what we want. We want the rightmost bin to
        # be a closed interval.
        on_x_edge = x_data == x_bin_edges[-1]
        on_y_edge = y_data == y_bin_edges[-1]
        x_bin_indices[on_x_edge] -= 1
        y_bin_indices[on_y_edge] -= 1

        # Build the values buffer. The values buffer holds a list of z
        # values for each bin.
        for x_bin_index, y_bin_index, z in six.moves.zip(
                x_bin_indices, y_bin_indices, z_data):
            if 0 < x_bin_index <= x_bins and 0 < y_bin_index <= y_bins:
                xi = x_bin_index - 1
                yi = y_bin_index - 1
            else:
                # print("bin doesn't exist: ({}, {})".format(
                #     x_bin_index, y_bin_index))
                continue
            if values_buffer[xi, yi] is None:
                values_buffer[xi, yi] = Accumulator()
            values_buffer[xi, yi].add_data(z)

        # Now go through the values buffer and reduce each list into the real z
        # data for that bin.
        bin_values = np.ma.masked_all((x_bins, y_bins), dtype=float)
        for xi, yi in itertools.product(range_(x_bins), range_(y_bins)):
            z_values = values_buffer[xi, yi]
            if z_values is not None:
                bin_values[xi, yi] = z_values.value()

        x_output = np.array([x_bin_edges[:-1]] * y_bins).reshape(-1, order='F')
        y_output = np.array([y_bin_edges[:-1]] * x_bins).reshape(-1, order='C')
        node_context.output['out'].set_column_from_array(
            "X bin edges", x_output)
        node_context.output['out'].set_column_from_array(
            "Y bin edges", y_output)
        node_context.output['out'].set_column_from_array(
            "Bin values", bin_values.flatten())
