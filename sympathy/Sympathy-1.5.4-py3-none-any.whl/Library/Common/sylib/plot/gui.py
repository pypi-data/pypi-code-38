# Copyright (c) 2013, Combine Control Systems AB
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
import datetime
import itertools
import six
from sympathy.api import qt as qt_compat, ParameterView
from sympathy.utils.prim import combined_key
from . import model as models
from . import backend as backends
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.axes import Axes
import numpy as np
qt_compat.backend.use_matplotlib_qt()
QtCore = qt_compat.QtCore
QtGui = qt_compat.import_module('QtGui')


class DuplicateComboboxValidator(QtGui.QValidator):
    def __init__(self, combobox, parent=None):
        super(DuplicateComboboxValidator, self).__init__()
        self._combobox = combobox

    def validate(self, input, pos):
        index = self._combobox.currentIndex()
        other_index = self._combobox.findText(input)
        if index == other_index:
            return self.Acceptable
        elif other_index is -1:
            return self.Acceptable
        return self.Intermediate


def object_or_none(value):
    try:
        return eval(value)
    except Exception:
        return None


def to_unicode(value):
    if value is None:
        return ''
    return six.text_type(value)


def to_repr(value):
    if value is None:
        return ''
    return repr(value)


def get_compact_button(label):
    button = QtGui.QPushButton(label)
    button.setSizePolicy(QtGui.QSizePolicy(
        QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum))
    return button


def get_add_button():
    return get_compact_button(' + ')


def get_remove_button():
    return get_compact_button(' - ')


def _set_field_if(setter, value):
    if value == '':
        return setter(None)
    else:
        value = object_or_none(value)
        if value is not None:
            return setter(value)


def _set_color_if(lineedit, value):
    if value:
        lineedit.setStyleSheet('QLineEdit { color : back; }')
    else:
        lineedit.setStyleSheet('QLineEdit { color : red; }')


def _set_lineedit_field(lineedit, setter, value):
    _set_color_if(lineedit, _set_field_if(setter, value))


class PlotConfigWidget(QtGui.QWidget):
    plot_changed = qt_compat.Signal()

    def __init__(self, model):
        super(PlotConfigWidget, self).__init__()
        self._model = model
        self._plot = QtGui.QComboBox()
        self._control_add = get_add_button()
        self._control_remove = get_remove_button()
        self._title = QtGui.QLineEdit()
        self._show_legend = QtGui.QCheckBox()

        # Layout GUI.
        layout = QtGui.QFormLayout()
        control = QtGui.QGroupBox()
        control_layout = QtGui.QHBoxLayout()
        control_layout.addWidget(self._plot)
        control_layout.addWidget(self._control_add)
        control_layout.addWidget(self._control_remove)
        control.setLayout(control_layout)
        layout.addRow('Plot', control)
        layout.addRow('Title', self._title)
        layout.addRow('Show legend', self._show_legend)
        self.setLayout(layout)

        # Initialize Data.
        self._plot.addItems([plot.get_title()
                             for plot in self._model.get_plots()])
        self._select_plot(0)

        # Setup Widgets.
        self._plot.currentIndexChanged[int].connect(self._select_plot)
        self._control_add.clicked.connect(self._control_add_clicked)
        self._control_remove.clicked.connect(self._control_remove_clicked)
        self._title.textChanged.connect(self._title_changed)
        self._show_legend.stateChanged.connect(self._show_legend_changed)

    def _control_add_clicked(self):
        plot = models.PlotModel(table=self._model.get_table())
        self._model.add_plot(plot)
        self._plot.addItem(plot.get_title())
        self._plot.setCurrentIndex(self._plot.count() - 1)

    def _control_remove_clicked(self):
        index = self._plot.currentIndex()
        if index == self._model.get_index():
            self._model.set_index(index - 1)
        self._model.remove_plot(self._model.get_plots()[index])
        self._plot.removeItem(index)

    def _title_changed(self, value):
        self._model.set_title(value)
        self._plot.setItemText(self._plot.currentIndex(), value)

    def _select_plot(self, value):
        if value is -1:
            return
        self._model.set_index(value)
        self._title.setText(self._model.get_title())
        self._plot.setCurrentIndex(value)
        self._show_legend.setChecked(self._model.get_show_legend())
        self.plot_changed.emit()

    def _plot_type_changed(self, value):
        self._model.set_plot_type(value)

    def _show_legend_changed(self, value):
        self._model.set_show_legend(value)


