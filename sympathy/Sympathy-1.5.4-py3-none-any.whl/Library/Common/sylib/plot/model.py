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
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import uuid
import itertools
import math
import json
import datetime
import numpy as np
import six
import matplotlib.dates as dates
from collections import OrderedDict
from sympathy.api import table as sytable
from matplotlib.colors import ColorConverter
from sympathy.api import qt as qt_compat
from PySide.QtCore import Signal
from sylib.util import mock_wrap
QtCore = qt_compat.QtCore


grid_options = ['major', 'minor', 'both', 'nothing']


marker_styles = {'circle': 'o',
                 'diamond': 'D',
                 'nothing': '',
                 'plus': '+',
                 'point': '.',
                 'square': 's',
                 'star': '*',
                 'triangle': '^'}


line_styles = {'dash-dotted': '-.',
               'dashed': '--',
               'dotted': ':',
               'nothing': '',
               'solid': '-'}


class Array(object):
    pass


class Series(object):
    pass


class Object(object):
    pass


class Axis(object):
    pass


class String(object):
    pass


class RGBString(object):
    pass


class RGBTuple(object):
    pass


class RGBATuple(object):
    pass


def object_or_none(value):
    try:
        return eval(value)
    except:
        return None


def float_or_none(value):
    try:
        return float(value)
    except ValueError:
        return None


def in_float(value):
    if value is None:
        return True
    return False


def type_or_none(classes):
    def inner(self, value):
        try:
            evaluated = eval(value)
        except:
            evaluated = None

        for item in classes:
            if isinstance(evaluated, item):
                return True
        return False
    return inner


def in_types(classes):
    def inner(self, value):
        for item in classes:
            if isinstance(value, item):
                return True
        return False
    return inner


def eval_or_none(value):
    try:
        return eval(value)
    except:
        return None


def color_or_none(value):
    try:
        return ColorConverter().to_rgba(value)
    except ValueError:
        return None


def string_or_repr(value):
    if value is None:
        return ''
    elif isinstance(value, six.string_types):
        return value
    return repr(value)


def color_format(color, format):
    if color == '':
        return None
    if format == Object:
        return color
    if format == RGBString:
        color = ColorConverter().to_rgb(color)
        return '#{}{}{}'.format(*[
            '{:02x}'.format(int(math.ceil(val * 255)))
            for val in ColorConverter().to_rgb(color)])
    elif format == RGBTuple:
        return ColorConverter().to_rgb(color)
    elif format == RGBATuple:
        return ColorConverter().to_rgba(color)


def encode_item(item, encoding='utf8'):
    def encode(item):
        if isinstance(item, dict):
            return OrderedDict(
                (encode(key),
                 encode(value)) for key, value in six.iteritems(item))
        elif isinstance(item, list):
            return [encode(value) for value in item]
        elif isinstance(item, six.text_type):
            if six.PY2:
                return item.encode(encoding)
            return item
        else:
            return item
    return encode(item)


def decode_item(item, encoding='utf8'):
    def encode(item):
        if isinstance(item, dict):
            return OrderedDict(
                (encode(key),
                 encode(value)) for key, value in six.iteritems(item))
        elif isinstance(item, list):
            return [encode(value) for value in item]
        elif isinstance(item, six.binary_type):
            return item.decode(encoding)
        else:
            return item
    return encode(item)


def get_plots_model(table):
    attributes = table.get_table_attributes()
    if 'plots model' in attributes:
        plots_model = PlotsModel(
            table=table, dict_attr='plots model')
    else:
        plots_model = PlotsModel(table=table)
        plots_model.set_plots([])
    return plots_model


def _get_color_field(data, field, format):
    value = data[field]
    if value == '':
        return None
    return color_format(object_or_none(value), format)


def _set_float_field(data, field, value):
    if isinstance(value, float) or isinstance(value, int):
        data[field] = repr(float(value))
        return True
    elif value is None:
        data[field] = ''
        return True
    return False


