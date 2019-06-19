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
"""The F(x) nodes all have a similar role as the :ref:`Calculator List`
node. But where the :ref:`Calculator List` node shines when the calculations
are simple, the f(x) nodes are better suited for more advanced calculations
since the code is kept in a separate python file. You can place this python
file anywhere, but it might be a good idea to keep it in the same folder as
your workflow or in a subfolder to that folder.


The script file
^^^^^^^^^^^^^^^
When writing a "function" (it is actually a python class) you need to inherit
from ``FxWrapper``. The ``FxWrapper`` provides access to the input and output
with ``self.arg`` and ``self.res`` respectively. These variables are of the
same type as the input on port2. Consult the API for that type to figure out
relevant operations.

The field ``arg_types`` is a list containing string representations of types
(as shown in port tooltips) that you intend your script to support and
determines the types for which the function is available.

For example::

    from sympathy.api import fx_wrapper

    class MyCalculation(fx_wrapper.FxWrapper):
        arg_types = ['table']

        def execute(self):
            spam = self.arg.get_column_to_array('spam')

            # My super advanced calculation that totally couldn't be
            # done in the :ref:`Calculator Lists` node:
            more_spam = spam + 1

            self.res.set_column_from_array('more spam', more_spam)


The same script file can be used with both :ref:`F(x)` and :ref:`F(x) List`
nodes.

A quick way to get the skeleton for a function is to use the function wizard
that is started by clicking *File->New Function*.


Debugging your script
^^^^^^^^^^^^^^^^^^^^^
F(x) scripts can be debugged in spyder by following these simple steps:

#. Open the script file in spyder and place a breakpoint somewhere in the
   execute method that you want to debug.
#. Go back to Sympathy and right-click and choose *Debug* on the f(x) node with
   that function selected.
#. Make sure that the file *node_fx_selector.py* is the active file in spyder
   and press *Debug file* (Ctrl+F5).
#. A third python file will open as the debugging starts. Press *Continue*
   (Ctrl+F12) to arrive at the breakpoint in your f(x) script. From here you
   can step through your code however you want to.


Configuration
^^^^^^^^^^^^^
When *Copy input* is disabled (the default) the output table will be empty
when the functions are run.

When the *Copy input* setting is enabled the entire input table will get
copied to the output before running the functions in the file. This is useful
when your functions should only add a few columns to a data table, but in this
case you must make sure that the output has the same number of rows as the
input.

By default (*pass-through* disabled) only the functions that you have manually
selected in the configuration will be run when you execute the node, but with
the *pass-through* setting enabled the node will run all the functions in the
selected file. This can be convenient in some situations when new functions are
added often.

"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
from sympathy.api import node as synode
from sympathy.api import fx_wrapper
from sympathy.api.nodeconfig import Port, Ports
from sylib.fx_selector import (
    FxSelector, FxSelectorList)
from sympathy.api.nodeconfig import Tag, Tags


def _base_params():
    parameters = synode.parameters()
    editor = synode.Util.multilist_editor()
    parameters.set_boolean(
        'copy_input', value=False, label='Copy input',
        description=('If enabled the incoming data will be copied to the '
                     'output before running the nodes.'))
    parameters.set_list(
        'selected_functions', value=[], label='Select functions',
        description=('Choose one or many of the listed functions to apply to '
                     'the content of the incoming item.'), editor=editor)
    return parameters


class Fx(synode.Node):
    """
    Apply functions to an item.

    Functions based on FxWrapper will be invoked once on the item.
    The functions available are the ones where ``arg_types`` of the function
    matches the type of the item port (port2).

    :Ref. nodes: :ref:`F(x) List`
    """

    name = 'F(x)'
    description = 'Select and apply functions to item.'
    nodeid = 'org.sysess.sympathy.data.fx'
    author = 'Erik der Hagopian <erik.hagopian@combine.se>'
    copyright = '(C) 2016 Combine Control Systems AB'
    version = '1.0'
    icon = 'fx.svg'
    parameters = _base_params()
    tags = Tags(Tag.DataProcessing.Calculate)
    wrapper_cls = fx_wrapper.FxWrapper
    inputs = Ports([
        Port.Datasource(
            'Path to Python file with scripted functions.', name='port1'),
        Port.Custom(
            '<a>', 'Item with data to apply functions on', name='port2')])
    outputs = Ports([
        Port.Custom('<a>',
                    'Item with the results from the applied functions',
                    name='port3')])

    def __init__(self):
        super(Fx, self).__init__()
        self._base = FxSelector()

    def adjust_parameters(self, node_context):
        return self._base.adjust_parameters(node_context)

    def exec_parameter_view(self, node_context):
        return self._base.exec_parameter_view(node_context)

    def execute(self, node_context):
        self._base.execute(node_context, self.set_progress)


class FxList(synode.Node):
    """
    Apply functions to a list of items.

    Functions based on FxWrapper will be invoked once for each item in the list
    with each item as argument.
    The functions available are the ones where ``arg_types`` of the function
    matches the type of the individual items from the list port (port2).

    :Ref. nodes: :ref:`F(x)`
    """

    name = 'F(x) List'
    description = 'Select and apply functions to List.'
    author = 'Erik der Hagopian <erik.hagopian@combine.se>'
    copyright = '(C) 2016 Combine Control Systems AB'
    version = '1.0'
    icon = 'fx.svg'
    nodeid = 'org.sysess.sympathy.data.generic.fxlist'
    parameters = _base_params()
    tags = Tags(Tag.DataProcessing.Calculate)
    wrapper_cls = fx_wrapper.FxWrapper
    inputs = Ports([
        Port.Datasource(
            'Path to Python file with scripted functions.', name='port1'),
        Port.Custom(
            '[<a>]', 'List with data to apply functions on', name='port2')])
    outputs = Ports([
        Port.Custom(
            '[<a>]',
            'List with function(s) applied', name='port3')])

    def __init__(self):
        super(FxList, self).__init__()
        self._base = FxSelectorList()

    def exec_parameter_view(self, node_context):
        return self._base.exec_parameter_view(node_context)

    def adjust_parameters(self, node_context):
        return self._base.adjust_parameters(node_context)

    def execute(self, node_context):
        self._base.execute(node_context, self.set_progress)
