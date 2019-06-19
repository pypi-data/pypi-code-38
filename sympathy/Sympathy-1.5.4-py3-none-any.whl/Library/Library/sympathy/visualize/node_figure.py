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

import json
import six
import numpy as np

from sympathy import api
from sympathy.api import node as synode
from sympathy.api import qt as qt_compat
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust
from sympathy.api.nodeconfig import join_doc

from sympathy.platform.exceptions import SyConfigurationError

from sylib.figure import util, gui, mpl_utils


# OVERVIEW_DOCSTRING = """
#  The
# :ref:`Figure Compressor` node allows to compress a list of Figures into one
# single Figure, while the :ref:`Layout Figures in Subplots` generates a Figure
# with subplots. Figures can be exported using the :ref:`Export Figures` node.
# """

TREEVIEW_DOCSTRING = """
Both of the nodes :ref:`Figure` and :ref:`Figures` are used to configure
figures in a graphical user interface. They both output the figure(s) on the
upper port and a configuration table an optional lower port. The configuration
table can be used in the nodes :ref:`Figure from Table with Table` and
:ref:`Figures from Tables with Table`.

The configuration gui for these nodes consists of a toolbar and a tree view.
The tree view has two columns: one for the configuration items and one for
their values.

You can add plots to the figure by clicking on its corresponding button in the
toolbar, or by pressing on a plot button and dragging it to where in the tree
view you want it (possible drop locations will be shown in green). The plot
will be added with some basic properties depending on which plot type you added
(e.g. *X Data* and *Y Data* for line plot). Almost all configuration items
support more than the default properties. To add more, right-click on a
configuration item and choose "Add..." or "Add property" depending on what you
want to add.

Properties that allow free text are interpreted as python code and executed. In
this python evironment the input data table is available under the name ``arg``
(``table`` can also be used for historical reasons). For example one can refer
to data columns in a connected Table by writing something like
``arg['My data column']``. Have a look at the :ref:`datatypeapis` to see all
the available methods and attributes for the data type that you connect to the
node.

Use the node :ref:`Export figures` to write any figures you produce to files.
"""

