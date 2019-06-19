# Copyright (c) 2013, 2017, Combine Control Systems AB
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
To generate data fast and easy is valuable when you want to test the
functionality of nodes or during the development process of nodes. In Sympathy
random data can be generated for both Tables and ADAFs, both a single object or
as a list with several objects. The random data consists of random floats
in the half-open interval [0.0, 1.0). The Generate Signal Nodes allow the
generation of sinus, cosines or tangent signals with or without added random
noise.

The properties of the outgoing objects are specified in the configuration of
the nodes. For example for ADAFs, it is possible to specify the number of
signals in the various containers, how many attributes will be connected to
each signal or the number of elements in the signals. Similar properties can
be specified for Tables, where far less alternatives are given.
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from collections import OrderedDict


import numpy as np
from numpy.random import random as nrandom
from random import random as prandom

from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags


def adaf_base_parameters():
    parameters = synode.parameters()
    parameters.set_integer(
        'meta_entries', value=5, label='Meta columns:',
        description='The number of meta entries to be generated.',
        editor=synode.Util.bounded_spinbox_editor(0, 1000000, 1))
    parameters.set_integer(
        'meta_attributes', value=2, label='Meta attributes:',
        description='The number of meta attributes to be generated.',
        editor=synode.Util.bounded_spinbox_editor(0, 10000, 1))
    parameters.set_integer(
        'res_entries', value=5, label='Res columns:',
        description='The number of res entries to be generated.',
        editor=synode.Util.bounded_spinbox_editor(0, 1000000, 1))
    parameters.set_integer(
        'res_attributes', value=2, label='Res attributes:',
        description='The number of res attributes to be generated.',
        editor=synode.Util.bounded_spinbox_editor(0, 10000, 1))
    parameters.set_integer(
        'systems', value=1, label='Systems',
        description='The number of systems to be generated.',
        editor=synode.Util.bounded_spinbox_editor(0, 100, 1))
    parameters.set_integer(
        'rasters', value=1, label='Rasters per system',
        description='The number of rasters to be generated.',
        editor=synode.Util.bounded_spinbox_editor(0, 100, 1))
    parameters.set_integer(
        'signal_entries', value=5, label='Signals per raster',
        description='The number of signal entries to be generated.',
        editor=synode.Util.bounded_spinbox_editor(0, 1000000, 1))
    parameters.set_integer(
        'signal_attributes', value=2, label='Signal attributes',
        description='The number of signal attributes to be generated.',
        editor=synode.Util.bounded_spinbox_editor(0, 100, 1))
    parameters.set_integer(
        'signal_length', value=5, label='Signal length',
        description='The length of signals to be generated.',
        editor=synode.Util.bounded_spinbox_editor(0, 100000000, 1))
    return parameters


class RandomADAF(synode.Node):
    """
    Generates an ADAF with random numbers between 0 and 1.

    :Ref. nodes: :ref:`Random ADAFs`
    """

    author = 'Erik der Hagopian <erik.hagopian@combine.se>'
    copyright = '(C) 2013 Combine Control Systems AB'
    description = 'Random ADAF generator.'
    name = 'Random ADAF'
    nodeid = 'org.sysess.sympathy.random.randomadaf'
    icon = 'random.svg'
    version = '0.1'

    outputs = Ports([Port.ADAF(
        'ADAF with random numbers. The specifications of the ADAFs are '
        'declared in the configuration.', name='port0')])
    parameters = adaf_base_parameters()
    tags = Tags(Tag.Input.Generate)

    def execute(self, node_context):
        af = node_context.output['port0']
        self.run(af, node_context)

    def run(self, output, node_context):
        parameters = node_context.parameters
        meta = parameters['meta_entries'].value
        meta_attributes = parameters['meta_attributes'].value
        res = parameters['res_entries'].value
        res_attributes = parameters['res_attributes'].value
        systems = parameters['systems'].value
        rasters = parameters['rasters'].value
        signals = parameters['signal_entries'].value
        attributes = parameters['signal_attributes'].value
        length = parameters['signal_length'].value

        # Groups
        for group_name, entries, group_attributes in [
                ('meta', meta, meta_attributes),
                ('res', res, res_attributes)]:
            group_node = getattr(output, group_name)
            for i in range(entries):
                attribs = dict([('attr{0}'.format(attr), prandom())
                                for attr in range(attributes)])
                group_node.create_column(
                    '{0}_col{1}'.format(group_name, i),
                    np.array([prandom()]),
                    attribs)

        # Timeseries
        group = output.sys
        for i in range(systems):
            system = group.create('system{0}'.format(i))
            for j in range(rasters):
                raster = system.create('raster{0}'.format(j))
                raster.create_basis(np.arange(length))
                for k in range(signals):
                    attribs = dict([('attr{0}'.format(attr), prandom())
                                    for attr in range(attributes)])
                    raster.create_signal('signal{0}'.format(k),
                                         nrandom(length),
                                         attribs)


