# coding=utf-8
# Copyright (c) 2013, 2017-2018 Combine Control Systems AB
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
A collection of examples that illustrates a number of details that are
important in order to create nodes for Sympathy of Data. The usage of content
in this file should be combined with the Node Writing Tutorial.
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import time
import collections

import numpy as np
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api.exceptions import SyNodeError, sywarn


OPTIONS_DICT = collections.OrderedDict([
    ('opt1', 'First option (default)'),
    ('opt2', 'Second option'),
    ('opt3', 'Third option'),
])


class HelloWorld(synode.Node):
    """
    This, minimal, example prints a fixed "Hello world!" greeting when
    executed.
    """

    name = 'Hello world example'
    nodeid = 'org.sysess.sympathy.examples.helloworld'
    tags = Tags(Tag.Development.Example)

    def execute(self, node_context):
        print('Hello world!')


class HelloWorldCustomizable(synode.Node):
    """
    This example prints a customizable greeting. Default greeting is "Hello
    world!".

    :Ref. nodes: :ref:`Output example`, :ref:`Error example`
    """

    name = 'Hello world customizable example'
    description = 'Node demonstrating the basics of node creation.'
    icon = 'example.svg'
    nodeid = 'org.sysess.sympathy.examples.helloworldcustomizable'
    author = 'Magnus Sandén <magnus.sanden@combine.se>'
    copyright = '(c) 2014 Combine Control Systems AB'
    version = '1.0'
    tags = Tags(Tag.Development.Example)

    parameters = synode.parameters()
    parameters.set_string(
        'greeting', value='Hello world!', label='Greeting:',
        description='Your preferred greeting.')

    def execute(self, node_context):
        print(node_context.parameters['greeting'].value)


class OutputExample(synode.Node):
    """
    This example demonstrates how to write data to an outgoing Table.

    :Ref. nodes: :ref:`Hello world example`, :ref:`Error example`
    """

    name = 'Output example'
    description = 'Node demonstrating how to write a table.'
    icon = 'example.svg'
    nodeid = 'org.sysess.sympathy.examples.outputexample'
    author = 'Magnus Sandén <magnus.sanden@combine.se>'
    copyright = '(c) 2014 Combine Control Systems AB'
    version = '1.0'
    tags = Tags(Tag.Development.Example)

    outputs = Ports([
        Port.Table("Table with a column named 'Enumeration' with values 1-99",
                   name='output')])

    def execute(self, node_context):
        """Execute node"""
        tablefile = node_context.output['output']
        data = np.arange(1, 101, dtype=int)
        tablefile.set_name('Output Example')
        tablefile.set_column_from_array('Enumeration', data)


class ErrorExample(synode.Node):
    """
    Demonstrates how to give the user error messages or warnings and how that
    is shown in the platform.

    :Ref. nodes: :ref:`Hello world example`, :ref:`Output example`
    """

    name = 'Error example'
    description = 'Node demonstrating the error handling system.'
    icon = 'example_error.svg'
    nodeid = 'org.sysess.sympathy.examples.errorexample'
    author = 'Stefan Larsson <stefan.larsson@combine.se>'
    copyright = '(C)2011-2012,2015 Combine Control Systems AB'
    version = '2.0'
    tags = Tags(Tag.Development.Example)

    parameters = synode.parameters()
    parameters.set_string(
        'severity', value='Error', label='Severity:',
        description='Choose how severe the error is.',
        editor=synode.editors.combo_editor(
            options=['Notice', 'Warning', 'Error', 'Exception']))
    parameters.set_string(
        'error_msg', label='Error message:',
        description='This error message will be shown when executing the node',
        value='This is an expected error.')

    def execute(self, node_context):
        severity = node_context.parameters['severity'].value
        error_msg = node_context.parameters['error_msg'].value
        if severity == 'Notice':
            print(error_msg)
        elif severity == 'Warning':
            sywarn(error_msg)
        elif severity == 'Error':
            raise SyNodeError(error_msg)
        elif severity == 'Exception':
            raise Exception(error_msg)


