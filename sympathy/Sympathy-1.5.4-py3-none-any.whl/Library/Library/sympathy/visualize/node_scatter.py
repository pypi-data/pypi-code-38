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
This node is for visualising data in 3D.

In the configuration Table columns are selected along the axes in the plots.
There exist differences between the nodes how to do this, but the basic
principle is the same. For the actual plots is possible to change both
line/marker style and plot style in the plot. Below, the available plot styles
are listed. A plot legend is, by default, shown in the plot, but can be hidden
by a simple push of a button. The navigation toolbar under the plot let the
user zoom and pan the plot window.

Available plot types (3D):
    - scatter
    - surf
    - wireframe
    - plot
    - contour
    - heatmap

The advanced plot controller allows the user to draw two lines parallel to
the Y-axis. These can be moved along the X-axis while information about the
intersection points between these lines and the plotted data points is shown
in a table. If a line is drawn in between two points in the plotted data, the
line will always move to the closest point.
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import os
import numpy as np
import sys
import six
import warnings

from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api.exceptions import NoDataError
from sympathy.api import qt as qt_compat
from sylib.util import mock_wrap

from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas)
from matplotlib.backends.backend_agg import (
    FigureCanvasAgg as FigureCanvasNonInteractive)
from matplotlib.backends.backend_qt4agg import (
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

# For 3D plot
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

QtCore = qt_compat.QtCore
QtGui = qt_compat.import_module('QtGui')
qt_compat.backend.use_matplotlib_qt()


def reinit_3d(node_context):
    """Reinitialize parameter_root for 3d plot. Ex. when file datasource has
    changed.
    """
    parameter_root = synode.parameters(node_context.parameters)
    parameter_root['tb_names'].list = []
    parameter_root['tb_names'].value = []
    parameter_root['x_axis'].list = []
    parameter_root['x_axis'].value = []
    parameter_root['x_axis'].value_names = []
    parameter_root['y_axis'].list = []
    parameter_root['y_axis'].value = []
    parameter_root['y_axis'].value_names = []
    parameter_root['z_axis'].list = []
    parameter_root['z_axis'].value = []
    parameter_root['z_axis'].value_names = []
    parameter_root['line_style'].value = [0]
    parameter_root['plot_func'].value = [0]
    parameter_root['filename_extension'].list = []
    parameter_root['filename_extension'].value = []


def create_filenames_from_parameters(parameter_root, index=None,
                                     table_name=None):
    export_directory = parameter_root['directory'].value or '.'
    filename = parameter_root['filename'].value
    extension = parameter_root['filename_extension'].selected
    if table_name is not None:
        complete_filename = '{}{}'.format(table_name, extension)
    else:
        if index is not None:
            complete_filename = '{}_{}{}'.format(filename, index, extension)
        else:
            complete_filename = '{}{}'.format(filename, extension)
    return os.path.join(export_directory, complete_filename)


class Super3dNode(synode.Node):
    name = 'Scatter 3D Table'
    description = 'A three dimensional plot'
    nodeid = 'org.sysess.sympathy.visualize.scatter3dnode'
    author = 'Helena Olen <helena.olen@combine.se>'
    copyright = '(C) 2013 Combine Control Systems AB'
    version = '1.0'
    icon = 'scatter3d.svg'
    tags = Tags(Tag.Visual.Plot)

    parameters = synode.parameters()
    parameters.set_list(
        'tb_names', label='Time basis',
        description='Combo of all timebasis',
        editor=synode.Util.combo_editor())
    parameters.set_list(
        'x_axis', label='X axis',
        description='X axis selection for plot',
        editor=synode.Util.combo_editor())
    parameters.set_list(
        'y_axis', label='Y axis',
        description='Y axis selection for plot',
        editor=synode.Util.combo_editor())
    parameters.set_list(
        'z_axis', label='Z axis',
        description='Z axis selection for plot',
        editor=synode.Util.combo_editor())
    parameters.set_list(
        'line_style', label='Line style',
        plist=['o', '^', '*'],
        description='Selectable line styles',
        editor=synode.Util.combo_editor())
    parameters.set_list(
        'plot_func', label='Plot type',
        plist=['scatter', 'surf', 'wireframe', 'plot', 'contour', 'heatmap'],
        description='Selectable plot types',
        editor=synode.Util.combo_editor())
    parameters.set_list(
        'filename_extension', label='File extension',
        description='Filename extension',
        editor=synode.Util.combo_editor())

    inputs = Ports(
        [Port.Table('Input Table', name='port1', requiresdata=True)])
    outputs = Ports([Port.Datasource('Output file', name='port2')])

    def update_parameters(self, params):
        # Remove old parameters.
        for param in ['azim', 'elev']:
            if param in params:
                del params[param]

    def verify_parameters(self, node_context):
        parameters = node_context.parameters
        try:
            if parameters['filename'].value == '':
                return False
        except Exception:
            return False
        return True

    def exec_parameter_view(self, node_context):
        """Create the parameter view"""
        tabledata = None
        try:
            with node_context.input['port1'] as tablefile:
                tabledata = tablefile.to_recarray()
        except NoDataError:
            # When no input is connected
            pass
        try:
            return Scatter3dWidget(node_context, [tabledata])
        except Exception:
            reinit_3d(node_context)
            return Scatter3dWidget(node_context, [tabledata])

    def execute(self, node_context):
        """Execute"""
        parameter_root = synode.parameters(node_context.parameters)
        fq_filename = create_filenames_from_parameters(parameter_root)
        fig = Figure()
        FigureCanvasNonInteractive(fig)
        axes = Axes3D(fig)
        with node_context.input['port1'] as tablefile:
            tabledata = tablefile.to_recarray()

        plot_widget = Plot3d(
            [tabledata], parameter_root, fig, axes)
        plot_widget.update_figure()
        fig.savefig(fq_filename)
        node_context.output['port2'].encode_path(fq_filename)


class FigureCanvasCustom(FigureCanvas):
    canvasResized = qt_compat.Signal()

    def resizeEvent(self, event):
        FigureCanvas.resizeEvent(self, event)
        self.canvasResized.emit()


@mock_wrap
class Scatter3dWidget(QtGui.QWidget):
    """Widget to plot a three dimensional scatter graph"""

    def __init__(self, node_context, tables, names=None, names_short=None,
                 units=None):
        """
        Args: tables (list): list of numpy recarrays
              names (list): list of names of the tables in tables
              tb_names (list): list of short time basis names,
                               corresponding to lo0ng names in names
              units: {table_name: {column_name1: column_unit1, ...}, ...}
        """
        super(Scatter3dWidget, self).__init__()
        self._tables = tables

        self._node_context = node_context
        self._parameter_root = synode.parameters(node_context.parameters)
        self._x_axis_combobox = None
        self._y_axis = None
        self._line_style_combobox = None
        self._plot_combobox = None
        self._file_extension_combo = None
        self._outputs_hlayout = None
        self._projection = None
        self._background = None
        self._figure = None
        self._axes = None
        self._canvas = None
        self._toolbar = None

        self._plot = None

        self._names_short = names_short
        if names is None:
            self._names = []
        else:
            self._names = names
        self._units = units
        self._z_axis_combobox = None
        self._tb_combobox = None
        self._projection = '3d'
        self._init_gui()

    def _init_gui(self):
        """Init GUI"""
        # Create plot window.
        self._create_figure_gui()
        self._pre_init_gui_from_parameters()
        vlayout = QtGui.QVBoxLayout()

        axes_hlayout = QtGui.QHBoxLayout()
        axes_hlayout.setSpacing(20)
        self._tb_combobox = self._parameter_root['tb_names'].gui()
        self._x_axis_combobox = self._parameter_root['x_axis'].gui()
        self._y_axis_combobox = self._parameter_root['y_axis'].gui()
        self._z_axis_combobox = self._parameter_root['z_axis'].gui()

        self._line_style_combobox = self._parameter_root['line_style'].gui()

        self._plot_combobox = self._parameter_root['plot_func'].gui()

        axes_hlayout.addWidget(self._tb_combobox)
        axes_hlayout.addWidget(self._x_axis_combobox)
        axes_hlayout.addWidget(self._y_axis_combobox)
        axes_hlayout.addWidget(self._z_axis_combobox)
        axes_hlayout.addWidget(self._line_style_combobox)
        axes_hlayout.addWidget(self._plot_combobox)
        axes_hlayout.insertStretch(-1)

        # Create outputlayout
        self._create_output_layout()

        vlayout.addItem(axes_hlayout)
        vlayout.addWidget(self._canvas)
        vlayout.addWidget(self._toolbar)
        vlayout.addLayout(self._outputs_hlayout)

        self.setLayout(vlayout)

        self._init_gui_from_parameters()

        self._x_axis_combobox.editor().currentIndexChanged[int].connect(
            self._x_axis_change)
        self._tb_combobox.editor().currentIndexChanged[int].connect(
            self._tb_names_change)
        self._y_axis_combobox.editor().currentIndexChanged[int].connect(
            self._y_axis_change)
        self._z_axis_combobox.editor().currentIndexChanged[int].connect(
            self._z_axis_change)
        self._line_style_combobox.editor().currentIndexChanged[int].connect(
            self._line_style_changed)
        self._plot_combobox.editor().currentIndexChanged.connect(
            self._plot_func_changed)
        self._figure.canvas.mpl_connect(
            'button_release_event', self._update_view)

    def _pre_init_gui_from_parameters(self):
        column_names = []
        if (self._tables is not None and len(self._tables) and
                self._tables[0] is not None):
            column_names = list(self._tables[0].dtype.names)

        if self._parameter_root['tb_names'].list and self._names:
            self._parameter_root['tb_names'].list = self._names

        x_list = self._parameter_root['x_axis'].list
        if (not x_list or len(x_list) == 0):
            self._parameter_root['x_axis'].list = column_names
            self._parameter_root['y_axis'].list = column_names
            self._parameter_root['z_axis'].list = column_names

        if not self._parameter_root['filename_extension'].list:
            supported_files_dict = (self._figure.canvas.
                                    get_supported_filetypes())
            supported_files = supported_files_dict.keys()
            supported_files = (
                ['.' + supported_file for supported_file in supported_files if
                    supported_file in ['svg', 'pdf', 'eps', 'png']])
            self._parameter_root['filename_extension'].list = supported_files

    def _init_gui_from_parameters(self):
        """Init GUI from parameters"""
        # variables for figure view.
        if len(self._names) == 0:
            self._tb_combobox.editor().setEnabled(False)

        self._plot = Plot3d(
            self._tables, self._parameter_root, self._figure, self._axes,
            self._names_short, self._units)
        self._plot_func_changed()
        self._update_figure()

    def _create_figure_gui(self):
        if sys.platform == 'darwin':
            backgroundcolor = '#ededed'
        else:
            backgroundcolor = self.palette().color(
                QtGui.QPalette.Window).name()
        self._figure = Figure(facecolor=backgroundcolor)
        self._create_subplot()
        self._create_canvas_tool()

    def _create_subplot(self):
        """To be implemented by subclasses"""
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', UserWarning)
                self._axes = self._figure.add_subplot(
                    111, projection=self._projection)
        except ValueError:
            pass

    def _create_canvas_tool(self):
        """Create canvas and navigation toolbar."""
        self._canvas = FigureCanvasCustom(self._figure)
        policy = QtGui.QSizePolicy()
        policy.setHorizontalStretch(1)
        policy.setVerticalStretch(1)
        policy.setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
        policy.setVerticalPolicy(QtGui.QSizePolicy.Expanding)
        self._canvas.setSizePolicy(policy)
        self._toolbar = NavigationToolbarCustom(self._canvas, self)

    def _create_output_layout(self):
        """Create output layout with directory edit, file editor and file
        extension combo.
        """
        try:
            self._parameter_root['directory']
        except KeyError:
            self._parameter_root.set_string(
                "directory", label="Output directory",
                description="Select the directory where to export the files.",
                editor=synode.Util.directory_editor().value())
        try:
            self._parameter_root['filename']
        except KeyError:
            self._parameter_root.set_string(
                "filename", label="Filename",
                description="Filename without extension.")

        self._outputs_hlayout = QtGui.QHBoxLayout()
        self._outputs_hlayout.addWidget(
            self._parameter_root['directory'].gui())
        self._outputs_hlayout.addWidget(self._parameter_root['filename'].gui())
        self._file_extension_combo = (self._parameter_root[
            'filename_extension'].gui())
        self._outputs_hlayout.addWidget(self._file_extension_combo)

    def _tb_names_change(self, index):
        """Update axis combobox items when timebasis is changed"""
        column_names = list(self._tables[index].dtype.names)
        x_editor = self._x_axis_combobox.editor()
        x_editor.blockSignals(True)
        x_editor.clear()
        x_editor.addItems(column_names)
        x_editor.blockSignals(False)
        y_editor = self._y_axis_combobox.editor()
        y_editor.blockSignals(True)
        y_editor.clear()
        y_editor.addItems(column_names)
        y_editor.blockSignals(False)
        z_editor = self._z_axis_combobox.editor()
        z_editor.blockSignals(True)
        z_editor.clear()
        z_editor.addItems(column_names)
        z_editor.blockSignals(False)
        self._update_figure()

    def _x_axis_change(self, index):
        """Update figure with new x_axis value"""
        self._update_figure()

    def _y_axis_change(self, index):
        """Update figure with new y_axis value"""
        self._update_figure()

    def _z_axis_change(self, index):
        """Update figure with new z_axis value"""
        self._update_figure()

    def _line_style_changed(self, index):
        """Update figure with new line_style"""
        self._update_figure()

    def _enable_line(self, state):
        """Enable or disable line style combo"""
        self._line_style_combobox.editor().setEnabled(state)

    def _plot_func_changed(self):
        """Update GUI and figure when plot function changed"""
        plot_func = self._parameter_root['plot_func'].selected
        if plot_func == 'plot':
            self._enable_line(False)
        elif plot_func == 'scatter':
            self._enable_line(True)
        else:
            self._enable_line(False)
        self._update_figure()

    def _update_figure(self):
        """Update figure"""
        self._plot.update_figure()
        try:
            self._canvas.draw()
        except ValueError:
            self._axes.clear()
            self._canvas.draw()

    def _update_view(self, event):
        """Update view when figure rotated"""
        self._plot.update_view()


class Plot3d(object):
    def __init__(self, tables, parameter_root, fig, axes,
                 names_short=None, units=None, cb=None):
        self._fig = fig
        self._axes = axes
        self._parameter_root = parameter_root
        self._tables = tables
        self._units = units
        self._tb_names_short = names_short
        self._cb = cb
        self._nbr_points = 100
        self._2d_axes = False
        self._rotation = None

    def update_figure(self):
        """Update figure"""
        x_column_name = ''
        x_data = []
        y_data = []
        z_data = []

        plot_func = self._parameter_root['plot_func'].selected
        try:
            table_index = self._parameter_root['tb_names'].value[0]
        except IndexError:
            table_index = 0

        if len(self._parameter_root['x_axis'].list):
            x_column_name = self._parameter_root['x_axis'].selected

        y_column_name = self._parameter_root['y_axis'].selected
        z_column_name = self._parameter_root['z_axis'].selected

        if (self._tables is not None and len(self._tables) and
                self._tables[table_index] is not None):
            if x_column_name and y_column_name and z_column_name:
                x_data = self._tables[table_index][x_column_name]
                y_data = self._tables[table_index][y_column_name]
                z_data = self._tables[table_index][z_column_name]

        if self._axes is not None:
            self._axes.clear()
            if not self._2d_axes:
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore', UserWarning)
                    self._axes.mouse_init()
        if len(self._parameter_root['tb_names'].list) > 0:
            tb_name = self._parameter_root['tb_names'].selected

        # Get units for axis
        if (self._units is not None and
                len(self._parameter_root['tb_names'].list) > 0):
            x_units = self._get_units(tb_name, x_column_name, table_index)
            y_units = self._get_units(tb_name, y_column_name, table_index)
            z_units = self._get_units(tb_name, z_column_name, table_index)

        else:
            x_units = ''
            y_units = ''
            z_units = ''

        # Only plot real numbers
        if (np.all(np.isreal(x_data)) and np.all(np.isreal(y_data)) and
                np.all(np.isreal(z_data))):
            if plot_func == 'surf':
                self._axes_2d_to_3d()
                if len(x_data) >= 1 and len(y_data) >= 1 and len(z_data) >= 1:
                    self._surf_plot(x_data, y_data, z_data)
            elif plot_func == 'contour':
                self._axes_2d_to_3d()
                if len(x_data) >= 1 and len(y_data) >= 1 and len(z_data) >= 1:
                    self._contour_plot(x_data, y_data, z_data)
            elif plot_func == 'scatter':
                self._axes_2d_to_3d()
                self._check_cb()
                if self._axes is not None:
                    self._axes.scatter(
                        x_data, y_data, z_data,
                        marker=self._parameter_root['line_style'].selected)
                self._cb = None
            elif plot_func == 'plot':
                self._axes_2d_to_3d()
                self._check_cb()
                if self._axes is not None:
                    self._axes.plot(x_data, y_data, z_data)
                self._cb = None
            elif plot_func == 'wireframe':
                self._axes_2d_to_3d()
                self._wireframe_plot(x_data, y_data, z_data)
            elif plot_func == 'heatmap':
                self._heatmap_plot(
                    x_data, y_data, z_data, z_column_name, z_units)
            else:
                pass
        if self._axes is not None:
            self._axes.set_xlabel(self._get_label(x_column_name, x_units))
            self._axes.set_ylabel(self._get_label(y_column_name, y_units))
        if not self._2d_axes and self._axes is not None:
            self._axes.set_zlabel(self._get_label(z_column_name, z_units))

    def update_view(self):
        """Update figure rotation if 3d figure"""
        pass

    def _get_label(self, column_name, unit):
        """Get axis label"""
        if self._units is not None and unit != 'unknown' and unit != '':
            label = six.text_type(column_name) + ' [' + unit + ']'
        else:
            label = six.text_type(column_name)
        return label

    def _interpolate_data(self, data):
        """Linear interpolation of data when data more than predefined
        nbr of points.
        """
        len_data = len(data)
        if len_data > self._nbr_points:
            x_interp = range(0, len_data)
            new_x_points = np.linspace(0, len_data - 1, self._nbr_points)
            new_data = np.interp(new_x_points, x_interp, data)
            return new_data
        return data

    def _interpolate_all(self, x_data, y_data, z_data):
        """Interpolate x_data, y_data and z_data"""
        x_data_new = self._interpolate_data(x_data)
        y_data_new = self._interpolate_data(y_data)
        z_data_new = self._interpolate_data(z_data)
        return x_data_new, y_data_new, z_data_new

    def _surf_plot(self, x_data, y_data, z_data):
        """3d surface plot"""
        x_data_new, y_data_new, z_data_new = self._interpolate_all(
            x_data, y_data, z_data)
        X, Y, Z = self._get_xyz(
            x_data_new, y_data_new, z_data_new)
        self._check_cb()
        if self._axes is not None:
            surf = self._axes.plot_surface(
                X, Y, Z, cmap=cm.coolwarm, rstride=1, cstride=1,
                linewidth=0, antialiased=False)

        if len(x_data) > 1 and len(y_data) > 1 and len(z_data) > 1:
            self._cb = self._fig.colorbar(surf, format='%d')  # ?????
        else:
            self._cb = None

    def _contour_plot(self, x_data, y_data, z_data):
        """3d contour plot"""
        x_data_new, y_data_new, z_data_new = self._interpolate_all(
            x_data, y_data, z_data)
        X, Y, Z = self._get_xyz(
            x_data_new, y_data_new, z_data_new)
        if self._axes is not None:
            cset = self._axes.contour(X, Y, Z, cmap=cm.coolwarm)
            self._axes.clabel(cset, fontsize=9, inline=1)
        self._check_cb()
        self._cb = None

    def _wireframe_plot(self, x_data, y_data, z_data):
        """3d wireframe plot"""
        x_data_new, y_data_new, z_data_new = self._interpolate_all(
            x_data, y_data, z_data)
        X, Y, Z = self._get_xyz(
            x_data_new, y_data_new, z_data_new)
        if self._axes is not None:
            self._axes.plot_wireframe(
                X, Y, Z, rstride=1, cstride=1, alpha=0.4)
        self._check_cb()
        self._cb = None

    def _heatmap_plot(self, x_data, y_data, z_data, z_column_name, z_units):
        """2d heatmap plot with z_axis as colour"""
        x_data_new, y_data_new, z_data_new = self._interpolate_all(
            x_data, y_data, z_data)
        X, Y, Z = self._get_xyz(
            x_data_new, y_data_new, z_data_new)

        x = X.ravel()
        y = Y.ravel()
        z = Z.ravel()
        gridsize = 30

        self._check_cb()
        self._fig.delaxes(self._axes)
        self._axes = self._fig.add_subplot(111)
        self._2d_axes = True

        if (len(x_data) > 1 and len(y_data) > 1 and len(z_data) > 1 and
                self._axes is not None):
            heat = self._axes.hexbin(
                x, y, C=z, gridsize=gridsize, cmap=cm.jet, bins=None)
            self._axes.axis([x.min(), x.max(), y.min(), y.max()])
            self._cb = self._fig.colorbar(heat)
            z_label = self._get_label(z_column_name, z_units)
            self._cb.set_label(z_label)
        else:
            self._cb = None

    def _axes_2d_to_3d(self):
        """Create new 3d figure and delete old figure"""
        self._check_cb()
        if self._axes is not None:
            self._fig.delaxes(self._axes)
        self._axes = Axes3D(self._fig)
        self._2d_axes = False

    def _check_cb(self):
        """Check if colorbar exists, and then delete it"""
        if self._cb:
            try:
                self._fig.delaxes(self._fig.axes[1])
            except Exception:
                pass

    def _get_units(self, tb_name, column_name, table_index):
        """Get units of axis and handle deg to be displayed correctly in
        plot.
        """
        try:
            unit = self._units[tb_name][column_name]
        except Exception:
            try:
                if (column_name) == self._tb_names_short[table_index]:
                    unit = self._units[tb_name][(
                        self._parameter_root['tb_names'].list[
                            table_index])]
                else:
                    unit = ''
            except Exception:
                unit = ''
        # Handle deg in units
        if '\xb0' in unit:
            unit_temp = unit.split('\xb0')
            unit = r'$^\circ$'.join(unit_temp)
        return unit

    def _get_xyz(self, x_data, y_data, z_data):
        """Get matrices X,Y,Z from 1D arrays"""
        x, y = np.meshgrid(x_data, y_data)
        z = np.tile(z_data, (len(z_data), 1))
        return x, y, z


class NavigationToolbarCustom(NavigationToolbar):
    zoomChanged = qt_compat.Signal(float, float, float, float)
    zoomActive = qt_compat.Signal(bool)
    panActive = qt_compat.Signal(bool)
    panDragged = qt_compat.Signal(float, float, float, float)
    parameters_edited = qt_compat.Signal()
    home_clicked = qt_compat.Signal()
    _home = True

    def __init__(self, canvas, parent):
        NavigationToolbar.__init__(self, canvas, parent)
        self._forward = False
        self._back = False

    def draw(self):
        super(NavigationToolbarCustom, self).draw()
        if self._xypress is None or self._home:
            home_view = self._views.home()
            x_min, x_max = home_view[0][0:2]
            y_min, y_max = home_view[0][2:4]
        elif self._forward:
            self._views.back()
            forward_view = self._views.forward()
            x_min, x_max = forward_view[0][0:2]
            y_min, y_max = forward_view[0][2:4]
        elif self._back:
            self._views.forward()
            back_view = self._views.back()
            x_min, x_max = back_view[0][0:2]
            y_min, y_max = back_view[0][2:4]
        else:
            if self._active == 'PAN':
                a = self._xypress_save[0][0].figure.axes[0]
            elif self._active == 'ZOOM':
                _, _, a, _, _, _ = self._xypress[0]
            else:
                a = self.canvas.figure.get_axes()
            x_min, x_max = a.get_xlim()
            y_min, y_max = a.get_ylim()
        self.parameters_edited.emit()
        self.zoomChanged.emit(x_min, x_max, y_min, y_max)

    def pan(self, *args):
        super(NavigationToolbarCustom, self).pan()
        self.panActive.emit(self._active == 'PAN')

    def zoom(self, *args):
        super(NavigationToolbarCustom, self).zoom()
        self.zoomActive.emit(self._active == 'ZOOM')

    def home(self, *args):
        self._home = True
        super(NavigationToolbarCustom, self).home()
        self._home = False
        self.home_clicked.emit()
        self.parameters_edited.emit()

    def release_zoom(self, event):
        super(NavigationToolbarCustom, self).release_zoom(event)
        self._home = False
        self._xypress_save = None
        self.parameters_edited.emit()

    def forward(self, *args):
        self._forward = True
        super(NavigationToolbarCustom, self).forward(*args)
        self._forward = False

    def back(self, *args):
        self._back = True
        super(NavigationToolbarCustom, self).back(*args)
        self._back = False

    def release_pan(self, event):
        self._xypress_save = self._xypress
        super(NavigationToolbarCustom, self).release_pan(event)
        self._home = False
        self._xypress_save = None

    def drag_pan(self, event):
        a, ind = self._xypress[0]
        super(NavigationToolbarCustom, self).drag_pan(event)
        x_min, x_max = a.get_xlim()
        y_min, y_max = a.get_ylim()
        self.parameters_edited.emit()
        self.panDragged.emit(x_min, x_max, y_min, y_max)

    def edit_parameters(self):
        super(NavigationToolbarCustom, self).edit_parameters()
        self.parameters_edited.emit()