class RandomADAFs(synode.Node):
    """
    Generates a list of ADAF with random numbers between 0 and 1.

    :Ref. nodes: :ref:`Random ADAF`
    """

    author = 'Erik der Hagopian <erik.hagopian@combine.se>'
    copyright = '(C) 2013 Combine Control Systems AB'
    description = 'Random ADAFs generator.'
    name = 'Random ADAFs'
    icon = 'random.svg'
    nodeid = 'org.sysess.sympathy.random.randomadafs'
    outputs = Ports([Port.ADAFs(
        'ADAFs with random numbers. The specifications of the ADAFs are '
        'declared in the configuration.', name='port0')])

    version = '0.1'
    parameters = adaf_base_parameters()
    parameters.set_integer(
        'length', value=5, label='List length',
        description='The number of adafs to be generated.',
        editor=synode.Util.bounded_spinbox_editor(0, 10000, 1))
    tags = Tags(Tag.Input.Generate)

    def execute(self, node_context):
        length = node_context.parameters['length'].value
        afs = node_context.output['port0']
        single = RandomADAF()
        for i in range(length):
            self.set_progress(100. * i / length)
            af = afs.create()
            single.run(af, node_context)
            afs.append(af)
        self.set_progress(100)


def table_base_parameters():
    parameters = synode.parameters()
    parameters.set_integer(
        'column_entries', value=5, label='Columns:',
        description='The number of columns in the generated table.',
        editor=synode.Util.bounded_spinbox_editor(0, 1000000, 1))
    parameters.set_integer(
        'column_length', value=5, label='Rows:',
        description='The number of rows in the generated table.',
        editor=synode.Util.bounded_spinbox_editor(0, 100000000, 1))
    parameters.set_boolean(
        'mask_values', value=False, label='Randomly mask values',
        description='If checked each value has a 50% chance to be masked.')
    return parameters


class RandomTable(synode.Node):
    """
    Generates a Table with random numbers between 0 and 1.

    :ref. nodes: :ref:`Random Tables`
    """

    author = 'Erik der Hagopian <erik.hagopian@combine.se>'
    copyright = '(C) 2013 Combine Control Systems AB'
    description = 'Random Table generator.'
    name = 'Random Table'
    icon = 'random.svg'
    nodeid = 'org.sysess.sympathy.random.randomtable'
    version = '0.1'

    outputs = Ports([Port.Table(
        'Table with random numbers. The specifications of the Table are '
        'declared in the configuration.', name='port0')])

    parameters = table_base_parameters()
    tags = Tags(Tag.Input.Generate)

    def execute(self, node_context):
        tf = node_context.output['port0']
        self.run(tf, node_context)

    def run(self, output, node_context):
        column_entries = node_context.parameters['column_entries'].value
        column_length = node_context.parameters['column_length'].value
        mask_values = node_context.parameters['mask_values'].value

        for index in range(column_entries):
            data = nrandom(column_length)
            if mask_values:
                data = np.ma.masked_array(data,
                                          nrandom(column_length) > 0.5)
            output.set_column_from_array(str(index), data)
            self.set_progress(100.0 * (1.0 + index) / column_entries)


class RandomTables(synode.Node):
    """
    Generates a list of Tables with random numbers between 0 and 1.

    :ref. nodes: :ref:`Random Table`
    """

    author = 'Erik der Hagopian <erik.hagopian@combine.se>'
    copyright = '(C) 2013 Combine Control Systems AB'
    description = 'Random Tables generator.'
    name = 'Random Tables'
    icon = 'random.svg'
    nodeid = 'org.sysess.sympathy.random.randomtables'
    version = '0.1'

    outputs = Ports([Port.Tables(
        'Tables with random numbers. The specifications of the Tables are '
        'declared in the configuration.', name='port0')])

    parameters = table_base_parameters()
    parameters.set_integer(
        'length', value=5, label='List length',
        description='The number of tables to be generated.',
        editor=synode.Util.bounded_spinbox_editor(0, 10000, 1))
    tags = Tags(Tag.Input.Generate)

    def execute(self, node_context):
        length = node_context.parameters['length'].value
        tfs = node_context.output['port0']
        single = RandomTable()
        for idx in range(length):
            tf = tfs.create()
            single.run(tf, node_context)
            tfs.append(tf)
            self.set_progress(100.0 * (1.0 + idx) / length)