CONF_TABLE_DOCSTRING = """
Having the full configuration for the figure as a table on an input port allow
you to programmatically configure a figure. If you are looking for an eaiser
but slightly less powerful way to configure a figure you should instead use one
of the nodes :ref:`Figure` or :ref:`Figures` where you
can configure the figure in a graphical user interface.

The configuration table consists of one parameter column and one value column.
Both column should be of text type. The easiest way to learn how to create a
specific figure with this node is to first build the same figure using the node
:ref:`Figure` and look at the configuration table that that node
produces.

Here is a simple example of a configuration table for a line plot:

    =========================== ===================
    Parameters                  Values
    =========================== ===================
    axes.axes-1.xaxis_position  bottom
    axes.axes-1.yaxis_position  left
    axes.axes-1.title           Plot title
    axes.axes-1.xlabel          The xlabel
    axes.axes-1.ylabel          The ylabel
    line.line-1.axes            axes-1
    line.line-1.xdata           ``table.col('x').data``
    line.line-1.ydata           ``table.col('y').data``
    =========================== ===================


**Plots**

Every line/scatter is addressed with a unique
identifier *{id}*, which can be any string without a '.'. A
line parameter is constructed as with *line.{id}.{property}*
in the parameter column and the corresponding value in the
value column. Every line needs to have at least the 'xdata'
and 'ydata' specified. All line properties, except the 'ydata',
can also be given on a *global* level like *line.{property}*.
All properties given on a global level with be copied to all
configured lines without overriding locally declared properties.

Currently supported properties are (some properties allow
alternative names *longname/shortname*):

===================== =====================
Property              Type
===================== =====================
xdata                 unicode
ydata                 unicode
axes                  *axes id* (see below)
label                 unicode
marker                matplotlib marker: o, ., ^, d, etc
markersize            float
markeredgecolor       mpl color (see below)
markeredgewidth       float
markerfacecolor       mpl color (see below)
linestyle             matplotlib line style: -, --, .-, etc
linewidth             float
color                 mpl color (see below)
alpha                 float [0., 1.]
zorder                number
drawstyle             matplotlib drawstyle: default, steps, etc
===================== =====================

Please see the matplotlib_ documentation for sensible values of the
different types.

.. _matplotlib: http://matplotlib.org/api/lines_api.html

Example
^^^^^^^
An example assigning the 'index' column as x values and the 'signal' column as
y values to a line with id 'line-1', as well as drawing it in red with a
circular marker:

    ==================== ==================
    Parameters           Values
    ==================== ==================
    line.line-1.xdata    ``table.col('index').data``
    line.line-1.ydata    ``table.col('signal').data``
    line.line-1.color    red
    line.line-1.marker   o
    ==================== ==================

**Axes**

Axes are defined similarly to lines. All axes are overlaid on top of each
other. Every axes also has a unique identifier *{id}* (without '.'). The
parameter name is constructed as *axes.{id}.{property}* on the local level
or *axes.{property}* for global properties, valid for all defined axes.

===================== =====================
Property              Type
===================== =====================
xaxis_position        bottom, top
yaxis_position        left, right
title                 unicode
xlabel                unicode
ylabel                unicode
xlim                  str of two comma separated numbers
ylim                  str of two comma separated numbers
xscale                linear, log
yscale                linear, log
aspect                auto, equal, float
grid                  GRID (see below)
legend                LEGEND (see below)
===================== =====================

**Grid**

Every axes can also have a grid with the following optional
properties:

===================== =====================
Property              Type
===================== =====================
show                  bool
color                 mpl color (see below)
linestyle             matplotlib line style: -, --, .-, etc
linewidth             float
which                 major, minor, both
axis                  both, x, y
===================== =====================

**Legend**

Every axes can also have a legend defined with the following
optional properties:

===================== =====================
Property              Type
===================== =====================
show                  bool
loc                   mpl legend location (e.g. best, upper left)
ncol                  int
fontsize              e.g. x-small, medium, x-large, etc
markerfirst           bool
frameon               bool
title                 unicode
===================== =====================


Example
^^^^^^^

The example defines two axes, one (id=xy) with the y axis on the left and the
other (id=foo) with the y axis on the right while sharing the bottom x axis.
Since the xaxis_position is shared between the two axes, it is defined on the
global level. For *xy*, a legend will be shown in the upper left corner, while
the *foo* axes will have a green grid.

    ======================= ===================
    Parameters              Values
    ======================= ===================
    axes.xaxis_position     bottom
    axes.xy.yaxis_position  left
    axes.xy.xlabel          The xy xlabel
    axes.xy.ylabel          The xy ylabel
    axes.xy.legend.show     True
    axes.xy.legend.loc      upper left
    axes.foo.yaxis          y2
    axes.foo.ylabel         The y2 ylabel
    axes.foo.grid.show      True
    axes.foo.grid.color     green
    ======================= ===================

**MPL colors**

All properties with *mpl colors* values expect a string with
either a hex color (with or without extra alpha channel), 3 or 4
comma separated integers for the RGBA values (range [0, 255]),
3 or 4 comma separated floats for the RGBA values (range [0., 1.])
or a matplotlib color_ name (e.g. r, red, blue, etc.).

.. _color: http://matplotlib.org/examples/color/named_colors.html
"""
QtCore = qt_compat.QtCore
QtGui = qt_compat.QtGui
qt_compat.backend.use_matplotlib_qt()


