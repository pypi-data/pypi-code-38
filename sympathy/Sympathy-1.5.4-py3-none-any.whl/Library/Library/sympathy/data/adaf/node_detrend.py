# Copyright (c) 2013 2017, Combine Control Systems AB
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
To identify and remove trends in data is an important tool in the work of
data analysis. For example, large background values can be reduced in order
to obtain a better view of variations in the data.

In the considered node, trends of polynomial nature are identified and
removed from the data arrays in the timeseries container of :ref:`ADAF`
objects. The method used to identify the trend is an ordinary least square
polynomial fit, where an upper limit with polynomial of 4th order is
introduced. The detrended result is achieved by subtracting the identified
polynomial from the considered timeseries.

For the node several timeseries belonging to a selected timebasis can be
selected for detrending. Keep in mind that the same order of the detrend
polynomials will be used even when several timeseries have been selected.

The selected timeseries arrays are overwritten by the detrended result in
the outgoing file.
"""
import numpy as np

from sympathy.api import qt as qt_compat
QtCore = qt_compat.QtCore  # noqa
QtGui = qt_compat.import_module('QtGui')  # noqa
qt_compat.backend.use_matplotlib_qt()  # noqa

from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas)
from matplotlib.backends.backend_qt4agg import (
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

from sympathy.api import node_helper
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags


def get_adaf_info(adaffile):
    """
    Get dict with whole timebasis names as keys and recarrays
    with timeseries and timebasis as values
    """
    tb_ts_dict = {}
    tb_dict = {}
    adaf_ts = adaffile.ts
    for ts_key in adaf_ts.keys():
        ts = adaf_ts[ts_key]
        tb_name = (str(ts.system_name()) + '/' +
                   str(ts.raster_name()) + '/')
        try:
            tb_dict[tb_name]
        except:
            tb_dict[tb_name] = (
                {'raster_name': ts.raster_name(),
                 'system_name': ts.system_name(), 'tb': ts.t,
                 'attr': dict(ts.basis().attr.items())})
        try:
            ts_info = tb_ts_dict[tb_name]
            ts_info[str(ts_key)] = {'ts': ts.y,
                                    'attr': dict(ts.signal().attr.items())}
        except:
            tb_ts_dict[tb_name] = (
                {str(ts_key): {'ts': ts.y,
                               'attr': dict(ts.signal().attr.items())}})
    return tb_ts_dict, tb_dict


def write_meta_result(in_adaffile, out_adaffile):
    """Copy meta and result from in file to out file."""
    out_adaffile.meta.hjoin(in_adaffile.meta)
    out_adaffile.res.hjoin(in_adaffile.res)


def write_timeseries(parameter_root, in_adaffile, out_adaffile,
                     tb_ts_dict, tb_dict):
    selected_tb = parameter_root['tb'].selected
    selected_ts = parameter_root['y_axis'].list
    tb_group = out_adaffile.sys
    system_dict = {}
    for tb in tb_ts_dict.keys():
        try:
            system = tb_group.create(str(tb_dict[tb]['system_name']))
            system_dict[tb_dict[tb]['system_name']] = system
        except:
            system = system_dict[tb_dict[tb]['system_name']]
        raster = system.create(str(tb_dict[tb]['raster_name']))
        raster.create_basis(tb_dict[tb]['tb'], tb_dict[tb]['attr'])
        if tb == selected_tb:
            for ts in tb_ts_dict[tb].keys():
                # Or add ts from trend, not overwrite exoisting ts??!?!?
                if ts not in selected_ts:
                    raster.create_signal(
                        ts, tb_ts_dict[tb][ts]['ts'],
                        tb_ts_dict[tb][ts]['attr'])
                else:
                    tb_data = tb_dict[tb]['tb']
                    ts_data = tb_ts_dict[tb][ts]['ts']
                    if (np.all(np.isreal(tb_data)) and
                            np.all(np.isreal(ts_data))):
                        ts_new, _ = detrend_data(
                            tb_data, ts_data,
                            parameter_root['detrend_function'].value[0])
                        raster.create_signal(
                            ts, ts_new, tb_ts_dict[tb][ts]['attr'])
                    else:
                        raster.create_signal(
                            ts, ts_data, tb_ts_dict[tb][ts]['attr'])
                    # TODO if signal can't be detrended. What to do?!
        else:
            for ts in tb_ts_dict[tb].keys():
                raster.create_signal(
                    ts, tb_ts_dict[tb][ts]['ts'], tb_ts_dict[tb][ts]['attr'])


def check_consistence(node_context, tb_ts_dict, tb_dict):
    """Check if items in widgest are constistent with input file."""
    parameters = synode.parameters(node_context.parameters)
    if tb_ts_dict is None or tb_dict is None or tb_ts_dict == {}:
        return False
    if (sorted(parameters['tb'].list) == sorted(tb_dict.keys()) and
            sorted(parameters['ts'].list) == sorted(
                tb_ts_dict[parameters['tb'].selected].keys())):
        return True
    else:
        return False


def reinit_detrend(node_context, tb_ts_dict, tb_dict):
    """Reinitialize node when infile has changed."""
    parameters = synode.parameters(node_context.parameters)
    parameters['tb'].list = []
    parameters['tb'].value = []
    parameters['tb'].value_names = []
    parameters['ts'].list = []
    parameters['ts'].value = []
    parameters['ts'].value_names = []
    parameters['detrend_function'].value = [0]
    parameters['x_axis'].list = []
    parameters['x_axis'].value = []
    parameters['y_axis'].list = []
    parameters['y_axis'].value = []


def check_and_reinit_node(node_context, tb_ts_dict, tb_dict):
    """
    Check if node_context consistent with info from input file and
    reinitialize if not.
    """
    if not check_consistence(node_context, tb_ts_dict, tb_dict):
        reinit_detrend(node_context, tb_ts_dict, tb_dict)


def detrend_data(tb, ts, detrend_function):
    """Detrend data."""
    trend = get_trend(tb, ts, detrend_function)
    ts_new = ts - trend
    return ts_new, trend


def get_trend(tb, ts, detrend_function):
    """Fit ploynomial to data points. detrend_function index for
    degree of ploynomial.
    """
    poly_coeff = np.polyfit(tb, ts, detrend_function)
    trend = np.polyval(poly_coeff, tb)
    return trend


def get_functions():
    functions = ['Constant', 'Linear', '2nd degree poly', '3rd degree poly',
                 '4th degree poly']
    return functions


def cooks_distance(tb, ts, detrend_function, trend=None):
    """Calculates cooks distance function."""
    if trend is None:
        trend = get_trend(tb, ts, detrend_function)
    n = len(ts)
    mse = 1.0 / n * np.sum((trend - ts) ** 2)
    d = np.zeros(n, 1)
    p = detrend_function + 1
    for ind in range(n):
        trend_ind = np.delete(trend, [ind])
        ts_new = np.delete(ts, [ind])
        tb_new = np.delete(tb, [ind])
        trend_new = get_trend(tb_new, ts_new, detrend_function)
        d[ind] = np.sum((trend_ind - trend_new) ** 2) / (p * mse)
    return d, trend


def simple_detrend(tb, ts, detrend_function, trend=None):
    if trend is None:
        trend = get_trend(tb, ts, detrend_function)
    ts_new = ts - trend
    return ts_new, trend


def sigma_detrend(tb, ts, detrend_function, trend=None):
    if trend is None:
        trend = get_trend(tb, ts, detrend_function)
    sigma = np.std(ts - trend)
    ts_new = (ts - trend) / sigma
    return ts_new, trend


class SuperNode(object):
    author = 'Helena Olen <helena.olen@gmail.com'
    copyright = '(C) 2013 Combine Control Systems AB'
    version = '1.0'
    tags = Tags(Tag.Analysis.SignalProcessing)
    icon = 'detrend.svg'

    parameters = synode.parameters()
    tb_editor = synode.Util.list_editor()
    tb_editor.set_attribute('filter', True)
    ts_editor = synode.Util.multilist_editor()
    parameters.set_list(
        'tb', label="Time basis column",
        description='Choose a raster to select timeseries columns from',
        value=[0], editor=tb_editor)
    parameters.set_list(
        'ts', label="Timeseries columns",
        description='Choose one or many timeseries columns to detrend',
        value=[0], editor=ts_editor)
    parameters.set_list(
        'detrend_function', plist=get_functions(), label='Detrend function',
        value=[0], description='Function used to detrend data',
        editor=synode.Util.combo_editor())
    parameters.set_list(
        'x_axis', label='X axis', description='X axis combobox',
        editor=synode.Util.combo_editor())
    parameters.set_list(
        'y_axis', label='Y axis', description='Y axis combobox',
        editor=synode.Util.combo_editor())


class DetrendADAF(SuperNode, synode.Node):
    """
    Detrend timeseries in an ADAF.

    :Ref. nodes: :ref:`Detrend ADAFs`
    """

    inputs = Ports([Port.ADAF('Input ADAF', name='port1')])
    outputs = Ports([Port.ADAF(
        'Output ADAF with detrended data', name='port1')])

    name = 'Detrend ADAF'
    description = 'Remove trends from timeseries data'
    nodeid = 'org.sysess.sympathy.data.adaf.detrendadafnode'

    def exec_parameter_view(self, node_context):
        """Create the parameter view."""
        tb_ts_dict = None
        tb_dict = None
        if node_context.input['port1'].is_valid():
            tb_ts_dict, tb_dict = get_adaf_info(node_context.input['port1'])
        else:
            tb_ts_dict, tb_dict = {}, {}
        assert(tb_ts_dict is not None)
        check_and_reinit_node(node_context, tb_ts_dict, tb_dict)
        return DetrendWidget(node_context, tb_ts_dict, tb_dict)

    def execute(self, node_context):
        """Execute."""
        in_adaffile = node_context.input['port1']
        out_adaffile = node_context.output['port1']
        tb_ts_dict, tb_dict = get_adaf_info(in_adaffile)
        write_meta_result(in_adaffile, out_adaffile)
        write_timeseries(
            synode.parameters(node_context.parameters), in_adaffile,
            out_adaffile, tb_ts_dict, tb_dict)


DetrendADAFs = node_helper.list_node_factory(
    DetrendADAF, ['port1'], ['port1'])


class DetrendWidget(QtGui.QWidget):
    """A widget containing a TimeBasisWidget and a ListSelectorWidget."""

    def __init__(
            self, node_context, tb_ts_dict, tb_dict, parent=None):
        super(DetrendWidget, self).__init__()
        self._node_context = node_context
        self._tb_ts_dict = tb_ts_dict
        self._tb_dict = tb_dict
        self._parameters = synode.parameters(node_context.parameters)
        self._figure = None
        self._axes = None
        self._canvas = None
        self._toolbar = None

        self._init_gui()

    def _init_gui(self):
        self._pre_init_gui_from_parameters()

        self._tb_selection = self._parameters['tb'].gui()

        self._ts_selection = self._parameters['ts'].gui()

        self._detrend_function = self._parameters['detrend_function'].gui()

        selection_vlayout = QtGui.QVBoxLayout()
        selection_vlayout.addWidget(self._detrend_function)
        selection_vlayout.addWidget(self._tb_selection)
        selection_vlayout.addWidget(self._ts_selection)

        self._x_axis = self._parameters['x_axis'].gui()
        self._y_axis = self._parameters['y_axis'].gui()
        axes_hlayout = QtGui.QHBoxLayout()
        axes_hlayout.addWidget(self._x_axis)
        axes_hlayout.addWidget(self._y_axis)

        self._figure = Figure()
        self._axes = self._figure.add_subplot(111)
        self._canvas = FigureCanvas(self._figure)
        policy = QtGui.QSizePolicy()
        policy.setHorizontalStretch(1)
        policy.setVerticalStretch(1)
        policy.setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
        policy.setVerticalPolicy(QtGui.QSizePolicy.Expanding)
        self._canvas.setSizePolicy(policy)

        self._toolbar = NavigationToolbar(self._canvas, self)

        plot_vlayout = QtGui.QVBoxLayout()
        plot_vlayout.addLayout(axes_hlayout)
        plot_vlayout.addWidget(self._canvas)
        plot_vlayout.addWidget(self._toolbar)

        hlayout = QtGui.QHBoxLayout()
        hlayout.addLayout(selection_vlayout)
        hlayout.addLayout(plot_vlayout)

        layout = QtGui.QVBoxLayout()
        layout.addLayout(hlayout)
        self.setLayout(layout)

        self._init_gui_from_parameters()

        self._tb_selection.editor().itemChanged.connect(
            self._tb_selection_changed)

        self._ts_selection.editor().itemChanged.connect(
            self._ts_selection_changed)

        self._detrend_function.editor().currentIndexChanged.connect(
            self._detrend_function_changed)

        self._x_axis.editor().currentIndexChanged.connect(self._x_axis_changed)
        self._y_axis.editor().currentIndexChanged.connect(self._y_axis_changed)

    def _pre_init_gui_from_parameters(self):
        if self._parameters['tb'].list == []:
            if self._tb_ts_dict is not None:
                self._parameters['tb'].list = self._tb_ts_dict.keys()
                if self._parameters['tb'].list:
                    self._parameters['tb'].value = [0]
            l = self._parameters['tb'].selected
            self._parameters['x_axis'].list = [l] if l is not None else []

        if (self._parameters['ts'].list == [] and
                self._parameters['tb'].list != []):
            self._parameters['ts'].list = self._tb_ts_dict[
                self._parameters['tb'].selected].keys()
            if self._parameters['ts'].list:
                self._parameters['ts'].value = [0]
            self._parameters['y_axis'].list = (
                self._parameters['ts'].value_names)

    def _init_gui_from_parameters(self):
        self._update_figure()

    def _ts_selection_changed(self):
        self._x_axis.editor().blockSignals(True)
        self._y_axis.editor().blockSignals(True)
        selected_items = self._parameters['ts'].value_names

        self._y_axis.editor().clear()
        if selected_items != []:
            self._y_axis.editor().addItems(selected_items)

        self._update_figure()
        self._x_axis.editor().blockSignals(False)
        self._y_axis.editor().blockSignals(False)

    def _detrend_function_changed(self, ind):
        self._update_figure()

    def _x_axis_changed(self, ind):
        self._update_figure()

    def _y_axis_changed(self, ind):
        self._update_figure()

    def _tb_selection_changed(self):
        self._x_axis.editor().blockSignals(True)
        self._y_axis.editor().blockSignals(True)
        self._ts_selection.editor().clear()
        self._ts_selection.editor().addItems(list(
            self._tb_ts_dict[self._parameters['tb'].selected].keys()))
        self._x_axis.editor().clear()
        self._x_axis.editor().addItems([self._parameters['tb'].selected])
        self._y_axis.editor().clear()
        self._y_axis.editor().addItems(self._parameters['ts'].value_names)
        # New ts -> have to update figure
        self._update_figure()
        self._x_axis.editor().blockSignals(False)
        self._y_axis.editor().blockSignals(False)

    def _update_figure(self):
        """Update figure."""
        self._axes.clear()
        if (self._parameters['x_axis'].list != [] and
                self._parameters['y_axis'].list != [] and
                self._parameters['y_axis'].selected):

            tb = self._tb_dict[self._parameters['tb'].selected]['tb']
            selected_y = self._parameters['y_axis'].selected
            selected_x = self._parameters['x_axis'].selected
            if selected_y is not None and selected_x is not None:
                ts = (self._tb_ts_dict[self._parameters['tb'].selected]
                      [selected_y]['ts'])
                if np.all(np.isreal(tb)) and np.all(np.isreal(ts)):
                    ts_new, ts_trend = detrend_data(
                        tb, ts, self._parameters['detrend_function'].value[0])
                    # TODO add grey color
                    self._axes.plot(tb, ts_trend, '--', label='Trend')
                    self._axes.plot(tb, ts, '-', label='Original')
                    self._axes.plot(tb, ts_new, '-', label='Detrended')
                    self._axes.legend()
                    self._axes.set_xlabel(
                        self._tb_dict[selected_x]['raster_name'])
                    self._axes.set_ylabel(selected_y)
        self._canvas.draw()