class AxisConfigWidget(QtGui.QWidget):
    axis_label_changed = qt_compat.Signal(six.text_type, six.text_type)
    axis_axes_added = qt_compat.Signal(six.text_type)
    axis_axes_removed = qt_compat.Signal(six.text_type)
    SCALAR_TAB = 0
    DATETIME_TAB = 1

    def __init__(self, model):
        super(AxisConfigWidget, self).__init__()
        self._model = model
        self._axis = QtGui.QComboBox()
        self._label = QtGui.QLineEdit()
        self._scale = QtGui.QComboBox()
        self._ticks_min = QtGui.QLineEdit()
        self._ticks_max = QtGui.QLineEdit()
        self._limits_tabs = QtGui.QTabWidget()
        self._limits_min = QtGui.QLineEdit()
        self._limits_max = QtGui.QLineEdit()
        self._min_datepicker = QtGui.QDateTimeEdit()
        self._max_datepicker = QtGui.QDateTimeEdit()
        self._min_datepicker.setDisplayFormat('yyyy-MM-dd hh:mm:ss')
        self._max_datepicker.setDisplayFormat('yyyy-MM-dd hh:mm:ss')
        self._datepicker = QtGui.QCalendarWidget()
        self._grid = QtGui.QComboBox()
        self._control_add = get_add_button()
        self._control_remove = get_remove_button()

        # Layout GUI.
        layout = QtGui.QVBoxLayout()
        form_layout = QtGui.QFormLayout()

        # Limits and ticks
        limits = QtGui.QVBoxLayout()
        limits_tab = QtGui.QWidget()
        self._limits_tabs.addTab(limits_tab, 'Regular')
        limits_tab_layout = QtGui.QFormLayout(limits_tab)
        limits_tab_layout.addRow('Min', self._limits_min)
        limits_tab_layout.addRow('Max', self._limits_max)
        limits_tab.setLayout(limits_tab_layout)
        limits_tab_layout.addRow('Minor ticks', self._ticks_min)
        limits_tab_layout.addRow('Major ticks', self._ticks_max)
        time_tab = QtGui.QWidget()
        self._limits_tabs.addTab(time_tab, 'Datetime')
        time_tab_layout = QtGui.QFormLayout(time_tab)
        time_tab_layout.addRow('Min', self._min_datepicker)
        time_tab_layout.addRow('Max', self._max_datepicker)
        time_tab.setLayout(time_tab_layout)
        limits.addWidget(self._limits_tabs)

        # Axis, Label, Scale, and Grid
        control = QtGui.QGroupBox('')
        control_layout = QtGui.QHBoxLayout()
        control_layout.addWidget(self._axis)
        control_layout.addWidget(self._control_add)
        control_layout.addWidget(self._control_remove)
        control.setLayout(control_layout)
        form_layout.addRow('Axis', control)
        form_layout.addRow('Label', self._label)
        form_layout.addRow('Scale', self._scale)
        form_layout.addRow('Limits and Ticks', limits)

        form_layout.addRow('Grid', self._grid)
        layout.addLayout(form_layout)
        self.setLayout(layout)

        # Initialize Data.
        self._scale.addItems(['linear', 'log'])
        self._grid.addItems(models.grid_options)
        self.load()

        # Setup Widgets.
        self._label.setValidator(DuplicateComboboxValidator(self._axis))
        self._scale.currentIndexChanged[six.text_type].connect(
            self._scale_changed)
        self._control_add.clicked.connect(self._control_add_clicked)
        self._control_remove.clicked.connect(self._control_remove_clicked)
        self._axis.currentIndexChanged[int].connect(self._select_axis)
        self._label.editingFinished.connect(self._label_changed)
        self._limits_min.textChanged.connect(self._limits_min_changed)
        self._limits_max.textChanged.connect(self._limits_max_changed)
        self._min_datepicker.dateTimeChanged.connect(
            self._datetime_min_changed)
        self._max_datepicker.dateTimeChanged.connect(
            self._datetime_max_changed)
        self._ticks_min.textChanged.connect(self._ticks_min_changed)
        self._ticks_max.textChanged.connect(self._ticks_max_changed)
        self._grid.currentIndexChanged[six.text_type].connect(
            self._grid_changed)
        self._limits_tabs.currentChanged.connect(self._limit_tab_changed)

    def clear(self):
        self._axis.blockSignals(True)
        self._axis.clear()

    def load(self):
        for axis in self._model.get_axes():
            self._axis.addItem(axis.get_label())
        self._axis.blockSignals(False)
        self._select_axis(0)

    def axes_changed(self, value):
        no_y = self._axis.count() - 1
        difference = value - no_y

        if difference > 0:
            self._axis.addItems(
                [six.text_type(x) for x in range(no_y + 1, value + 1)])
        elif difference < 0:
            if self._axis.currentIndex() >= value:
                self._select_axis(0)
            for i in range(-difference):
                index = self._axis.count() - 1
                self._axis.removeItem(index)

    def _get_axis_model(self):
        return self._model.get_axes()[self._axis.currentIndex()]

    def _control_add_clicked(self):
        used = [axis.get_label() for axis in self._model.get_axes()]
        integers = itertools.count()
        label = 'New axis {}'.format(next(integers))
        while label in used:
            label = 'New axis {}'.format(next(integers))
        axis = models.AxisModel(self._model, None, label)
        self._model.add_axis(axis)
        self._axis.addItem(label)
        self._axis.setCurrentIndex(self._axis.count() - 1)
        self.axis_axes_added.emit(label)

    def _control_remove_clicked(self):
        index = self._axis.currentIndex()
        axis = self._get_axis_model()
        label = axis.get_label()
        try:
            self._model.remove_axis(axis)
        except ValueError:
            return
        self._axis.removeItem(index)
        self.axis_axes_removed.emit(label)

    def _select_axis(self, value):
        axis_model = self._get_axis_model()
        index_scale = self._scale.findText(axis_model.get_scale())
        index_grid = self._grid.findText(axis_model.get_grid())
        self._scale.setCurrentIndex(index_scale)
        self._grid.setCurrentIndex(index_grid)
        self._axis.setCurrentIndex(value)
        self._label.setText(axis_model.get_label())
        self._limits_min.setText(to_repr(axis_model.get_limits_min()))
        self._limits_max.setText(to_repr(axis_model.get_limits_max()))
        self._ticks_min.setText(to_repr(axis_model.get_ticks_minor()))
        self._ticks_max.setText(to_repr(axis_model.get_ticks_major()))

    def _label_changed(self):
        value = self._label.text()
        previous = self._get_axis_model().get_label()
        self._get_axis_model().set_label(value)
        self._axis.setItemText(self._axis.currentIndex(), value)
        self.axis_label_changed.emit(previous, value)

    def _scale_changed(self, value):
        self._get_axis_model().set_scale(value)

    def _limits_min_changed(self, value):
        _set_lineedit_field(
            self._limits_min, self._get_axis_model().set_limits_min, value)

    def _limits_max_changed(self, value):
        _set_lineedit_field(
            self._limits_max, self._get_axis_model().set_limits_max, value)

    def _datetime_min_changed(self, value):
        self._limits_min_changed(repr(datetime.datetime.fromtimestamp(
            self._min_datepicker.dateTime().toTime_t())))
        self._clear_ticks()

    def _datetime_max_changed(self, value):
        self._limits_max_changed(repr(datetime.datetime.fromtimestamp(
            self._max_datepicker.dateTime().toTime_t())))
        self._clear_ticks()

    def _ticks_min_changed(self, value):
        _set_lineedit_field(
            self._ticks_min, self._get_axis_model().set_ticks_minor, value)

    def _ticks_max_changed(self, value):
        _set_lineedit_field(
            self._ticks_max, self._get_axis_model().set_ticks_major, value)

    def _grid_changed(self, value):
        self._get_axis_model().set_grid(value)

    def _limit_tab_changed(self):
        min_limit = self._get_axis_model().get_limits_min()
        max_limit = self._get_axis_model().get_limits_max()
        if (isinstance(min_limit, datetime.datetime) and
           isinstance(max_limit, datetime.datetime) and
           self._limits_tabs.currentIndex() == self.DATETIME_TAB):
            self._min_datepicker.setDateTime(min_limit)
            self._max_datepicker.setDateTime(max_limit)
            self._clear_ticks()
        else:
            min_limit = datetime.datetime.fromtimestamp(
                self._min_datepicker.dateTime().toTime_t())
            max_limit = datetime.datetime.fromtimestamp(
                self._max_datepicker.dateTime().toTime_t())
            if min_limit != max_limit:
                self._limits_min.setText(repr(min_limit))
                self._limits_max.setText(repr(max_limit))
            else:
                self._limits_min.setText('')
                self._limits_max.setText('')

    def _clear_ticks(self):
        self._ticks_min_changed('')
        self._ticks_max_changed('')
        self._ticks_min.setText('')
        self._ticks_max.setText('')