def _set_color_field(data, field, value):
    if value is None:
        data[field] = ''
        return True
    color = color_or_none(value)
    if color is not None:
        data[field] = repr(color)
        return True
    return False


class LineModel(object):
    line_styles = list(line_styles.keys())

    def __init__(self, dict_arg=None):
        if dict_arg is None:
            self.__data = {'Style': 'solid',
                           'Width': '',
                           'Color': ''}
        else:
            self.__data = dict_arg

    def to_dict(self):
        return self.__data

    @classmethod
    def from_dict(cls, dict_arg):
        return cls(dict_arg)

    def get_style(self):
        return self.__data['Style'] or None

    def get_width(self):
        return float_or_none(self.__data['Width'])

    def get_color(self, format=Object):
        return _get_color_field(self.__data, 'Color', format)

    def set_style(self, style):
        self.__data['Style'] = style

    def set_width(self, value):
        return _set_float_field(self.__data, 'Width', value)

    def set_color(self, value):
        return _set_color_field(self.__data, 'Color', value)


class MarkerModel(object):
    marker_styles = list(marker_styles.keys())

    def __init__(self, dict_arg=None):
        if dict_arg is None:
            self.__data = {'Style': 'nothing',
                           'Size': '',
                           'Edge width': '',
                           'Face color': '',
                           'Edge color': ''}
        else:
            self.__data = dict_arg

    def to_dict(self):
        return self.__data

    @classmethod
    def from_dict(cls, dict_arg):
        return cls(dict_arg)

    def get_style(self):
        return self.__data['Style'] or None

    def get_size(self):
        return float_or_none(self.__data['Size'])

    def get_edgewidth(self):
        return float_or_none(self.__data['Edge width'])

    def get_facecolor(self, format=Object):
        return _get_color_field(self.__data, 'Face color', format)

    def get_edgecolor(self, format=Object):
        return _get_color_field(self.__data, 'Edge color', format)

    def set_style(self, style):
        self.__data['Style'] = style

    def set_size(self, value):
        return _set_float_field(self.__data, 'Size', value)

    def set_edgewidth(self, value):
        return _set_float_field(self.__data, 'Edge width', value)

    def set_facecolor(self, value):
        return _set_color_field(self.__data, 'Face color', value)

    def set_edgecolor(self, value):
        return _set_color_field(self.__data, 'Edge color', value)