SIGNALS = OrderedDict({'sinus': np.sin,
                       'cosines': np.cos,
                       'tangent': np.tan})


def create_base_signal_parameters(parameters):
    signal_parameters = parameters.create_page('signal_params', 'Signal')
    signal_parameters.set_list(
        'signal_type', value=[0], label='Signal type',
        plist=SIGNALS.keys(),
        description='The signal to be generated.',
        editor=synode.Util.combo_editor())
    signal_parameters.set_float(
        'amplitude', value=1., label='Amplitude',
        description='The amplitude of the signal to be generated.')
    signal_parameters.set_float(
        'frequency', value=0.01, label='Frequency',
        description='The frequency of the signal to be generated.')
    signal_parameters.set_float(
        'period', value=100., label='Period',
        description='The period of the signal to be generated.')
    signal_parameters.set_boolean(
        'use_period', value=True, label='Period or Frequency',
        description=('Use Period [Checked] or Frequency [Unchecked] to ' +
                     'generate the signal.'))
    signal_parameters.set_float(
        'phase_offset', value=0., label='Phase offset',
        description='The phase offset of the signal to be generated.')
    signal_parameters.set_boolean(
        'add_noise', value=False, label='Add random noise',
        description='If random noise should be added to the signals.')
    signal_parameters.set_float(
        'noise_amplitude', value=0.01, label='Amplitude of noise',
        description='The amplitude of the noise.',
        editor=synode.Util.decimal_spinbox_editor(0.05, 2))
    signal_parameters.set_boolean(
        'index_column', value=True, label='First column as index',
        description='Add an index column to the beginning of the table.')
    return parameters


def adaf_signal_base_parameters():
    parameters = synode.parameters()
    adaf_parameters = parameters.create_page('adaf_params', 'ADAF')
    adaf_parameters.set_integer(
        'meta_entries', value=100, label='Meta entries',
        description='The number of meta entries to be generated.',
        editor=synode.Util.bounded_spinbox_editor(0, 1000000, 1))
    adaf_parameters.set_integer(
        'meta_attributes', value=5, label='Meta attributes',
        description='The number of meta attributes to be generated.',
        editor=synode.Util.bounded_spinbox_editor(0, 10000, 1))
    adaf_parameters.set_integer(
        'res_entries', value=100, label='Res entries',
        description='The number of res entries to be generated.',
        editor=synode.Util.bounded_spinbox_editor(0, 1000000, 1))
    adaf_parameters.set_integer(
        'res_attributes', value=5, label='Res attributes',
        description='The number of res attributes to be generated.',
        editor=synode.Util.bounded_spinbox_editor(0, 10000, 1))
    adaf_parameters.set_integer(
        'systems', value=1, label='Systems',
        description='The number of systems to be generated.',
        editor=synode.Util.bounded_spinbox_editor(0, 100, 1))
    adaf_parameters.set_integer(
        'rasters', value=1, label='Rasters per system',
        description='The number of rasters to be generated.',
        editor=synode.Util.bounded_spinbox_editor(0, 100, 1))
    adaf_parameters.set_integer(
        'signal_entries', value=100, label='Signals entries per raster',
        description='The number of signal entries to be generated.',
        editor=synode.Util.bounded_spinbox_editor(0, 1000000, 1))
    adaf_parameters.set_integer(
        'signal_attributes', value=5, label='Signal attributes',
        description='The number of signal attributes to be generated.',
        editor=synode.Util.bounded_spinbox_editor(0, 100, 1))
    adaf_parameters.set_integer(
        'signal_length', value=1000, label='Signal length',
        description='The length of signals to be generated.',
        editor=synode.Util.bounded_spinbox_editor(0, 100000000, 1))

    create_base_signal_parameters(parameters)
    return parameters


