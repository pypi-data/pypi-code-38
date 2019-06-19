# -*- coding: utf-8 -*-
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
Find peaks in a signal and slice the input Table into a list of Tables, where
each element contains one peak.

If peaks are found very close to the edges of the data, the first and/or
last element may contain unexpected results. If this is the case,
use :ref:`Slice List` to remove these elements.
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
from sympathy.api import node
from sympathy.api import table
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust
from sympathy.api.exceptions import sywarn, SyConfigurationError
import numpy as np
import scipy.signal as signal
import math
import warnings

LOCAL_MAXIMA = 'Local Maxima'
WAVELET = 'Continuous Wavelet Transform'


def median_period(data, peak_detector, samples):
    # Lowpass filter to reduce the risk of erroneous detections.
    # Remove last element to keep the original data length.
    data = np.convolve(data, np.ones(10) / 10)[:-1]

    # Calculate the autocorrelation
    # (see https://en.wikipedia.org/wiki/Autocorrelation)
    # and extract a sequence with the same size as the original data.
    correlation = signal.correlate(data, data, mode='same') / len(data)

    # Detect local maxima using the selected algorithm.
    if peak_detector == LOCAL_MAXIMA:
        peaks = signal.argrelmax(correlation)[0]
    else:
        peaks = signal.find_peaks_cwt(correlation, np.linspace(1, samples))

    # Differentiate to calculate the distance between peaks.
    # Then remove the first and last peaks to avoid problems where these
    # samples are to close the start or end of the data.
    diff_peaks = np.diff(peaks)

    # Calculate the average of 80 % of the found peaks.
    start = int(np.ceil(len(diff_peaks) * 0.1))
    stop = int(-np.ceil(len(diff_peaks) * 0.1))
    med_diff = np.mean(diff_peaks[start:stop])
    return med_diff


class SequenceSplit(node.Node):
    name = 'Periodic Sequence Split Table'
    author = u'Måns Fällman<mans.fallman@combine.se>'
    copyright = '(c) 2017 Combine Control Systems AB'
    version = '1.0'
    icon = 'sequencesplit.svg'
    description = (
        'Splits tables of data in equidistant points based on the periodicity '
        'of an identifier column')
    nodeid = 'org.sysess.sympathy.data.table.sequencesplit'
    tags = Tags(Tag.Analysis.SignalProcessing)

    inputs = Ports([Port.Table('The sequence to split', 'sequence')])
    outputs = Ports([Port.Tables('The split sequences', 'sequences')])

    parameters = node.parameters()
    parameters.set_string(
        'peak_detector',
        label='Peak Detecting Algorithm',
        description='Choose which algorithm to detect periodic events',
        value=LOCAL_MAXIMA,
        editor=node.Util.combo_editor(options=[LOCAL_MAXIMA, WAVELET]))
    parameters.set_integer(
        'samples',
        label='Samples per peak',
        description=(
            'Choose an approximate value for the number of expected samples '
            'between peaks'),
        editor=node.Util.bounded_spinbox_editor(2, 9999999, 1))
    parameters.set_list(
        'select_column',
        label='Select column:',
        description='Choose column to use as identifier',
        editor=node.Util.combo_editor(edit=True))
    parameters.set_float(
        'lag_offset',
        label='Offset of peridodic event(0-100)',
        description='Add lag as a percentage of the discarded data',
        value=0.0,
        editor=node.Util.bounded_lineedit_editor(
            0, 100, placeholder='0-100'))

    controllers = (
        node.controller(
            when=node.field('peak_detector', 'value', value=WAVELET),
            action=(node.field('samples', 'enabled'))),
        node.controller(
            when=node.field('peak_detector', 'value', value=LOCAL_MAXIMA),
            action=(node.field('samples', 'disabled'))))

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['select_column'],
               node_context.input['sequence'])

    def execute(self, node_context):
        parameters = node_context.parameters
        in_table = node_context.input['sequence']
        column = parameters['select_column'].selected
        if column is None:
            raise SyConfigurationError('No column selected.')

        data = in_table.get_column_to_array(column)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            med_diff = median_period(
                data,
                parameters['peak_detector'].value,
                parameters['samples'].value)
        if math.isnan(med_diff):
            sywarn('No peaks found. Check input data.')
            return

        offset = np.mod(len(data), np.round(med_diff))
        offset = int(offset * parameters['lag_offset'].value * 0.01)

        number_of_tables = np.int(len(data) / med_diff)
        for x in range(number_of_tables):
            out_table = table.File()
            names = in_table.column_names()
            start = int(np.round(x * med_diff) + offset + np.mod(x, 2))
            stop = int(np.round((x + 1) * med_diff) + offset + np.mod(x, 2))
            for name in names:
                out_table.set_column_from_array(
                    name, in_table.get_column_to_array(name)[start:stop])
            node_context.output['sequences'].append(out_table)