class StatisticsConfigWidget(QtGui.QWidget):

    def __init__(self, model):
        super(StatisticsConfigWidget, self).__init__()
        self._model = model
        self._signal = QtGui.QComboBox()

        self._statistics = list()
        self._statistics_signals = list()
        self._statistics_std = QtGui.QCheckBox('Std')
        self._statistics_mean = QtGui.QCheckBox('Mean')
        self._statistics_max = QtGui.QCheckBox('Max')
        self._statistics_min = QtGui.QCheckBox('Min')
        self._show_statistics = QtGui.QCheckBox()

        self._table = QtGui.QTableWidget()
        self._table.setColumnCount(1)
        self._table.insertRow(0)

        self._limits = QtGui.QTableWidget()
        self._limits.setColumnCount(1)
        self._limits.insertRow(0)

        self._control_add = get_add_button()
        self._control_remove = get_remove_button()

        self.limit_trigger = self._model.get_limits_trigger()

        # Layout GUI.
        layout = QtGui.QVBoxLayout()
        form_layout = QtGui.QFormLayout()
        statistics = QtGui.QGroupBox('')
        statistics_box_layout = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight)

        control = QtGui.QGroupBox('')
        control_layout = QtGui.QHBoxLayout()
        control_layout.addWidget(self._signal)
        control_layout.addWidget(self._control_add)
        control_layout.addWidget(self._control_remove)
        control.setLayout(control_layout)
        form_layout.addRow('Signal', control)

        statistics_box_layout.addWidget(self._statistics_std)
        statistics_box_layout.addWidget(self._statistics_mean)
        statistics_box_layout.addWidget(self._statistics_min)
        statistics_box_layout.addWidget(self._statistics_max)

        statistics.setLayout(statistics_box_layout)
        form_layout.addRow('Statistics', statistics)
        form_layout.addRow(self._table)
        form_layout.addRow('Limits', QtGui.QWidget())
        form_layout.addRow(self._limits)
        form_layout.addRow('Show statistics', self._show_statistics)

        layout.addLayout(form_layout)
        self.setLayout(layout)

        # Initialize Data.
        self.clear()
        self.load()

        # Setup Widgets.
        self._control_add.clicked.connect(self._control_add_clicked)
        self._control_remove.clicked.connect(self._control_remove_clicked)
        self._signal.currentIndexChanged[int].connect(self._select_signal)
        self.limit_trigger.connect(self.refresh_table)

        func = self._statistics_std_changed
        self._statistics_std.stateChanged.connect(func)
        func = self._statistics_mean_changed
        self._statistics_mean.stateChanged.connect(func)
        func = self._statistics_min_changed
        self._statistics_min.stateChanged.connect(func)
        func = self._statistics_max_changed
        self._statistics_max.stateChanged.connect(func)
        func = self._show_statistics_changed
        self._show_statistics.stateChanged.connect(func)

    def clear(self):
        """Clear previous attributes."""
        self._signal.blockSignals(True)
        self._signal.clear()
        self._table.clear()
        self._table.setRowCount(0)
        self._table.setColumnCount(1)
        self._limits.clear()
        self._limits.setRowCount(0)
        self._limits.setColumnCount(1)
        del self._statistics_signals
        del self._statistics

    def load(self):
        """Loads and set up wanted environment."""
        self._statistics = list()
        self._statistics_signals = list()

        self._model.set_show_statistics(False)
        self._model.clear_limits()
        if self._model.show_annotation():
            self._model.toggle_annotation()
        if self._model.show_selectors():
            self._model.toggle_selectors()

        for signal in self._model.get_signals():
            label = signal.get_label()
            self._signal.addItem(label)
            self.add_signal(signal)
            signal.get_std_y()
            signal.get_mean_y()
            signal.get_min_y()
            signal.get_max_y()

        self._signal.blockSignals(False)
        self._select_signal(0)

        self._table.setHorizontalHeaderItem(
            0, QtGui.QTableWidgetItem('Signal'))
        self._limits.setHorizontalHeaderItem(
            0, QtGui.QTableWidgetItem('X Axis'))

        self._table.setVerticalHeaderLabels(
            [six.text_type(i) for i in range(self._table.rowCount())])

        self._limits.setVerticalHeaderLabels(
            [six.text_type(i) for i in range(self._limits.rowCount())])

        self.limit_trigger = self._model.get_limits_trigger()
        self.limit_trigger.connect(self.refresh_table)

    def _get_signal_model(self):
        return self._model.get_signals()[self._signal.currentIndex()]

    def _control_add_clicked(self):
        """Add signal to table when add is clicked."""
        signal = self._get_signal_model()
        if self._limits.rowCount() == 0:
            self._limits.setColumnCount(4)
            self._limits.setHorizontalHeaderItem(
                1, QtGui.QTableWidgetItem("X axes"))
            self._limits.setHorizontalHeaderItem(
                1, QtGui.QTableWidgetItem("Min limit"))
            self._limits.setHorizontalHeaderItem(
                2, QtGui.QTableWidgetItem("Max limit"))
            self._limits.setHorizontalHeaderItem(
                3, QtGui.QTableWidgetItem("Delta"))
        self.add_signal(signal)

    def _control_remove_clicked(self):
        """Removes signal from table when remove is clicked. Append removed
        signals x axis from limits table if axis not used by other signals in
        statistics table.
        """
        signal = self._get_signal_model()
        if len(self._statistics_signals) == 1:
            for column in range(0, self._limits.columnCount()):
                self._limits.removeColumn(0)
            self._limits.removeRow(0)

        self.remove_signal(signal)
        for sig in self._model.get_signals():
            if (signal.get_axis_x() == sig.get_axis_x() and
               sig.get_label() in self._statistics_signals):
                self._append_limits(sig)
                return

    def add_signal(self, signal):
        """Add signal to table if not already there, adds x axis limits
        to table if not already there.
        params:
            signal: Signal to add.
        """
        # If there is no available data...
        if signal.get_data()[0] == '':
            return
        set_stat = True
        set_limits = True
        for i in range(0, self._table.rowCount()):
            if signal.get_label() == self._table.item(i, 0).text():
                set_stat = False
                break
        for j in range(0, self._limits.rowCount()):
            if signal.get_axis_x() == self._limits.item(j, 0).text():
                set_limits = False
                break
        if set_stat:
            self._append_statistics(signal)
        if set_limits:
            self._append_limits(signal)

    def remove_signal(self, signal):
        """Removes signal from statistics table and axis from limits table.
        params:
            signal: Signal to remove.
        """
        signal_label = signal.get_label()
        x_axis = signal.get_axis_x()
        if signal_label in self._statistics_signals:
            self._statistics_signals.remove(signal_label)
            self._model.set_statistics_signals(self._statistics_signals)
        for index in range(0, self._table.rowCount()):
            if signal_label == self._table.item(index, 0).text():
                self._table.removeRow(index)
                break
        for index in range(0, self._limits.rowCount()):
            if x_axis == self._limits.item(index, 0).text():
                self._limits.removeRow(index)
                break

    def _append_limits(self, signal):
        """Creates the limits table if not existing othervise appends signals
        low and high limits to table.
        params:
            signal: Signal to append.
        """
        if self._limits.rowCount() == 0:
            self._limits.setColumnCount(4)
            self._limits.setHorizontalHeaderItem(
                1, QtGui.QTableWidgetItem("X axes"))
            self._limits.setHorizontalHeaderItem(
                1, QtGui.QTableWidgetItem("Min limit"))
            self._limits.setHorizontalHeaderItem(
                2, QtGui.QTableWidgetItem("Max limit"))
            self._limits.setHorizontalHeaderItem(
                3, QtGui.QTableWidgetItem("Delta"))

        min_lim, max_lim = signal.get_x_limits()
        self._limits.insertRow(0)
        self._limits.setItem(0, 0, QtGui.QTableWidgetItem(signal.get_axis_x()))
        self._limits.setItem(0, 1, QtGui.QTableWidgetItem(
                             backends.format_value(min_lim)))
        self._limits.setItem(0, 2, QtGui.QTableWidgetItem(
                             backends.format_value(max_lim)))
        try:
            delta = max_lim - min_lim
            if delta < 0:
                delta = np.timedelta64(0)
            self._limits.setItem(0, 3, QtGui.QTableWidgetItem(
                                 backends.format_value(delta)))
        except:
            pass

        self._limits.setVerticalHeaderLabels(
            [six.text_type(i) for i in range(self._limits.rowCount())])

    def _append_statistics(self, signal):
        """Inserts a new row in statistics table and appends checked attributes
        and values.
        params:
            signal: Signal for which statisitics will be calculated.
        """
        self._statistics_signals.append(signal.get_label())
        self._table.insertRow(0)
        self._table.setItem(0, 0, QtGui.QTableWidgetItem(signal.get_label()))
        self._statistics = list()
        if self._statistics_std.checkState():
            self._statistics.append('Std')
            self.fill_column(self.get_column("Std"), [signal],
                             [signal.get_std_y()])
        if self._statistics_mean.checkState():
            self.fill_column(self.get_column("Mean"), [signal],
                             [signal.get_mean_y()])
            self._statistics.append('Mean')
        if self._statistics_min.checkState():
            self.fill_column(self.get_column("Min"), [signal],
                             [signal.get_min_y()])
            self._statistics.append('Min')
        if self._statistics_max.checkState():
            self.fill_column(self.get_column("Max"), [signal],
                             [signal.get_max_y()])
            self._statistics.append('Max')

        self._model.set_statistics(self._statistics)
        self._model.set_statistics_signals(self._statistics_signals)

        self._table.setVerticalHeaderLabels(
            [six.text_type(i) for i in range(self._table.rowCount())])

    def refresh_table(self):
        signals = self._model.get_signals()
        self._statistics_signals = self._model.get_statistics_signals()
        for signal in signals:
            if signal.get_label() in self._statistics_signals:
                self.remove_signal(signal)
            self.add_signal(signal)

    def signal_added(self, label):
        self._signal.addItem(label)

    def signal_removed(self, rm):
        label = self._signal.itemText(rm)
        self._statistics_signals.remove(label)
        self._model.set_statistics_signals(self._statistics_signals)

        for index in range(0, self._signal.count()):
            if index >= self._table.rowCount():
                break
            if label == self._table.item(index, 0).text():
                self._table.removeRow(index)
                break
        self._signal.removeItem(rm)

    def _select_signal(self, value):
        pass

    def remove_column(self, label):
        """Remove column from statistics table.
        params:
            label: Name of column to remove.
        """
        for column in range(1, self._table.columnCount()):
            if self._table.horizontalHeaderItem(column).text() == label:
                self._table.removeColumn(column)
                break

    def fill_column(self, column, signals, values):
        """Fill column in statistics table.
        params:
            column: the column to fill.
            signals: the signals to fill the column with.
            values: the values to fill the column withs.
        """
        iterator = iter(values)
        for signal in signals:
            value = next(iterator)
            for index in range(0, self._table.rowCount()):
                if signal.get_label() == self._table.item(index, 0).text():
                    self._table.setItem(index, column,
                                        QtGui.QTableWidgetItem(str(value)))
                    break

    def get_column(self, label):
        """Return column with label if existing, otherwise creates
        and returns new label.
        params:
            label: Name of column.
        return:
            column: The column.
        """
        for column in range(1, self._table.columnCount()):
            if self._table.horizontalHeaderItem(column).text() == label:
                return column
        column = self._table.columnCount()
        self._table.setColumnCount(column + 1)
        self._table.setHorizontalHeaderItem(
            column, QtGui.QTableWidgetItem(label))
        return column

    def _statistics_std_changed(self, value):
        """Handles when std checkbox have been checked/unchecked."""
        label = "Std"
        if self._statistics_std.checkState():
            self._statistics.append(label)
            column = self.get_column(label)
            signals = self._model.get_signals()
            values = []
            sigs = list()
            for signal in signals:
                try:
                    values.append(signal.get_std_y())
                    sigs.append(signal)
                except:
                    pass
            self.fill_column(column, sigs, values)
        else:
            self._statistics.remove(label)
            self.remove_column(label)
        self._model.set_statistics(self._statistics)

    def _statistics_mean_changed(self, value):
        """Handles when mean checkbox have been checked/unchecked."""
        label = "Mean"
        if self._statistics_mean.checkState():
            self._statistics.append(label)
            column = self.get_column(label)
            signals = self._model.get_signals()
            values = []
            sigs = list()
            for signal in signals:
                try:
                    values.append(signal.get_mean_y())
                    sigs.append(signal)
                except:
                    pass
            self.fill_column(column, sigs, values)
        else:
            self._statistics.remove(label)
            self.remove_column(label)
        self._model.set_statistics(self._statistics)

    def _statistics_min_changed(self, value):
        """Handles when min checkbox have been checked/unchecked."""
        label = "Min"
        if self._statistics_min.checkState():
            self._statistics.append(label)
            column = self.get_column(label)
            signals = self._model.get_signals()
            values = []
            sigs = list()
            for signal in signals:
                try:
                    values.append(signal.get_min_y())
                    sigs.append(signal)
                except:
                    pass
            self.fill_column(column, sigs, values)
        else:
            self._statistics.remove(label)
            self.remove_column(label)
        self._model.set_statistics(self._statistics)

    def _statistics_max_changed(self, value):
        """Handles when max checkbox have been checked/unchecked."""
        label = "Max"
        if self._statistics_max.checkState():
            self._statistics.append(label)
            column = self.get_column(label)
            signals = self._model.get_signals()
            values = []
            sigs = list()
            for signal in signals:
                try:
                    values.append(signal.get_max_y())
                    sigs.append(signal)
                except:
                    pass
            self.fill_column(column, sigs, values)
        else:
            self._statistics.remove(label)
            self.remove_column(label)
        self._model.set_statistics(self._statistics)

    def _show_statistics_changed(self, value):
        """Called when show statistics button is checked/unchecked.
        params:
            value: The value that is to be set.
        """
        self._model.set_show_statistics(value)