def table_signal_base_parameters():
    parameters = synode.parameters()
    table_parameters = parameters.create_page('table_params', 'Table')
    table_parameters.set_integer(
        'column_entries', value=100, label='Column entries',
        description='The number of column entries to be generated.',
        editor=synode.Util.bounded_spinbox_editor(0, 1000000, 1))
    table_parameters.set_integer(
        'column_length', value=1000, label='Column length',
        description='The length of columns to be generated.',
        editor=synode.Util.bounded_spinbox_editor(0, 100000000, 1))

    create_base_signal_parameters(parameters)
    return parameters


class GenerateSignalBase(synode.Node):
    author = 'Benedikt Ziegler <benedikt.ziegler@combine.se>'
    copyright = '(C) 2016 Combine Control Systems AB'
    version = '0.1'
    tags = Tags(Tag.Input.Generate)


class GenerateSignalTable(GenerateSignalBase):
    """
    Generates a table with signals like sinus, cosinus, etc.

    :ref. nodes: :ref:`Generate Signal Tables`
    """

    name = 'Generate Signal Table'
    icon = 'signal.svg'
    nodeid = 'org.sysess.sympathy.generate.signaltable'
    outputs = Ports([Port.Table('Signal Table', name='port0')])

    parameters = table_signal_base_parameters()

    controllers = (
        synode.controller(
            when=synode.field('use_period', 'checked'),
            action=(synode.field('frequency', 'disabled'),
                    synode.field('period', 'enabled'))),
        synode.controller(
            when=synode.field('add_noise', 'checked'),
            action=synode.field('noise_amplitude', 'enabled')))

    def execute(self, node_context):
        tf = node_context.output['port0']
        self.run(tf, node_context)

    def run(self, output, node_context):
        column_entries = node_context.parameters['table_params'][
            'column_entries'].value
        column_length = node_context.parameters['table_params'][
            'column_length'].value

        signal = node_context.parameters['signal_params'][
            'signal_type'].selected
        signal_func = SIGNALS[signal]
        amplitude = node_context.parameters['signal_params']['amplitude'].value
        frequency = node_context.parameters['signal_params']['frequency'].value
        period = node_context.parameters['signal_params']['period'].value
        use_period = node_context.parameters['signal_params'][
            'use_period'].value
        phase_offset = node_context.parameters['signal_params'][
            'phase_offset'].value
        noise = node_context.parameters['signal_params']['add_noise'].value
        noise_amplitude = node_context.parameters['signal_params'][
            'noise_amplitude'].value
        add_index_column = node_context.parameters['signal_params'][
            'index_column'].value

        if not use_period:
            period = 1. / frequency

        x = np.arange(column_length)

        for index in range(column_entries):
            if add_index_column and index == 0:
                data = np.arange(column_length)
                column_name = 'index'
            else:
                data = self.compute_signal(
                    x, signal_func, amplitude, period, phase_offset, noise,
                    noise_amplitude)
                column_name = '{}{}'.format(signal, index)
            output.set_column_from_array(column_name, data)
            self.set_progress(100.0 * (1.0 + index) / column_entries)

    def compute_signal(self, x, func, amplitude, period,
                       phase_offset, noise=False, noise_amplitude=0.01):
        data = amplitude * func(2. * np.pi / period * x + phase_offset)
        if noise:
            data += noise_amplitude * nrandom(len(x))
        return data


class GenerateSignalTables(GenerateSignalBase):
    """
    Generates a list of tables with signals like sinus, cosinus, etc.

    :ref. nodes: :ref:`Generate Signal Table`
    """

    name = 'Generate Signal Tables'
    icon = 'signal.svg'
    nodeid = 'org.sysess.sympathy.generate.signaltables'
    outputs = Ports([Port.Tables('Signal Tables', name='port0')])

    parameters = table_signal_base_parameters()
    parameters['table_params'].set_integer(
        'length', value=5, label='Table list length',
        description='The length of table list to be generated.',
        editor=synode.Util.bounded_spinbox_editor(0, 10000, 1))

    controllers = (
        synode.controller(
            when=synode.field('use_period', 'checked'),
            action=(synode.field('frequency', 'disabled'),
                    synode.field('period', 'enabled'))),
        synode.controller(
            when=synode.field('add_noise', 'checked'),
            action=synode.field('noise_amplitude', 'enabled')))

    def execute(self, node_context):
        length = node_context.parameters['table_params']['length'].value
        tfs = node_context.output['port0']
        single = GenerateSignalTable()
        for idx in range(length):
            tf = tfs.create()
            single.run(tf, node_context)
            tfs.append(tf)
            self.set_progress(100.0 * (1.0 + idx) / length)