class SignalModel(object):
    def __init__(self, plot_model, dict_arg=None, label=None):
        self._model = plot_model
        if dict_arg is None:
            self.__data = {
                'Label': label or '',
                'Data': ['', ''],
                'Axis': ['X', 'Y'],
                'Line': LineModel().to_dict(),
                'Marker': MarkerModel().to_dict()
            }
        else:
            self.__data = dict_arg
            assert(label is None)
        self.__line = LineModel(self.__data['Line'])
        self.__marker = MarkerModel(self.__data['Marker'])

    def to_dict(self):
        self.__data['Line'] = self.__line.to_dict()
        self.__data['Marker'] = self.__marker.to_dict()
        return self.__data

    @classmethod
    def from_dict(cls, dict_arg):
        return cls(dict_arg)

    def get_label(self):
        return self.__data['Label']

    def _get_data_column(self, column, format):
        try:
            if format == String:
                return column
            elif format == Array:
                return self._model.get_table().get_column_to_array(column)
            elif format == Series:
                return self._model.get_table().get_column_to_series(column)
        except KeyError:
            return None

    def get_data(self):
        return list(self.__data['Data'])

    def calc_indexes(self):
        """Calculates the array index for the selectors.
        return:
            low: the low index
            high: the high index.
        """
        low, high = self._model.get_limits()
        label = self.get_axis_x()
        x = self.get_data_x(Array)
        if (low == {} or high == {} or label not in low or
                label not in high or x is None):
            return 0, len(x) - 1

        low = low[label]
        high = high[label]
        if isinstance(x[0], np.datetime64):
            low = np.datetime64(dates.num2date(low))
            high = np.datetime64(dates.num2date(high))

        try:
            return np.where(x > low)[0][0], np.where(x < high)[0][-1]
        except:
            return None, None

    def get_data_x(self, format=String):
        return self._get_data_column(self.get_data()[0], format)

    def get_x_limits(self, format=Array):
        """Returns the x values at the selector limits.
        params:
            format: The wanted format (Array, String).
        return:
            low: low x limit.
            high: high x limit.
        """
        x = self.get_data_x(format)
        if x is not None:
            low, high = self.calc_indexes()
            if low is not None and high is not None:
                return x[low], x[high]
            else:
                return ('Config error',
                        'Do you have multiple signals on the X axis?')
        else:
            return ('Column names have changed, check signal configuration',
                    'Then save and restart this node')

    def get_std_y(self, format=Array):
        """Calculates the std of the y values between the given indexes.
        params:
            format: The wanted format (Array, String).
        return:
            std: The standard deviation.
        """
        try:
            yy = self.get_data_y(format)
            low, high = self.calc_indexes()
            yy = yy[low:high + 1]
            y = [float(e) for e in yy]
        except:
            y = []
        if len(y) == 0:
            return "-"
        a = np.array(y)
        return round(np.std(a, dtype=np.float), 2)

    def get_mean_y(self, format=Array):
        """Calculates the mean of the y values between the given indexes.
        params:
            format: The wanted format (Array, String).
        return:
            mean: The standard deviation.
        """
        try:
            yy = self.get_data_y(format)
            low, high = self.calc_indexes()
            yy = yy[low:high + 1]
            y = [float(e) for e in yy]
        except:
            y = []
        if len(y) == 0:
            return "-"
        mean = sum(y) / len(y)
        return round(mean, 2)

    def get_max_y(self, format=Array):
        """Calculates the max of the y values between the given indexes.
        params:
            format: The wanted format (Array, String).
        return:
            max: The standard deviation.
        """
        try:
            yy = self.get_data_y(format)
            low, high = self.calc_indexes()
            yy = yy[low:high + 1]
            y = [float(e) for e in yy]
        except:
            y = []
        if len(y) == 0:
            return "-"
        return round(max(y), 2)

    def get_min_y(self, format=Array):
        """Calculates the min of the y values between the given indexes.
        params:
            format: The wanted format (Array, String).
        return:
            min: The standard deviation.
        """
        try:
            yy = self.get_data_y(format)
            low, high = self.calc_indexes()
            yy = yy[low:high + 1]
            y = [float(e) for e in yy]
        except:
            y = []
        if len(y) == 0:
            return "-"
        return round(min(y), 2)

    def get_data_y(self, format=String):
        return self._get_data_column(self.get_data()[1], format)

    def _get_axis_axis(self, label, format):
        if format == String:
            return label
        elif format == Axis:
            return six.next(
                axis for axis in self._model.get_axes()
                if axis.get_label() == label)

    def get_axis(self):
        return list(self.__data['Axis'])

    def get_axis_x(self, format=String):
        return self._get_axis_axis(self.get_axis()[0], format)

    def get_axis_y(self, format=String):
        return self._get_axis_axis(self.get_axis()[1], format)

    def get_line(self):
        return self.__line

    def get_marker(self):
        return self.__marker

    def set_label(self, label):
        self.__data['Label'] = label

    def set_data(self, data):
        self.__data['Data'] = list(data)

    def set_data_x(self, data):
        self.__data['Data'][0] = data

    def set_data_y(self, data):
        self.__data['Data'][1] = data

    def set_axis_x(self, axis):
        self.__data['Axis'][0] = axis

    def set_axis_y(self, axis):
        self.__data['Axis'][1] = axis

    def set_axis(self, axis):
        self.__data['Axis'] = list(axis)

    def set_line(self, line):
        self.__line = line

    def set_marker(self, marker):
        self.__marker = marker