class SignalConfigWidget(QtGui.QWidget):
    signal_added = qt_compat.Signal(six.text_type)
    signal_removed = qt_compat.Signal(int)

    def __init__(self, model):
        super(SignalConfigWidget, self).__init__()
        self._model = model
        self._signal = QtGui.QComboBox()
        self._label = QtGui.QLineEdit()
        self._axis_x = QtGui.QComboBox()
        self._axis_y = QtGui.QComboBox()
        self._data_x = FilteredComboBox()
        self._data_y = FilteredComboBox()
        self._line_style = QtGui.QComboBox()
        self._line_width = QtGui.QLineEdit()
        self._line_color = QtGui.QLineEdit()
        self._line_button = get_compact_button('...')
        self._color_layout = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight)
        self._marker_style = QtGui.QComboBox()
        self._marker_size = QtGui.QLineEdit()
        self._marker_edgewidth = QtGui.QLineEdit()
        self._marker_facecolor = QtGui.QLineEdit()
        self._face_button = get_compact_button('...')
        self._face_layout = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight)
        self._marker_edgecolor = QtGui.QLineEdit()
        self._edge_button = get_compact_button('...')
        self._edge_layout = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight)
        self._control_add = get_add_button()
        self._control_remove = get_remove_button()

        # Layout GUI.
        layout = QtGui.QFormLayout()
        axis = QtGui.QGroupBox('')
        axis_formlayout = QtGui.QFormLayout()
        data = QtGui.QGroupBox('')
        data_formlayout = QtGui.QFormLayout()
        line = QtGui.QGroupBox('')
        marker = QtGui.QGroupBox('')
        line_formlayout = QtGui.QFormLayout()
        marker_formlayout = QtGui.QFormLayout()
        control = QtGui.QGroupBox('')
        control_layout = QtGui.QHBoxLayout()

        control_layout.addWidget(self._signal)
        control_layout.addWidget(self._control_add)
        control_layout.addWidget(self._control_remove)
        control.setLayout(control_layout)
        layout.addRow('Signal', control)
        layout.addRow('Label', self._label)
        axis_formlayout.addRow('X', self._axis_x)
        axis_formlayout.addRow('Y', self._axis_y)
        axis.setLayout(axis_formlayout)
        layout.addRow('Axis', axis)
        data_formlayout.addRow('X', self._data_x)
        data_formlayout.addRow('Y', self._data_y)
        data.setLayout(data_formlayout)
        layout.addRow('Data', data)
        line_formlayout.addRow('Style', self._line_style)
        line_formlayout.addRow('Width', self._line_width)
        self._color_layout.addWidget(self._line_color)
        self._color_layout.addWidget(self._line_button)
        line_formlayout.addRow('Color', self._color_layout)
        line.setLayout(line_formlayout)
        layout.addRow('Line', line)
        marker_formlayout.addRow('Style', self._marker_style)
        marker_formlayout.addRow('Size', self._marker_size)
        marker_formlayout.addRow('Edge width', self._marker_edgewidth)
        self._face_layout.addWidget(self._marker_facecolor)
        self._face_layout.addWidget(self._face_button)
        marker_formlayout.addRow('Face color', self._face_layout)
        self._edge_layout.addWidget(self._marker_edgecolor)
        self._edge_layout.addWidget(self._edge_button)
        marker_formlayout.addRow('Edge color', self._edge_layout)
        marker.setLayout(marker_formlayout)
        layout.addRow('Marker', marker)
        self.setLayout(layout)

        # Initialize Data.
        column_names = []
        if self._model.get_table().is_valid():
            column_names = self._model.get_table().column_names()
        column_names_data = [column_name
                             for mod in self._model.get_plots()
                             for signal in mod.get_signals()
                             for column_name in signal.get_data()]
        column_names = sorted(set(column_names + column_names_data),
                              key=combined_key)

        self._data_x.addItems(column_names)
        self._data_y.addItems(column_names)
        self.load()

        # Setup Widgets.
        self._label.setValidator(DuplicateComboboxValidator(self._signal))
        self._line_width.setValidator(QtGui.QDoubleValidator())
        self._marker_size.setValidator(QtGui.QDoubleValidator())
        self._marker_edgewidth.setValidator(QtGui.QDoubleValidator())
        self._line_style.addItems(models.LineModel.line_styles)
        self._marker_style.addItems(models.MarkerModel.marker_styles)
        self._control_add.clicked.connect(self._control_add_clicked)
        self._control_remove.clicked.connect(self._control_remove_clicked)
        self._signal.currentIndexChanged[int].connect(self._select_signal)
        self._label.editingFinished.connect(self._label_changed)
        self._axis_x.currentIndexChanged[six.text_type].connect(
            self._axis_x_changed)
        self._axis_y.currentIndexChanged[six.text_type].connect(
            self._axis_y_changed)
        self._data_x.currentIndexChanged[six.text_type].connect(
            self._data_x_changed)
        self._data_y.currentIndexChanged[six.text_type].connect(
            self._data_y_changed)
        self._line_style.currentIndexChanged[six.text_type].connect(
            self._line_style_changed)
        self._line_width.textChanged.connect(self._line_width_changed)
        self._line_color.textChanged.connect(self._line_color_changed)
        self._line_button.clicked.connect(self._line_button_clicked)
        self._marker_style.currentIndexChanged[six.text_type].connect(
            self._marker_style_changed)
        self._marker_size.textChanged.connect(self._marker_size_changed)
        self._marker_edgewidth.textChanged.connect(
            self._marker_edgewidth_changed)
        self._marker_facecolor.textChanged.connect(
            self._marker_facecolor_changed)
        self._face_button.clicked.connect(self._face_button_clicked)
        self._marker_edgecolor.textChanged.connect(
            self._marker_edgecolor_changed)
        self._edge_button.clicked.connect(self._edge_button_clicked)

    def clear(self):
        self._signal.blockSignals(True)
        self._axis_y.blockSignals(True)
        self._axis_x.blockSignals(True)
        self._signal.clear()
        self._axis_y.clear()
        self._axis_x.clear()

    def load(self):
        for axis in self._model.get_axes():
            self._axis_x.addItem(axis.get_label())
            self._axis_y.addItem(axis.get_label())
        for signal in self._model.get_signals():
            self._signal.addItem(signal.get_label())

        self._signal.blockSignals(False)
        self._axis_y.blockSignals(False)
        self._axis_x.blockSignals(False)

        self._select_signal(0)

    def axis_label_changed(self, previous, current):
        self._axis_x.setItemText(self._axis_x.findText(previous), current)
        self._axis_y.setItemText(self._axis_y.findText(previous), current)

    def axis_axes_added(self, label):
        self._axis_x.addItem(label)
        self._axis_y.addItem(label)

    def axis_axes_removed(self, label):
        self._axis_x.setItemText(self._axis_x.findText(label), 'Unknown axis')
        self._axis_x.setItemText(self._axis_y.findText(label), 'Unknown axis')

    def _get_signal_model(self):
        return self._model.get_signals()[self._signal.currentIndex()]

    def _control_add_clicked(self):
        used = [signal.get_label() for signal in self._model.get_signals()]
        integers = itertools.count()
        label = 'New signal {}'.format(next(integers))
        while label in used:
            label = 'New signal {}'.format(next(integers))
        signal = models.SignalModel(self._model, None, label)
        signal.set_axis_x(self._model.get_signals()[0].get_axis_x())
        self._model.add_signal(signal)
        self._signal.addItem(signal.get_label())
        self._signal.setCurrentIndex(self._signal.count() - 1)
        self.signal_added.emit(signal.get_label())

    def _control_remove_clicked(self):
        index = self._signal.currentIndex()

        signal = self._get_signal_model()
        try:
            self._model.remove_signal(signal)
        except ValueError:
            return

        self._signal.removeItem(index)
        self.signal_removed.emit(index)

    def _select_signal(self, signal):
        signal_model = self._get_signal_model()
        data_x, data_y = signal_model.get_data()
        axis_x, axis_y = signal_model.get_axis()
        line = signal_model.get_line()
        marker = signal_model.get_marker()
        index_line_style = self._line_style.findText(
            line.get_style())
        index_marker_style = self._marker_style.findText(
            marker.get_style())

        self._label.setText(signal_model.get_label())
        self._data_x.setCurrentIndex(self._data_x.findText(data_x))
        self._data_y.setCurrentIndex(self._data_y.findText(data_y))
        self._axis_x.setCurrentIndex(self._axis_x.findText(axis_x))
        self._axis_y.setCurrentIndex(self._axis_y.findText(axis_y))
        self._line_style.setCurrentIndex(index_line_style)
        self._line_width.setText(to_unicode(line.get_width()))
        self._line_color.setText(to_unicode(line.get_color()))
        self._marker_style.setCurrentIndex(index_marker_style)
        self._marker_size.setText(to_unicode(marker.get_size()))
        self._marker_edgewidth.setText(to_unicode(marker.get_edgewidth()))
        self._marker_facecolor.setText(to_unicode(marker.get_facecolor()))
        self._marker_edgecolor.setText(to_unicode(marker.get_edgecolor()))

    def _label_changed(self):
        value = self._label.text()
        self._get_signal_model().set_label(value)
        self._signal.setItemText(self._signal.currentIndex(), value)

    def _data_x_changed(self, value):
        self._get_signal_model().set_data_x(value)

    def _data_y_changed(self, value):
        self._get_signal_model().set_data_y(value)

    def _axis_x_changed(self, value):
        for signal in self._model.get_signals():
            signal.set_axis_x(value)

    def _axis_y_changed(self, value):
        self._get_signal_model().set_axis_y(value)

    def _line_style_changed(self, value):
        self._get_signal_model().get_line().set_style(value)

    def _line_width_changed(self, value):
        _set_lineedit_field(
            self._line_width, self._get_signal_model().get_line().set_width,
            value)

    def _line_color_changed(self, value):
        _set_lineedit_field(
            self._line_color, self._get_signal_model().get_line().set_color,
            value)

    def _line_button_clicked(self):
        self._set_line_color(self._line_color)

    def _marker_style_changed(self, value):
        self._get_signal_model().get_marker().set_style(value)

    def _marker_size_changed(self, value):
        _set_lineedit_field(
            self._marker_size,
            self._get_signal_model().get_marker().set_size,
            value)

    def _marker_edgewidth_changed(self, value):
        _set_lineedit_field(
            self._marker_edgewidth,
            self._get_signal_model().get_marker().set_edgewidth,
            value)

    def _marker_edgecolor_changed(self, value):
        _set_lineedit_field(
            self._marker_edgecolor,
            self._get_signal_model().get_marker().set_edgecolor,
            value)

    def _edge_button_clicked(self):
        self._set_line_color(self._marker_edgecolor)

    def _marker_facecolor_changed(self, value):
        _set_lineedit_field(
            self._marker_facecolor,
            self._get_signal_model().get_marker().set_facecolor,
            value)

    def _face_button_clicked(self):
        self._set_line_color(self._marker_facecolor)

    def _set_line_color(self, line):
        r, b, g, a = QtGui.QColorDialog.getColor().getRgbF()
        if not (r == 0 and b == 0 and g == 0 and a == 1):
            line.setText('(%(r)1.1f, %(b)1.1f, %(g)1.1f, %(a)1.1f)'
                         % {'r': r, 'b': b, 'g': g, 'a': a})