class SuperNodeFigureWithTable(synode.Node):
    author = 'Benedikt Ziegler <benedikt.ziegler@combine.se>'
    copyright = '(c) 2016 Combine Control Systems AB'
    version = '0.1'
    icon = 'figure.svg'
    tags = Tags(Tag.Visual.Figure)

    parameters = synode.parameters()
    parameters.set_list(
        'parameters', label='Parameters:',
        description='The column containing the parameter names.',
        editor=synode.Util.combo_editor(edit=True, filter=True))
    parameters.set_list(
        'values', label='Values:',
        description='The column containing the parameter values.',
        editor=synode.Util.combo_editor(edit=True, filter=True))

    def verify_parameters(self, node_context):
        parameters = node_context.parameters
        param_list = [] != parameters['parameters'].list
        value_list = [] != parameters['values'].list
        return param_list and value_list

    def adjust_parameters(self, node_context):
        config_input = node_context.input['config']
        adjust(node_context.parameters['parameters'], config_input)
        adjust(node_context.parameters['values'], config_input)

    def execute(self, node_context):
        config_table = node_context.input['config']

        parameters = node_context.parameters
        param_col = parameters['parameters'].selected
        value_col = parameters['values'].selected

        if param_col is None or value_col is None:
            raise SyConfigurationError(
                "No columns were selected or the columns you have selected "
                "are not present in the input please make sure to use data "
                "that contains the selected columns before executing this "
                "node.")

        param_names = config_table.get_column_to_array(param_col)
        param_values = config_table.get_column_to_array(value_col)
        configuration = list(zip(param_names, param_values))

        figure_param = util.parse_configuration(configuration)

        self._create_figure(node_context, figure_param)

    def _create_figure(self, node_context, figure_param):
        raise NotImplementedError()


class FigureFromTableWithTable(SuperNodeFigureWithTable):
    __doc__ = join_doc(
        """
        Create a Figure from a data Table (upper port) using another Table for
        configuration (lower port).
        """,
        CONF_TABLE_DOCSTRING)

    name = 'Figure from Table with Table'
    description = ('Create a Figure from a Table using a '
                   'configuration Table')
    nodeid = 'org.sysess.sympathy.visualize.figurefromtablewithtable'

    inputs = Ports([Port.Table('Input data', name='input'),
                    Port.Table('Configuration', name='config')])
    outputs = Ports([Port.Figure('Output figure', name='figure')])

    def _create_figure(self, node_context, figure_param):
        data_table = node_context.input['input']
        if not data_table.column_names():
            figure_param = util.parse_configuration([])
        figure = node_context.output['figure']

        figure_creator = util.CreateFigure(data_table, figure, figure_param)
        figure_creator.create_figure()


class FiguresFromTablesWithTable(SuperNodeFigureWithTable):
    __doc__ = join_doc(
        """
        Create Figures from a list of data Tables (upper port) using another
        Table for configuration (lower port).
        """,
        CONF_TABLE_DOCSTRING)

    name = 'Figures from Tables with Table'
    description = ('Create Figures from List of Tables using a '
                   'configuration Table')
    nodeid = 'org.sysess.sympathy.visualize.figuresfromtableswithtable'

    inputs = Ports([Port.Tables('Input data', name='input'),
                    Port.Table('Configuration', name='config')])
    outputs = Ports([Port.Figures('Output figure', name='figure')])

    def _create_figure(self, node_context, figure_param):
        data_tables = node_context.input['input']
        figures = node_context.output['figure']

        for i, data_table in enumerate(data_tables):
            figure = api.figure.File()
            figure_creator = util.CreateFigure(
                data_table, figure, figure_param)
            figure_creator.create_figure()

            figures.append(figure)

            self.set_progress(100 * (i + 1) / len(data_tables))