class AxisModel(object):
    _in_ticks = in_types(
        [int, float, datetime.timedelta])
    _in_limits = in_types(
        [int, float, datetime.datetime, datetime.date])

    def __init__(self, plot_model, dict_arg=None, label=None):
        self._model = plot_model
        if dict_arg is None:
            self.__data = {
                'Id': six.text_type(uuid.uuid4()),
                'Label': label or 'New axis 0',
                'Scale': 'linear',
                'Limits': ['', ''],
                'Ticks': ['', ''],
                'Grid': 'nothing'}
        else:
            self.__data = dict_arg

    def to_dict(self):
        return self.__data

    @classmethod
    def from_dict(cls, dict_arg):
        return cls(dict_arg)

    def get_label(self):
        return self.__data['Label']

    def get_scale(self):
        return self.__data['Scale']

    def get_limits(self):
        return [self.get_limits_min(), self.get_limits_max()]

    def get_limits_min(self):
        return eval_or_none(self.__data['Limits'][0])

    def get_limits_max(self):
        return eval_or_none(self.__data['Limits'][1])

    def get_ticks(self):
        return [self.get_ticks_minor(), self.get_ticks_major()]

    def get_ticks_minor(self):
        return eval_or_none(self.__data['Ticks'][0])

    def get_ticks_major(self, format=Object):
        return eval_or_none(self.__data['Ticks'][1])

    def get_grid(self):
        return self.__data['Grid']

    def set_label(self, label):
        old_label = self.get_label()
        for signal in self._model.get_signals():
            new = [label if value == old_label else value
                   for value in signal.get_axis()]
            signal.set_axis(new)
        self.__data['Label'] = label

    def set_scale(self, scale):
        self.__data['Scale'] = scale

    def set_limits(self, limits):
        self.set_limits_min(limits[0])
        self.set_limits_max(limits[1])

    def set_limits_min(self, value):
        if self._in_limits(value):
            self.__data['Limits'][0] = repr(value)
            return True
        elif value is None:
            self.__data['Limits'][0] = ''
            return True

    def set_limits_max(self, value):
        if self._in_limits(value):
            self.__data['Limits'][1] = repr(value)
            return True
        elif value is None:
            self.__data['Limits'][1] = ''
            return True

    def set_ticks(self, ticks):
        self.set_ticks_minor(ticks[0])
        self.set_ticks_major(ticks[1])

    def set_ticks_minor(self, value):
        if self._in_ticks(value):
            self.__data['Ticks'][0] = repr(value)
            return True
        elif value is None:
            self.__data['Ticks'][0] = ''
            return True

    def set_ticks_major(self, value):
        if self._in_ticks(value):
            self.__data['Ticks'][1] = repr(value)
            return True
        elif value is None:
            self.__data['Ticks'][1] = ''
            return True

    def set_grid(self, grid):
        self.__data['Grid'] = grid