class ConfigWidget(QtGui.QWidget):

    def __init__(self, model):
        super(ConfigWidget, self).__init__()
        self._model = model
        self.plot = PlotConfigWidget(model)
        self.axis = AxisConfigWidget(model)
        self.signal = SignalConfigWidget(model)
        self.statistics = StatisticsConfigWidget(model)
        self.setMinimumSize(400, 250)

        # Layout GUI.
        layout = QtGui.QHBoxLayout()
        tabs = QtGui.QTabWidget()
        tabs.addTab(self.plot, 'Plot')
        tabs.addTab(self.axis, 'Axis')
        tabs.addTab(self.signal, 'Signal')
        tabs.addTab(self.statistics, 'Statistics')
        tabs.currentChanged.connect(self.statistics.refresh_table)
        layout.addWidget(tabs)
        self.setLayout(layout)

        # Setup Widgets.
        self.axis.axis_label_changed.connect(self.signal.axis_label_changed)
        self.axis.axis_axes_added.connect(self.signal.axis_axes_added)
        self.axis.axis_axes_removed.connect(self.signal.axis_axes_removed)
        self.signal.signal_added.connect(self.statistics.signal_added)
        self.signal.signal_removed.connect(self.statistics.signal_removed)
        self.plot_changed = self.plot.plot_changed

    def load(self):
        self.signal.clear()
        self.axis.clear()
        self.statistics.clear()
        self.axis.load()
        self.signal.load()
        self.statistics.load()