class FigureCompressor(synode.Node):
    """
    Compress a list of Figures into one Figure.

    :Ref. nodes: :ref:`Figure`
    """

    author = 'Benedikt Ziegler <benedikt.ziegler@combine.se>'
    copyright = '(c) 2016 Combine Control Systems AB'
    version = '0.3'
    icon = 'figurecompressor.svg'
    name = 'Figure Compressor'
    description = 'Compress a list of Figures to a single Figure'
    nodeid = 'org.sysess.sympathy.visualize.figurecompressorgui'
    tags = Tags(Tag.Visual.Figure)

    parameters = synode.parameters()
    parameters.set_list(
        'parent_figure', label='Parent figure:',
        description='Specify the figure from which axes parameters '
                    'and legend position are copied.',
        editor=synode.Util.combo_editor())
    parameters.set_boolean(
        'join_legends', value=True, label='Join legends',
        description='Set if legends from different axes should be '
                    'joined into one legend.')
    parameters.set_list(
        'legend_location', value=[0], label='Legend position:',
        plist=sorted(mpl_utils.LEGEND_LOC.keys()),
        description='Defines the position of the joined legend.',
        editor=synode.Util.combo_editor())
    parameters.set_boolean(
        'join_colorbars', value=False, label='Make first colorbar global',
        description='If checked, the colorbar from the first figure becomes '
                    'a global colorbar in the output figure.')
    parameters.set_boolean(
        'auto_recolor', value=False, label='Auto recolor',
        description='Automatically recolor all artists to avoid using a color '
                    'multiple times, if possible.')
    parameters.set_boolean(
        'auto_rescale', value=True, label='Auto rescale axes',
        description='Automatically rescale all axes to fit the visible data.')

    controllers = (
        synode.controller(
            when=synode.field('join_legends', 'checked'),
            action=synode.field('legend_location', 'enabled')))

    inputs = Ports([Port.Figures('List of Figures', name='input')])
    outputs = Ports([Port.Figure(
        'A Figure with the configured axes, lines, labels, etc',
        name='figure')])

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['parent_figure'],
               node_context.input['input'],
               lists='index')

    def execute(self, node_context):
        input_figures = node_context.input['input']
        output_figure = node_context.output['figure']
        parameters = node_context.parameters

        try:
            parent_figure_number = parameters['parent_figure'].value[0]
        except IndexError:
            parent_figure_number = 0

        input_axes = [figure.get_mpl_figure().axes for figure in input_figures]
        default_output_axes = output_figure.first_subplot().get_mpl_axes()

        axes_colorbars = util.compress_axes(
            input_axes, default_output_axes,
            parameters['join_legends'].value,
            parameters['legend_location'].selected,
            int(parent_figure_number),
            auto_recolor=parameters['auto_recolor'].value,
            auto_rescale=parameters['auto_rescale'].value,
            add_colorbars=not parameters['join_colorbars'].value)

        if parameters['join_colorbars'].value:
            util.add_global_colorbar(axes_colorbars, output_figure)


