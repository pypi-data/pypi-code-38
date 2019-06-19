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
The Plot Table nodes are an all-in-one tool to visualize and investigate data.
It is also possible to perform simpler statistical calculations in the node.

The node configuration window is divided into two parts, the plot window and
the configuration window.

The plot window has three parts, the Refresh button, the plot, and the toolbar.
The Refresh button updates the plot window according to the changes in the
configuration.

The toolbar can be used to manipulate the plot window:
    - Reset view
        Goes to default zoom and pan.

    - Back
        Goes to the previous view.

    - Forward
        Goes to the next view.

    - Pan
        This tool will pan the plot with left click, and right click will zoom
        the plot using the mouse direction as its axis. When using multiple
        vertical axes and zooming with this tool the results may be
        surprising, or useful, depending on the situation. If the former
        happens, the ordinary zoom tool should work as expected.

    - Zoom
        The magnifying glass enables zooming in and out using a box drawn with
        the mouse. Left click drag will zoom in, and right click drag will
        zoom out.

    - Save
        Saves the current plot to disk.

    - Data cursor
        Click this button to enable the showing of data points by clicking in
        the plot. If signals intersect in the point they will all be shown.
        A current limitation is that only values that are plotted against
        the first vertical (Y) axis can be shown.

    - Select interval
        After clicking this button the next two clicks in the plot will draw
        lines which will define the area in which statistics will be
        calculated. To move any of the lines after they have been created,
        just click on one of them and use the scroll wheel to move it.
        Please note that if your X axis is not sorted, you will get
        unpredictable results. Use the Sort Table/Tables node if
        neceessary.

===============================================================================

The configuration window has four tabs:
    - Plot
        In the Plot tab you can create one or many plots. The currently
        selected one is the one that the rest of the tabs will affect.

    - Axis
        In the Axis tab the axes for the plot are created. It is possible to
        create multiple Y axes and one X axis. Limits can be used to set
        the default view to  certain range (i.e., zoom). If these are not
        set the window will be fitted to the whole data set.

        Ticks sets markers at the wished increments and determines how the
        grid will look, if enabled.

    - Signal
        In the Signal tab the signals are created and configured. For each
        signal the proper axes are set, and wich data from the input that
        should be shown.

        In the Line and Marker sections the characteristics of the lines
        and data points can be set. Using the '...' button colors can
        easily be set using a picker.

    - Statistics
        On the Statistics tab the standard deviation, mean, min, and max for
        the chosen signals can be shown. The avaliable signals are located
        in the Signal section where they can be added/deleted to show/hide
        statistics from the specific signal. By default all available
        signals are loaded and shown in the table.

        In the Statistics section there are checkboxes for the different
        statistics choices. These checkboxes determines if the statistic is
        shown in the table and/or the plot (depending on the Show
        Statistics checkbox). The plot information is updated by pressing
        the Refresh button.

        The Limits section shows the intervals set by the Select interval
        toolbar option, described above.

        Note: Contrary to the other tabs, the Statistics configuration will
        not be saved upon exiting the node, and therefore any changes made
        to the plot must be saved as pictures in this node, if you want to
        retain the results.

===============================================================================
"""
import json
import functools
from collections import OrderedDict

try:
    from mock import MagicMock
except ImportError:
    class MagicMock(object):
        pass
import numpy as np

from sympathy.api import node as synode
from sympathy.api import qt as qt_compat
from sympathy.api import table as sytable
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sylib.plot import model as plot_models
from sylib.plot import gui as plot_guis
QtCore = qt_compat.QtCore
QtGui = qt_compat.import_module('QtGui')


# If numpy is mocked we can't create PlotsModel so fall back on empty string.
# This is required for generating documentation on Read the Docs.
if isinstance(np, MagicMock):
    DEFAULT_VALUE = ''
else:
    DEFAULT_VALUE = json.dumps(plot_models.PlotsModel().to_dict(), indent=4)


def get_plot_model(node_context, in_table):
    plot_model_string = node_context.parameters['plots model'].value
    if plot_model_string == '':
        return plot_models.PlotsModel(table=in_table)
    else:
        return plot_models.PlotsModel(
            json.loads(plot_model_string, object_pairs_hook=OrderedDict),
            table=in_table)


def set_model(parameters, model):
    parameters['plots model'].value = json.dumps(
        model.to_dict(), indent=4)


class PlotTable(synode.Node):
    author = "Erik der Hagopian <erik.hagopian@combine.se>"
    copyright = "(C) 2014 Combine Control Systems AB"
    version = '0.6'
    icon = 'scatter2d.svg'
    name = 'Plot Table'
    description = 'Plot Table'
    nodeid = 'org.sysess.sympathy.visualize.plottable'
    tags = Tags(Tag.Visual.Plot)

    parameters = synode.parameters()
    parameters.set_string(
        'plots model', label='GUI', value=DEFAULT_VALUE,
        description='Configuration window')

    inputs = Ports([Port.Table('Input Table',
                               name='input', requiresdata=True)])
    outputs = Ports([Port.Table('Output Table with "plots model" attribute',
                                name='output')])

    def exec_parameter_view(self, node_context):
        in_table = node_context.input['input']
        if not in_table.is_valid():
            in_table = sytable.File()
        plots_model = get_plot_model(node_context, in_table)
        widget = plot_guis.MainWidget(
            plots_model, save_model=functools.partial(
                set_model, node_context.parameters))
        QtCore.QTimer.singleShot(0, widget.plot)
        return widget

    def execute(self, node_context):
        in_table = node_context.input['input']
        out_table = node_context.output['output']
        plots_model = get_plot_model(node_context, in_table)
        out_table.set_name(in_table.get_name())
        out_table.update(in_table)
        plots_model.set_table(out_table)
        plots_model.write_table_attribute()


class PlotTables(synode.Node):
    author = "Erik der Hagopian <erik.hagopian@combine.se>"
    copyright = "(C) 2014 Combine Control Systems AB"
    version = '0.6'
    icon = 'scatter2d.svg'
    name = 'Plot Tables'
    description = 'Plot Tables'
    nodeid = 'org.sysess.sympathy.visualize.plottables'
    tags = Tags(Tag.Visual.Plot)

    inputs = Ports([Port.Tables('Input Tables',
                                name='input', requiresdata=True)])
    outputs = Ports([Port.Tables('Output Tables with "plots model" attribute',
                                 name='output')])

    parameters = synode.parameters()
    parameters.set_string(
        'plots model', label='GUI', value=DEFAULT_VALUE,
        description='Configuration window')

    def exec_parameter_view(self, node_context):
        in_tables = node_context.input['input']
        if in_tables.is_valid() and len(in_tables):
            in_table = in_tables[0]
        else:
            in_table = sytable.File()

        plots_model = get_plot_model(node_context, in_table)
        widget = plot_guis.MainWidget(
            plots_model, save_model=functools.partial(
                set_model, node_context.parameters))
        QtCore.QTimer.singleShot(0, widget.plot)
        return widget

    def execute(self, node_context):
        in_tables = node_context.input['input']
        out_tables = node_context.output['output']

        for in_table in in_tables:
            out_table = sytable.File()
            plot_model = get_plot_model(node_context, in_table)
            out_table.set_name(in_table.get_name())
            out_table.update(in_table)
            plot_model.set_table(out_table)
            plot_model.write_table_attribute()
            out_tables.append(out_table)