class MainWidget(ParameterView):
    def __init__(self, model, save_model=None):
        super(MainWidget, self).__init__()

        if save_model is not None:
            self._save_model = save_model
        else:
            self._save_model = lambda model: None
        self._model = model
        layout = QtGui.QVBoxLayout()
        model = IndexedPlotModel(model)
        splitter = QtGui.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self._config = ConfigWidget(model)
        self._plot = PlotWidget(model)
        splitter.addWidget(self._config)
        splitter.addWidget(self._plot)
        splitter.setHandleWidth(4)
        layout.addWidget(splitter)
        self._config.plot_changed.connect(self.plot)
        self.setLayout(layout)

    def save_parameters(self):
        self._save_model(self._model)

    def plot(self):
        self._config.load()
        self._plot.reset_toolbar()
        self._plot.plot()


class PlotWidget(QtGui.QWidget):
    """This class handles all drawings to the plot canvas"""

    def __init__(self, model):
        """Initialises the drawing area in the plot node
        params:
            model: The IndexedPlotModel for all plots.
        """
        super(PlotWidget, self).__init__()
        self._model = model
        figure = Figure(
            facecolor=self.palette().color(QtGui.QPalette.Window).name())
        self._canvas = FigureCanvasQTAgg(figure)
        self._backend = backends.InteractiveBackend(model, figure)
        self._plot = QtGui.QPushButton('Refresh')
        self._toolbar = Toolbar(
            self._canvas, self._canvas, self._model, self._backend)
        self._skip_next_event = False
        self._currently_selected_line = None

        layout = QtGui.QVBoxLayout()
        groupbox = QtGui.QGroupBox()
        grouplayout = QtGui.QVBoxLayout()
        button_layout = QtGui.QHBoxLayout()
        button_layout.addWidget(self._plot)
        layout.addLayout(button_layout)
        grouplayout.addWidget(self._canvas)
        grouplayout.addWidget(self._toolbar)
        groupbox.setLayout(grouplayout)
        layout.addWidget(groupbox)
        grouplayout.setContentsMargins(1, 1, 1, 1)
        self.setLayout(layout)
        self._plot.clicked.connect(self.plot)
        figure.canvas.mpl_connect('pick_event', self._click_event)
        figure.canvas.mpl_connect('scroll_event', self._scroll_event)

    def plot(self):
        """Plots the entire graph from scratch"""
        index = self._model.get_index()
        if index is -1:
            return
        self._backend.render(None, index)
        self._canvas.draw()

    def reset_toolbar(self):
        """Disables all buttons and clears button states in toolbar"""
        self._toolbar.reset()

    def _plot_annotation(self):
        """Adds an annotation to the plot"""
        index = self._model.get_index()
        if index is -1:
            return
        self._backend.render_annotation(index)
        self._canvas.draw()

    def _plot_limits(self):
        """Adds a limit line to the plot"""
        index = self._model.get_index()
        if index is -1:
            return
        self._backend.render_limits(index)
        self._canvas.draw()

    def _select_limit(self, name, line):
        """Draws a thicker limit line to mark that it is selected.
        params:
            name: The name of the selected line.
            line: The Line2D plot line
        """
        index = self._model.get_index()
        if index is -1:
            return
        self._backend.select_limit(name, index, line)
        self._canvas.draw()

    def _deselect_limits(self, name):
        """Redraws the limit line so that it looks deselected.
        :param name: The name of the line to be deselected.
        """
        index = self._model.get_index()
        if index is -1:
            return
        self._backend.deselect_limits(name, index)
        self._canvas.draw()

    def _move_limit(self, direction):
        """Redraws the limit line according to mouse scroll.
        :param direction: 'up' or 'down' scroll direction.
        """
        index = self._model.get_index()
        if index is -1:
            return
        name = self._model.get_axes()[0].get_label()
        flipped = self._backend.move_limit(
            name, index, self._currently_selected_line, direction)
        if flipped:
            self._currently_selected_line = (
                'high' if self._currently_selected_line == 'low' else 'low')
        self._canvas.draw()

    def _click_event(self, event):
        """Handles mouse clicks on plot lines and axes to draw limit lines
        and annotations.
        :param event: The event that triggered this function.
        """
        if self._skip_next_event:
            self._skip_next_event = False
            return
        if self._model.show_selectors() is False:
            self._currently_selected_line = None

        label = self._model.get_axes()[0].get_label()
        if isinstance(event.artist, Line2D):
            if (self._model.show_selectors() and
               event.mouseevent.name == 'button_press_event'):
                line = event.artist.get_label()
                if line == self._currently_selected_line:
                    self._deselect_limits(label)
                    self._currently_selected_line = None
                else:
                    self._select_limit(label, line)
                    self._currently_selected_line = line
            if self._model.show_annotation():
                self._model.set_annotation_event(
                    event.mouseevent.x, event.mouseevent.y,
                    event.artist.get_label(), event.ind[len(event.ind) / 2])
                self._plot_annotation()

        elif isinstance(event.artist, Axes) and self._model.show_selectors():
                low_in, high_in = self._model.get_limits()
                low = None
                high = None
                if label in low_in:
                    low = low_in[label]
                if label in high_in:
                    high = high_in[label]

                if low is None or high is None:
                    self._model.set_limits(label, event.mouseevent.xdata)
                    self._plot_limits()
                    self._skip_next_event = True

    def _scroll_event(self, event):
        """Updates the selected limit line if the mouse wheel is scrolled
        :param event: The event that triggered this function.
        """
        if self._currently_selected_line:
            self._move_limit(event.button)