@mock_wrap
class PlotModel(QtCore.QObject):
    _limit_trigger = Signal()

    def __init__(self, dict_arg=None, table=None):
        QtCore.QObject.__init__(self)
        if dict_arg is None:
            self.__data = {
                'Title': '',
                'Show statistics': False,
                'Statistics': [],
                'Statistics_signals': [],
                'Show annotation': False,
                'Show selectors': False,
                'Limit low': {},
                'Limit high': {},
                'Limits index factor': (None, None),
                'Axes': [
                    AxisModel(self, None, 'X').to_dict(),
                    AxisModel(self, None, 'Y').to_dict()
                ],
                'Signals': [
                    SignalModel(self, None, 'New signal 0').to_dict()
                ],
                'Show legend': True
            }
        else:
            self.__data = dict_arg

        if table is None:
            self.__table = sytable.File()
        else:
            self.__table = table

        self.__axes = [AxisModel(self, axis) for axis in self.__data['Axes']]
        self.__signals = [SignalModel(self, signal)
                          for signal in self.__data['Signals']]
        self.__axis_lookup = None
        self.__signal_lookup = None
        self.__annotation_events = []
        self.clear_limits()
        try:
            self.show_annotation()
            self.show_selectors()
        except:
            self.__data['Show annotation'] = False
            self.__data['Show selectors'] = False
        try:
            self.get_statistics_signals()
            self.get_statistics()
            self.get_show_statistics()
        except:
            self.set_statistics_signals([])
            self.set_statistics([])
            self.set_show_statistics(False)

    def to_dict(self):
        self.__data['Axes'] = [axis.to_dict() for axis in self.__axes]
        self.__data['Signals'] = [signal.to_dict()
                                  for signal in self.__signals]
        return self.__data

    @classmethod
    def from_dict(cls, dict_arg):
        return cls(dict_arg)

    def get_title(self):
        return self.__data['Title']

    def get_show_legend(self):
        return self.__data['Show legend']

    def get_show_statistics(self):
        """True if statistics should be showed in plot, False otherwise."""
        return self.__data['Show statistics']

    def get_statistics(self):
        """Returns the statistic attributes that should be showed in plot
        statistics table.
        returns:
            attributes: The statistics attributes.
        """
        return self.__data['Statistics']

    def get_statistics_signals(self):
        """Returns the signals should be shown in plot statistics table.
        returns:
            signals: The signals that should be shown.
        """
        return self.__data['Statistics_signals']

    def get_axes(self):
        return list(self.__axes)

    def get_signals(self):
        return list(self.__signals)

    def get_signals_by_axis_x(self):
        signals_by_axis_x = sorted(
            self.get_signals(), key=lambda x: x.get_axis_x())
        groups = []
        for key, value in itertools.groupby(
                signals_by_axis_x, lambda x: x.get_axis_x()):
            groups.append(list(value))
        return groups

    def get_table(self):
        return self.__table

    def set_title(self, title):
        self.__data['Title'] = title

    def set_show_legend(self, show_legend):
        self.__data['Show legend'] = show_legend

    def set_show_statistics(self, show_statistics):
        """Set if statistics should be shown in plot.
        params:
            show_statistics: True or False.
        """
        self.__data['Show statistics'] = show_statistics

    def set_statistics(self, statistics):
        """Sets which statistic attributes should be showed in plot
        statistics table.
        params:
            statistics: The attributes.
        """
        self.__data['Statistics'] = statistics

    def set_statistics_signals(self, statistics_signals):
        """Sets which signals should be showed in plot statistics table."""
        self.__data['Statistics_signals'] = statistics_signals

    def set_axes(self, axes):
        self.__axes = list(axes)

    def set_signals(self, signals):
        self.__signals = list(signals)

    def set_label(self, label):
        self.__data['Label'] = label

    def add_axis(self, axis):
        label = axis.get_label()
        for _axis in self.__axes:
            if _axis.get_label() == label:
                raise KeyError
        self.__axes.append(axis)

    def add_signal(self, signal):
        label = signal.get_label()
        for _signal in self.__signals:
            if _signal.get_label() == label:
                raise KeyError
        self.__signals.append(signal)

    def remove_axis(self, axis):
        if len(self.__axes) <= 2:
            raise ValueError()
        label = axis.get_label()
        for i, axis in enumerate(self.__axes):
            if axis.get_label() == label:
                del self.__axes[i]
                return
        raise KeyError

    def remove_signal(self, signal):
        if len(self.__signals) <= 1:
            raise ValueError()
        label = signal.get_label()
        for i, signal in enumerate(self.__signals):
            if signal.get_label() == label:
                del self.__signals[i]
                return
        raise KeyError

    def set_annotation_event(self, x, y, signal_name, signal_index):
        """Saves the event and deletes the former events if the position
        of the event has changed. Otherwise keeps the old events
        (same click). Does not add duplicates
        params:
            x: The X position.
            y: The Y position.
            signal_name: The signal name.
            signal_index: The array index of the clicked value.
        """
        if(self.__annotation_events and
           self.__annotation_events[0][0] != x and
           self.__annotation_events[0][1] != y):
            del self.__annotation_events[:]
        add_event = True
        for event in self.__annotation_events:
            if event[2] == signal_name:
                add_event = False
                break
        if add_event:
            self.__annotation_events.append((x, y, signal_name, signal_index))

    def get_annotation_event(self):
        """Returns the gathered annotation event(s)
        returns:
            annotation_event: List of gathered events.
        """
        return self.__annotation_events

    def clear_annotation_event(self):
        """Removes the current annotaiton event"""
        del self.__annotation_events[:]
        self.__annotation_events = []

    def toggle_annotation(self):
        """Toggles the current state of the annotation"""
        self.__data['Show annotation'] = not self.__data['Show annotation']

    def show_annotation(self):
        """Returns state of the annotation.
        returns:
            state: True if the annotation should be shown, False otherwise.
        """
        return self.__data['Show annotation']

    def toggle_selectors(self):
        """Toggles the current state of the selectors"""
        self.clear_limits()
        self.__data['Show selectors'] = not self.__data['Show selectors']

    def show_selectors(self):
        """Returns the state of the intervall lines.
        returns:
            state: True if the selectors should be shown, False otherwise.
        """
        return self.__data['Show selectors']

    def set_limits(self, name, x):
        """Sets upper and/or lower limit.
        params:
            name: axis name.
            x: axis position.
        """
        if ('Limits low' not in self.__data) or(self.__data['Limits low']
                                                is None):
            self.__data['Limits low'] = {name: x}
        else:
            if name not in self.__data['Limits low']:
                self.__data['Limits low'][name] = x
            else:
                if 'Limits high' not in self.__data:
                    self.__data['Limits high'] = {name: x}
                elif name not in self.__data['Limits high']:
                    if x > self.__data['Limits low'][name]:
                        self.__data['Limits high'][name] = x
                    else:
                        self.__data['Limits high'][name] = (
                            self.__data['Limits low'][name])
                        self.__data['Limits low'][name] = x
        self._limit_trigger.emit()

    def set_explicit_limits(self, name, low, high):
        """Directly sets the limits. Used when moving the limits.
        params:
            name: axis name.
            low: low x position.
            high: high x position.
        """
        self.__data['Limits low'] = {name: low}
        self.__data['Limits high'] = {name: high}
        self._limit_trigger.emit()

    def clear_limits(self):
        """Removes the selector limits"""
        self.__data['Limits low'] = {}
        self.__data['Limits high'] = {}

    def get_limits(self):
        """Returns the selector limits
        return:
            low: lower limit.
            high: higher limit.
        """
        return self.__data['Limits low'], self.__data['Limits high']

    def get_limits_trigger(self):
        """Returns the trigger so that the GUI can know when to update
        returns:
            trigger: The trigger.
        """
        return self._limit_trigger