class AllParametersExample(synode.Node):
    """
    This node includes all available configuration options for initialising
    parameters. The configuration GUI is automatically generated by the
    platform.

    :Configuration: All types of configuration options
    :Ref. nodes: :ref:`Hello world example`, :ref:`Output example`
    """

    name = 'All parameters example'
    description = 'Node showing all different parameter types.'
    icon = 'example.svg'
    nodeid = 'org.sysess.sympathy.examples.allparameters'
    author = 'Alexander Busck <alexander.busck@combine.se>'
    copyright = '(C)2011-2012,2015 Combine Control Systems AB'
    version = '1.0'
    tags = Tags(Tag.Development.Example)

    parameters = synode.parameters()
    numbers_page = parameters.create_page('numbers', label='Numbers')
    float_group = numbers_page.create_group('float', label='Floats')
    float_group.set_float('stringfloat',
                          label='Float in a line edit',
                          description='A float',
                          value=0.1234)
    float_group.set_float('spinfloat',
                          label='Float in a spinbox',
                          description='A float',
                          value=0.1234,
                          editor=synode.editors.bounded_decimal_spinbox_editor(
                              0.0, 4.0, 0.1, 4))
    float_group.set_float('combo_float1',
                          label='Float with static options',
                          value=0.,
                          description='Float parameter with '
                          'predefined options.',
                          editor=synode.editors.combo_editor(
                              options=[0.1, 0.2, 0.3]))
    float_group.set_float('combo_float2',
                          label='Float with editable static options',
                          value=1.0,
                          description='Float parameter with '
                          'predefined options.',
                          editor=synode.editors.combo_editor(
                              options=[0.1, 0.2, 0.3], edit=True))

    integer_group = numbers_page.create_group('integer', label='Integers')
    integer_group.set_integer('stringinteger',
                              label='Integer in a line edit',
                              description='An integer',
                              value=1234,
                              editor=synode.editors.bounded_lineedit_editor(
                                  0, 2000, placeholder='Number between 0 '
                                                       'and 2000'))
    integer_group.set_integer('spininteger',
                              label='Integer in a spinbox',
                              description='An integer',
                              value=1234,
                              editor=synode.editors.bounded_spinbox_editor(
                                  0, 2000, 10))
    integer_group.set_integer('combo_integer1',
                              label='Integer with static options',
                              value=1,
                              description='Integer parameter with '
                              'predefined options.',
                              editor=synode.editors.combo_editor(
                                  options=[1, 2, 3]))
    integer_group.set_integer('combo_integer2',
                              label='Integer with editable static options',
                              value=1,
                              description='Integer parameter with '
                              'predefined options.',
                              editor=synode.editors.combo_editor(
                                  options=[1, 2, 3], edit=True))
    integer_group.set_integer('combo_integer3',
                              label='Integer with dynamic options',
                              value=1,
                              description='Integer parameter with '
                              'dynamic options.',
                              editor=synode.editors.combo_editor(edit=True))

    string_page = parameters.create_page('strings', label='Strings')
    string_group = string_page.create_group('strings', label='Normal strings')
    string_group.set_string('lineedit',
                            label='String in a line edit',
                            value='Hello',
                            description='Text on a single line',
                            editor=synode.editors.lineedit_editor(
                                'Hello World!'))
    string_group.set_string('textedit',
                            label='String in a text edit',
                            value='This is a\nmulti-line\neditor',
                            editor=synode.editors.textedit_editor())
    string_group.set_string('combo_string1',
                            label='String with static options',
                            value='B',
                            description='String parameter with '
                                        'predefined options.',
                            editor=synode.editors.combo_editor(
                                options=['A', 'B', 'C']))
    string_group.set_string('combo_string2',
                            label='String with dynamic options and filter',
                            value='',
                            description=(
                                'String parameter with '
                                'dynamic options. The case arises naturally '
                                'when selecting column names from some input. '
                                'Filter is enabled and suited to deal with '
                                'a large number of choices'),
                            editor=synode.editors.combo_editor(
                                include_empty=True, filter=True))
    string_group.set_string('combo_string3',
                            label='String with key-value options',
                            value='opt1',
                            description='String parameter with '
                                        'predefined options.',
                            editor=synode.editors.combo_editor(
                                options=OPTIONS_DICT))
    string_group.set_string('combo_string4',
                            label='String with editable selection',
                            value='B',
                            description='String parameter with '
                            'predefined options. Selected option can be '
                            'edited (press return to confirm edit).',
                            editor=synode.editors.combo_editor(
                                options=['A', 'B', 'C'], edit=True))

    path_group = string_page.create_group('path', label='Paths')
    path_group.set_string('filename',
                          label='Filename',
                          description='A filename including path if needed',
                          value='test.txt',
                          editor=synode.editors.filename_editor(
                              ['Image files (*.png *.xpm *.jpg)',
                               'Text files (*.txt)',
                               'Any files (*)']))
    path_group.set_string('save_filename',
                          label='Save filename',
                          description='A filename including path if needed',
                          value='test.txt',
                          editor=synode.editors.savename_editor(
                              ['Image files (*.png *.xpm *.jpg)',
                               'Text files (*.txt)',
                               'Any files (*)']))
    path_group.set_string('directory',
                          label='Directory',
                          description='A directory including path if needed',
                          value='MyDirectory',
                          editor=synode.editors.directory_editor())

    logics_page = parameters.create_page('logics', label='Logics')
    logics_page.set_boolean('boolflag',
                            label='Boolean',
                            description=('A boolean flag indicating true or '
                                         'false'),
                            value=True)

    lists_page = parameters.create_page('lists', label='Lists')
    lists_page.set_list('combo',
                        label='Combo box',
                        description='A combo box',
                        value=[1],
                        plist=['First option',
                               'Second option',
                               'Third option'],
                        editor=synode.editors.combo_editor(include_empty=True))
    lists_page.set_list('editcombo',
                        label='Editable combo box',
                        description='An editable combo box. Selected option '
                        'can be edited (press return to confirm edit).',
                        value=[1],
                        plist=['First option',
                               'Second option',
                               'Third option'],
                        editor=synode.editors.combo_editor(
                            include_empty=True, edit=True))
    lists_page.set_list('alist',
                        label='List view',
                        description='A list',
                        editor=synode.editors.list_editor())
    lists_page.set_list('editlist',
                        label='Editable list view',
                        description=(
                            'An editable lists (use double-click, '
                            'right-click). Only checked elements are saved.'),
                        plist=['Element1', 'Element2', 'Element3'],
                        editor=synode.editors.list_editor(edit=True))
    lists_page.set_list('multilist',
                        label='List view with multiselect',
                        description='A list with multiselect',
                        value=[0, 2],
                        plist=['Element1', 'Element2', 'Element3'],
                        editor=synode.editors.multilist_editor())
    lists_page.set_list('editmultilist',
                        label='Editable list view with multiselect',
                        description=(
                            'An editable multiselect list (use double-click, '
                            'right-click). Only checked elements are saved.'),
                        value=[0, 2],
                        plist=['Element1', 'Element2', 'Element3'],
                        editor=synode.editors.multilist_editor(edit=True))

    def adjust_parameters(self, node_context):
        """
        This method is called before configure. In this example it fills one of
        the lists and a couple of comboboxes with alternatives.
        """
        node_context.parameters['lists']['alist'].adjust(
            ['My', 'Programmatically', 'Generated', 'List'])
        node_context.parameters['strings']['strings']['combo_string2'].adjust(
            ['My', 'Programmatically', 'Generated', 'Options',
             'With', 'Several', 'Choices'])
        node_context.parameters['numbers']['integer']['combo_integer3'].adjust(
            [0, 1, 2, 3])

    def execute(self, node_context):
        """
        You always have to implement the execute method to be able to execute
        the node. In this node we don't want the execute method to actually do
        anything though.
        """
        pass