class IndexedPlotModel(object):
    def __init__(self, model):
        self._model = model
        self._index = 0

    def get_index(self):
            return self._index

    def get_title(self):
        return self._model.get_plots()[self._index].get_title()

    def get_show_legend(self):
        return self._model.get_plots()[self._index].get_show_legend()

    def get_show_statistics(self):
        return self._model.get_plots()[self._index].get_show_statistics()

    def get_statistics(self):
        return self._model.get_plots()[self._index].get_statistics()

    def get_statistics_signals(self):
        return self._model.get_plots()[self._index].get_statistics_signals()

    def get_axes(self):
        return self._model.get_plots()[self._index].get_axes()

    def get_signals(self):
        return self._model.get_plots()[self._index].get_signals()

    def get_signals_by_axis_x(self):
        return self._model.get_plots()[self._index].get_signals_by_axis_x()

    def get_table(self):
        return self._model.get_plots()[self._index].get_table()

    def get_limits_trigger(self):
        return self._model.get_plots()[self._index].get_limits_trigger()

    def set_show_statistics(self, show_statistics):
        plot = self._model.get_plots()[self._index]
        return plot.set_show_statistics(show_statistics)

    def set_statistics(self, statistics):
        return self._model.get_plots()[self._index].set_statistics(statistics)

    def set_statistics_signals(self, statistics_signals):
        plot = self._model.get_plots()[self._index]
        return plot.set_statistics_signals(statistics_signals)

    def set_index(self, index):
        self._index = index

    def set_title(self, title):
        return self._model.get_plots()[self._index].set_title(title)

    def set_show_legend(self, show_legend):
        return self._model.get_plots()[self._index].set_show_legend(
            show_legend)

    def set_axes(self, axes):
        return self._model.get_plots()[self._index].set_axes(axes)

    def set_signals(self, signals):
        return self._model.get_plots()[self._index].set_signals(signals)

    def set_label(self, label):
        return self._model.get_plots()[self._index].set_label(label)

    def add_axis(self, axis):
        return self._model.get_plots()[self._index].add_axis(axis)

    def add_signal(self, signal):
        return self._model.get_plots()[self._index].add_signal(signal)

    def remove_axis(self, axis):
        return self._model.get_plots()[self._index].remove_axis(axis)

    def remove_signal(self, signal):
        return self._model.get_plots()[self._index].remove_signal(signal)

    def get_plots(self):
        return self._model.get_plots()

    def set_plots(self, plots):
        return self._model.set_plots(plots)

    def add_plot(self, plot):
        self._model.add_plot(plot)

    def remove_plot(self, plot):
        self._model.remove_plot(plot)

    def set_annotation_event(self, x, y, signal_name, signal_index):
        self._model.get_plots()[self._index].set_annotation_event(
            x, y, signal_name, signal_index)

    def get_annotation_event(self):
        return self._model.get_plots()[self._index].get_annotation_event()

    def clear_annotation_event(self):
        self._model.get_plots()[self._index].clear_annotation_event()

    def toggle_annotation(self):
        self._model.get_plots()[self._index].toggle_annotation()

    def show_annotation(self):
        return self._model.get_plots()[self._index].show_annotation()

    def toggle_selectors(self):
        self._model.get_plots()[self._index].toggle_selectors()

    def show_selectors(self):
        return self._model.get_plots()[self._index].show_selectors()

    def set_limits(self, name, x):
        self._model.get_plots()[self._index].set_limits(name, x)

    def clear_limits(self):
        self._model.get_plots()[self._index].clear_limits()

    def get_limits(self):
        return self._model.get_plots()[self._index].get_limits()