class SubplotFigures(synode.Node):
    """
    Layout the Figures in a list of Figures into subplots.

    The number of rows and columns is automatically adjusted to an approximate
    square. Empty axes in a non-empty row will be not shown.

    :Ref. nodes: :ref:`Figure`
    """

    author = 'Benedikt Ziegler <benedikt.ziegler@combine.se>'
    copyright = '(c) 2016 Combine Control Systems AB'
    version = '0.2'
    icon = 'figuresubplots.svg'
    name = 'Layout Figures in Subplots'
    description = 'Layout a list of Figures in a Subplot'
    nodeid = 'org.sysess.sympathy.visualize.figuresubplot'
    tags = Tags(Tag.Visual.Figure)

    inputs = Ports([Port.Figures('List of Figures', name='input')])
    outputs = Ports([Port.Figure(
        'A Figure with several subplot axes', name='figure')])

    parameters = synode.parameters()
    parameters.set_integer(
        'rows', value=0, label='Number of rows (0 = best):',
        description='Specify the number of rows. 0 optimizes to fit all '
                    'figures. If rows and columns are 0, the axes layout '
                    'will be approximately square.',
        editor=synode.Util.bounded_spinbox_editor(0, 100, 1))
    parameters.set_integer(
        'columns', value=0, label='Number of columns (0 = best):',
        description='Specify the number of columns. 0 optimizes to fit all '
                    'figures. If rows and columns are 0, the axes layout '
                    'will be approximately square.',
        editor=synode.Util.bounded_spinbox_editor(0, 100, 1))
    parameters.set_boolean(
        'recolor', value=True, label='Auto recolor',
        description='Specify if artists should be assigned new colors '
                    'automatically to prevent duplicate colors.')
    parameters.set_boolean(
        'remove_internal_ticks', value=False, label='Remove internal ticks',
        description='If checked, remove ticklabels from any axis between two '
                    'subplots.')
    parameters.set_boolean(
        'join_colorbars', value=False, label='Make first colorbar global',
        description='If checked, the colorbar from the first subplot is '
                    'treated as a global colorbar valid for all subplots.')
    parameters.set_boolean(
        'join_legends', value=False, label='Make first legend global',
        description='If checked, the legend(s) in the first subplot are '
                    'treated as global legends valid for all subplots.')

    def execute(self, node_context):
        input_figures = node_context.input['input']
        output_figure = node_context.output['figure']
        parameters = node_context.parameters
        rows = parameters['rows'].value
        cols = parameters['columns'].value
        auto_recolor = parameters['recolor'].value
        global_colorbar = parameters['join_colorbars'].value
        global_legend = parameters['join_legends'].value
        remove_internal_ticks = parameters['remove_internal_ticks'].value

        # calculate the number of rows and columns if any is =0
        nb_input_figures = len(input_figures)
        if rows == 0 and cols == 0:
            rows = int(np.ceil(np.sqrt(nb_input_figures)))
            cols = int(np.ceil(np.sqrt(nb_input_figures)))
            if rows * cols - cols >= nb_input_figures > 0:
                rows -= 1
        elif rows == 0 and cols > 0:
            rows = int(np.ceil(nb_input_figures / float(cols)))
        elif rows > 0 and cols == 0:
            cols = int(np.ceil(nb_input_figures / float(rows)))

        subplots = np.array(output_figure.subplots(rows, cols)).ravel()

        figure_colorbars = []

        for i, (subplot, input_figure) in enumerate(
                six.moves.zip(subplots, input_figures)):
            default_axes = subplot.get_mpl_axes()
            input_axes = [axes.get_mpl_axes() for axes in input_figure.axes]

            if remove_internal_ticks:
                subplot_mpl = subplot.get_mpl_axes()
                remove_ticklabels = (
                    not subplot_mpl.is_first_row(),
                    not subplot_mpl.is_last_col(),
                    not subplot_mpl.is_last_row(),
                    not subplot_mpl.is_first_col())
            else:
                remove_ticklabels = None

            axes_colorbars = util.compress_axes(
                [input_axes], default_axes,
                legends_join=False,
                legend_location='best',
                copy_properties_from=0,
                auto_recolor=auto_recolor,
                auto_rescale=False,
                add_colorbars=not global_colorbar,
                add_legends=(i == 0 or not global_legend),
                remove_ticklabels=remove_ticklabels)

            if axes_colorbars:
                figure_colorbars.append(axes_colorbars)

        if global_colorbar and len(figure_colorbars):
            util.add_global_colorbar(
                figure_colorbars[0], output_figure)

        # don't show empty axes
        if len(subplots) > len(input_figures):
            for ax_to_blank in subplots[len(input_figures):]:
                ax_to_blank.set_axis(False)