class ProgressExample(synode.Node):
    """
    This node runs with a delay and updates its progress during execution to
    let the user know how far it has gotten.

    :Ref. nodes: :ref:`Error example`
    """

    name = 'Progress example'
    description = 'Node demonstrating progress usage'
    icon = 'example.svg'
    nodeid = 'org.sysess.sympathy.examples.progress'
    author = 'Magnus Sandén <magnus.sanden@combine.se>'
    copyright = '(C)2015 Combine Control Systems AB'
    version = '1.0'
    tags = Tags(Tag.Development.Example)

    parameters = synode.parameters()
    parameters.set_float(
        'delay', value=0.02, label='Delay:',
        description='Delay between tables')

    def execute(self, node_context):
        """
        Loop with customizable delay from 0 to 99 and update the node's
        progress accordingly each iteration.
        """
        delay = node_context.parameters['delay'].value
        for i in range(100):
            self.set_progress(float(i))

            # In real applications this would be some lengthy calculation.
            time.sleep(delay)


class ControllerExample(synode.Node):
    """
    This example demonstrates how to use controllers to create more advanced
    configuration guis, while still relying on the automatic configuration
    builder. For more information about controllers see :ref:`the user
    manual<controllers>`.

    :Ref. nodes: :ref:`All parameters example`, :ref:`Hello world example`
    """

    name = 'Controller example'
    description = 'Node demonstrating controller usage'
    icon = 'example.svg'
    nodeid = 'org.sysess.sympathy.examples.controller'
    author = 'Magnus Sandén <magnus.sanden@combine.se>'
    copyright = '(C)2016 Combine Control Systems AB'
    version = '1.0'
    tags = Tags(Tag.Development.Example)

    parameters = synode.parameters()
    value_group = parameters.create_group('fruit', label='Fruit')
    value_group.set_string(
        'fruit', value='Apples', label='Apples or oranges?',
        description='Which fruit do you prefer?',
        editor=synode.editors.combo_editor(['Apples', 'Oranges']))
    value_group.set_string(
        'color', value='', label='Color:',
        description='What color should the apples have?')
    value_group.set_string(
        'size', value='Small', label='Size:',
        description='What size should the oranges have?',
        editor=synode.editors.combo_editor(['Small', 'Big', 'Really big']))
    checked_group = parameters.create_group('delivery', label='Delivery')
    checked_group.set_boolean(
        'delivery', value=False, label='Drone delivery:',
        description='When checked, drones will deliver the fruit to you, '
                    'wherever you are.')
    checked_group.set_string(
        'address', value='', label='Adress:',
        description='Your full address.')

    controllers = (
        synode.controller(
            when=synode.field('fruit', 'value', value='Apples'),
            action=(synode.field('color', 'enabled'),
                    synode.field('size', 'disabled'))),
        synode.controller(
            when=synode.field('delivery', 'checked'),
            action=synode.field('address', 'enabled')))

    def execute(self, node_context):
        pass


class ReadWriteExample(synode.Node):
    """
    This example node demonstrates how to read from and write to a list of
    tables. It forwards tables from the input to the output using the source
    method available for tables and other data types. This will forward data
    from one file to another, without making needless copies. Instead the data
    is linked to the source whenever possible.

    To run this node you can connect its input port to e.g. a
    :ref:`Random Tables` node.
    """

    name = 'Read/write example'
    description = (
        'Node demonstrating how to read from/write to lists of tables.')
    icon = 'example.svg'
    nodeid = 'org.sysess.sympathy.examples.readwrite'
    author = 'Magnus Sandén <magnus.sanden@combine.se>'
    copyright = '(C)2016 Combine Control Systems AB'
    version = '1.0'
    tags = Tags(Tag.Development.Example)

    inputs = Ports([Port.Tables('Input Tables', name='input')])
    outputs = Ports([Port.Tables('Output Tables', name='output')])

    def execute(self, node_context):
        """Loop over all the tables in the input and forward some them."""
        out_tables = node_context.output['output']
        for i, in_table in enumerate(node_context.input['input']):
            # Forward every second table:
            if i % 2 == 0:
                out_table = out_tables.create()
                out_table.source(in_table)
                out_tables.append(out_table)