class FilteredComboBox(QtGui.QComboBox):
    def __init__(self, parent=None):
        super(FilteredComboBox, self).__init__(parent)

        self.setEditable(True)

        self._filter_model = QtGui.QSortFilterProxyModel(self)
        self._filter_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._filter_model.setSourceModel(self.model())

        self._completer = QtGui.QCompleter(self._filter_model, self)
        self._completer.setCompletionMode(
            QtGui.QCompleter.UnfilteredPopupCompletion)
        self.setCompleter(self._completer)

        self.lineEdit().textEdited[six.text_type].connect(
            self.lineedit_changed)

        self._completer.activated.connect(self._filter_result_selected)

    def setModel(self, model):  # noqa
        super(FilteredComboBox, self).setModel(model)
        self._filter_model.setSourceModel(model)
        self._completer.setModel(self._filter_model)

    def addItems(self, items):  # noqa
        super(FilteredComboBox, self).addItems(items)
        self._filter_model.setSourceModel(self.model())
        self._completer.setModel(self._filter_model)

    def addItem(self, item): # noqa
        super(FilteredComboBox, self).addItem(item)
        self._filter_model.setSourceModel(self.model())
        self._completer.setModel(self._filter_model)

    def lineedit_changed(self, text):
        self._filter_model.setFilterFixedString(text)

    def _filter_result_selected(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)
            self.activated[str].emit(self.itemText(index))


class Toolbar(NavigationToolbar2QT):
    """Customized toolbar widget"""

    def __init__(self, canvas, parent, model, backend):
        """Initialises the toolbar.
        params:
            canvas: The canvas that will be drawn upon.
            parent: The calling object.
            model: The model object that holds the state.
            backend: Object that does the heavyweigth calculations.
        :return: The toolbar.
        """
        NavigationToolbar2QT.__init__(self, canvas, parent)
        self._model = model
        self._backend = backend
        self._canvas = canvas

        self._home = NavigationToolbar2QT.home
        self._back = NavigationToolbar2QT.back
        self._forward = NavigationToolbar2QT.forward
        self._pan = NavigationToolbar2QT.pan
        self._zoom = NavigationToolbar2QT.zoom

        NavigationToolbar2QT.home = self.home
        NavigationToolbar2QT.back = self.back
        NavigationToolbar2QT.forward = self.forward
        NavigationToolbar2QT.pan = self.pan
        NavigationToolbar2QT.zoom = self.zoom

        self._pan_clicked = False
        self._zoom_clicked = False

        # Hack to remove unsupported file formats
        file_types = self.canvas.get_supported_filetypes()
        delete = []
        for file_type in file_types:
            if file_type not in ['svg', 'pdf', 'eps', 'png']:
                delete.append(file_type)
        for item in delete:
            del file_types[item]

        # Remove unnecessary buttons
        self.layout().takeAt(10)
        self.layout().takeAt(9)
        self.layout().takeAt(7)
        self.layout().takeAt(3)

        self.addSeparator()

        # Show signal values in plot
        self.values = QtGui.QToolButton()
        icon = QtGui.QStyle.SP_MessageBoxInformation
        self.values.setIcon(self.style().standardIcon(icon))
        self.values.setToolTip('Show signal values in clicked location')
        self.values.setCheckable(True)
        self.addWidget(self.values)
        self.values.clicked.connect(self.toggle_annotation)

        # Selector lines
        self.selector = QtGui.QToolButton()
        icon = QtGui.QStyle.SP_MediaPause
        self.selector.setIcon(self.style().standardIcon(icon))
        self.selector.setToolTip('Select interval')
        self.selector.setCheckable(True)
        self.addWidget(self.selector)
        self.selector.clicked.connect(self.toggle_selectors)

    def home(self):
        """"Overload of the standard home button"""
        self._overload_button(self._home)

    def back(self):
        """"Overload of the standard back button"""
        self._overload_button(self._back)

    def forward(self):
        """"Overload of the standard forward button"""
        self._overload_button(self._forward)

    def pan(self):
        """"Overload of the standard pan button"""
        self._pan_clicked = not self._pan_clicked
        if self._zoom_clicked:
            self._zoom_clicked = False
        self._overload_button(self._pan)

    def zoom(self):
        """"Overload of the standard zoom button"""
        self._zoom_clicked = not self._zoom_clicked
        if self._pan_clicked:
            self._pan_clicked = False
        self._overload_button(self._zoom)

    def _overload_button(self, func):
        """Makes sure that annotations no longer are possible.
        params:
            func: Standard toolbar function.
        """
        if self.values.isChecked():
            self.values.setChecked(False)
            self.toggle_annotation()
        func(self)

    def toggle_annotation(self):
        """Toggles annotation and clears the model if neccessary."""
        self._model.toggle_annotation()
        if self.values.isChecked() is False:
            self._backend.clear_annotation()
            self._model.clear_annotation_event()
            self._canvas.draw()
        else:
            self._disable_buttons()

    def toggle_selectors(self):
        """Toggles interval lines and clears the model if neccessary."""
        self._model.toggle_selectors()
        if self.selector.isChecked() is False:
            self._model.clear_limits()
            self._backend.clear_limits()
            self._canvas.draw()
        else:
            self._disable_buttons()

    def _disable_buttons(self):
        """Unclicks pan and zoom button if they are pressed."""
        if self._pan_clicked:
            self._pan_clicked = False
            self._pan(self)
        if self._zoom_clicked:
            self._zoom_clicked = False
            self._zoom(self)

    def reset(self):
        """Resets the toolbar to it osrignial unclicked state."""
        self._disable_buttons()
        if self.selector.isChecked():
            self._model.clear_limits()
            self._backend.clear_limits()
            self.selector.setChecked(False)
        if self.values.isChecked():
            self._backend.clear_annotation()
            self._model.clear_annotation_event()
            self.values.setChecked(False)
