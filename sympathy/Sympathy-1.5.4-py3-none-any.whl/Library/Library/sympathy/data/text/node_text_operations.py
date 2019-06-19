# coding=utf8
# Copyright (c) 2016-2017, Combine Control Systems AB
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

import jinja2

from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags

from sylib.calculator import calculator_model
import sylib.calculator.plugins


class ConcatenateTexts(synode.Node):
    """Concatenate two texts"""

    name = 'Concatenate texts'
    nodeid = 'org.sysess.sympathy.texts.concatenatetexts'
    author = 'Magnus Sandén <magnus.sanden@combine.se>'
    copyright = "(C) 2016 Combine Control Systems AB"
    version = '1.0'
    icon = 'concatenate.svg'
    tags = Tags(Tag.DataProcessing.Text)

    inputs = Ports([
        Port.Custom('text', 'Text part', name='in', n=(2, None, 2))])
    outputs = Ports([Port.Text('Concatenated text', name='out')])

    parameters = synode.parameters()
    parameters.set_string(
        'sep', value='', label='Separator:',
        description='A string to be inserted between each part.',
        editor=synode.editors.textedit_editor())

    def execute(self, node_context):
        sep = node_context.parameters['sep'].value
        inputs = node_context.input.group('in')
        text_parts = [p.get() for p in inputs]
        node_context.output['out'].set(sep.join(text_parts))


class Jinja2TemplateOld(synode.Node):
    """
    Create and render a jinja2 template. See `Jinja2
    <http://jinja.pocoo.org/>`_ for full syntax of the template engine.

    Use {{column name}} for accessing the first row of a column, or use 'arg'
    inside a jinja for-loop to access full table.

    Example of iterating over each column::

       {% for name in arg.column_names() %}
          The column name is: {{name}}
          The column data is: {% for value in arg.col(name).data %} {{value}} {% endfor %}
       {% endfor %}

    Example of iterating over each row::

       {% for row in arg.to_rows() %}
          {% for value in row %} {{value}} {% endfor %}
       {% endfor %}

    """

    name = 'Jinja2 template (deprecated)'
    nodeid = 'org.sysess.sympathy.texts.jinja2template'
    author = 'Magnus Sandén <magnus.sanden@combine.se'
    copyright = "(C) 2016 Combine Control Systems AB"
    version = '0.1'
    icon = 'jinja_template.svg'
    description = (
        'Create and render a jinja2 template. Use "{{column name}}" for '
        'access to the first row of columns, or use "arg" inside a jinja '
        'for-loop to access full table.')

    tags = Tags(Tag.Hidden.Replaced)

    parameters = synode.parameters()
    jinja_code_editor = synode.Util.code_editor(language="jinja").value()
    parameters.set_string(
        'template', label="Template:", description='Enter template here',
        editor=jinja_code_editor)

    inputs = Ports([Port.Table('Input data', name='in')])
    outputs = Ports([Port.Text('Rendered Template', name='out')])

    def execute(self, node_context):
        infile = node_context.input['in']
        outfile = node_context.output['out']
        parameters = node_context.parameters
        template_string = parameters['template'].value

        jinja_env = jinja2.Environment()
        template = jinja_env.from_string(template_string)

        # Add metadata to template
        metadata = {'arg': infile}
        for col in infile.cols():
            metadata[col.name] = col.data[0].tolist()

        rendered_template = template.render(metadata)
        outfile.set(rendered_template)


class Jinja2Template(synode.Node):
    """
    Create and render a jinja2 template. See `Jinja2
    <http://jinja.pocoo.org/>`_ for full syntax of the template engine.

    Input data can be of any type and is accessed using {{arg}}.

    The examples below assume that the first input is a table.

    Example of iterating over each column::

       {% for name in arg.column_names() %}
          The column name is: {{name}}
          The column data is: {% for value in arg.col(name).data %} {{value}} {% endfor %}
       {% endfor %}

    Example of iterating over one specific column::

       {% for value in arg.col('Foo').data %}
          {{ value }}
       {% endfor %}

    Example of iterating over each row::

       {% for row in arg.to_rows() %}
          {% for value in row %} {{value}} {% endfor %}
       {% endfor %}

    The examples below assume that you have created a tuple or list of tables
    as input::

       {% for tbl in arg %}
          Table name: {{ tbl.name }}
          {% for col in tbl.cols() %}
             {{ col.name }}: {% for x in col.data %} {{x}} {% endfor %}
          {% endfor %}
       {% endfor %}

    Finally, you can connect complex datatypes such as an ADAF to the node::

       {% for name, col in arg.sys['system0']['raster0'].items() %}
          Signal: {{name}}
          Time: {{ col.t }}
          Value:  {{ col.y }}
       {% endfor %}

    Have a look at the :ref:`Data type APIs<datatypeapis>` to see what methods
    and attributes are available on the data type that you are working with.
    """

    name = 'Jinja2 template'
    nodeid = 'org.sysess.sympathy.texts.generic_jinja2template'
    author = 'Magnus Sandén <magnus.sanden@combine.se'
    copyright = "(C) 2016 Combine Control Systems AB"
    version = '0.1'
    icon = 'jinja_template.svg'
    description = (
        'Create and render a jinja2 template. Use "{{arg name}}" for access '
        'to the data.')

    tags = Tags(Tag.DataProcessing.Text)

    parameters = synode.parameters()
    jinja_code_editor = synode.Util.code_editor(language="jinja").value()
    parameters.set_string(
        'template', label="Template:", description='Enter template here',
        editor=jinja_code_editor)

    inputs = Ports([Port.Custom('<a>', 'Input', 'in', n=(0,1,1))])
    outputs = Ports([Port.Text('Rendered Template', name='out')])

    def execute(self, node_context):
        infile = node_context.input.group('in')
        outfile = node_context.output['out']
        parameters = node_context.parameters
        template_string = parameters['template'].value

        jinja_env = jinja2.Environment()
        template = jinja_env.from_string(template_string)

        env = calculator_model.context
        plugins = sylib.calculator.plugins.available_plugins()
        for plugin in plugins:
            env.update(plugin.globals_dict())
            env.update(plugin.imports())

        if len(infile) > 0:
            env['arg'] = infile[0]

        rendered_template = template.render(env)
        outfile.set(rendered_template)