class PlotsModel(object):
    def __init__(self, dict_arg=None, table=None, dict_attr=None):
        if dict_arg is None:
            self.__data = {
                'Plots': [PlotModel(dict_arg, table).to_dict()]
            }
        else:
            self.__data = dict_arg

        if table is not None and dict_attr:
            self.__data = decode_item(
                json.loads(table.get_table_attributes()[dict_attr],
                           object_pairs_hook=OrderedDict))
        if table is None:
            self.__table = sytable.File()
        else:
            self.__table = table

        self.__plots = [PlotModel(plot, table)
                        for plot in self.__data['Plots']]

    def to_dict(self):
        self.__data['Plots'] = [plot.to_dict() for plot in self.__plots]
        return self.__data

    @classmethod
    def from_dict(cls, dict_arg):
        return cls(dict_arg)

    def write_table_attribute(self):
        assert(self.__table is not None)
        attributes = self.__table.get_table_attributes() or {}
        attributes['plots model'] = json.dumps(encode_item(self.to_dict()))
        self.__table.set_table_attributes(attributes)

    def get_table(self):
        return self.__table

    def get_plots(self):
        return list(self.__plots)

    def set_table(self, table):
        self.__table = table

    def set_plots(self, plots):
        self.__plots = list(plots)

    def add_plot(self, plot):
        self.__plots.append(plot)

    def remove_plot(self, plot):
        if len(self.__plots) <= 1:
            raise ValueError()
        for i, current in enumerate(self.__plots):
            if plot == current:
                del self.__plots[i]
                return
        raise KeyError