class FigureFromAnyWithTreeView(synode.Node):
    __doc__ = join_doc(
        """
        Create a Figure from some data using a GUI.
        """,
        TREEVIEW_DOCSTRING)

    author = 'Benedikt Ziegler <benedikt.ziegler@combine.se'
    copyright = '(c) 2016 Combine Control Systems AB'
    version = '0.2'
    icon = 'figure.svg'
    name = 'Figure'
    description = 'Create a single Figure using a GUI.'
    nodeid = 'org.sysess.sympathy.visualize.figuretabletreegui'
    tags = Tags(Tag.Visual.Figure)

    parameters = synode.parameters()
    parameters.set_string(
        'parameters', value='[]',
        label='GUI', description='Configuration window')

    inputs = Ports([Port.Custom('<a>', 'Input', name='input')])
    outputs = Ports([Port.Figure('Output figure', name='figure'),
                     Port.Custom('table', 'Configuration', name='config',
                                 n=(0, 1, 1))])

    def update_parameters(self, old_params):
        # Old nodes have their parameters stored as a list, but nowadays we
        # json-encode that list into a string instead.
        if old_params['parameters'].type == 'list':
            parameters_list = old_params['parameters'].list
            del old_params['parameters']
            old_params.set_string(
                'parameters', value=json.dumps(parameters_list))

    def exec_parameter_view(self, node_context):
        input_data = node_context.input['input']
        if not input_data.is_valid():
            input_data = api.table.File()
        return gui.FigureFromTableWidget(input_data, node_context.parameters)

    def execute(self, node_context):
        data_table = node_context.input['input']
        figure = node_context.output['figure']

        config_table = node_context.output.group('config')
        if len(config_table) > 0:
            config_table = config_table[0]
        else:
            config_table = None

        fig_parameters = json.loads(
            node_context.parameters['parameters'].value)
        parsed_param = util.parse_configuration(fig_parameters)

        figure_creator = util.CreateFigure(data_table, figure, parsed_param)
        figure_creator.create_figure()

        fig_parameters = np.atleast_2d(np.array(fig_parameters))
        if len(fig_parameters) and fig_parameters.shape >= (1, 2):
            parameters = fig_parameters[:, 0]
            values = fig_parameters[:, 1]
        else:
            parameters = np.array([])
            values = np.array([])

        if config_table is not None:
            config_table.set_column_from_array('Parameters', parameters)
            config_table.set_column_from_array('Values', values)


class FiguresFromAnyListWithTreeView(FigureFromAnyWithTreeView):
    __doc__ = join_doc(
        """
        Create a List of Figures from a List of data using a GUI.
        """,
        TREEVIEW_DOCSTRING)

    version = '0.2'
    name = 'Figures'
    description = 'Create a list of Figures from a list of data using a GUI.'
    nodeid = 'org.sysess.sympathy.visualize.figurestablestreegui'
    tags = Tags(Tag.Visual.Figure)

    inputs = Ports([Port.Custom('[<a>]', 'Inputs', name='inputs')])
    outputs = Ports([Port.Figures('Output figure', name='figures'),
                     Port.Custom('table', 'Configuration', name='config',
                                 n=(0, 1, 1))])

    def exec_parameter_view(self, node_context):
        input_data = node_context.input['inputs']
        if not input_data.is_valid() or not len(input_data):
            first_input = api.table.File()
        else:
            first_input = input_data[0]
        return gui.FigureFromTableWidget(first_input, node_context.parameters)

    def execute(self, node_context):
        data_tables = node_context.input['inputs']
        figures = node_context.output['figures']

        config_table = node_context.output.group('config')
        if len(config_table) > 0:
            config_table = config_table[0]
        else:
            config_table = None
        fig_parameters = json.loads(
            node_context.parameters['parameters'].value)
        parsed_param = util.parse_configuration(fig_parameters)

        number_of_tables = len(data_tables) + 1  # +1 for writing config table

        i = 0
        for i, data_table in enumerate(data_tables):
            figure = api.figure.File()
            figure_creator = util.CreateFigure(data_table, figure,
                                               parsed_param.copy())
            figure_creator.create_figure()
            figures.append(figure)
            self.set_progress(100 * (i + 1) / number_of_tables)

        fig_parameters = np.atleast_2d(np.array(fig_parameters))
        if len(fig_parameters) and fig_parameters.shape >= (1, 2):
            parameters = fig_parameters[:, 0]
            values = fig_parameters[:, 1]
        else:
            parameters = np.array([])
            values = np.array([])
        if config_table is not None:
            config_table.set_column_from_array('Parameters', parameters)
            config_table.set_column_from_array('Values', values)
        self.set_progress(100 * (i + 1) / number_of_tables)
