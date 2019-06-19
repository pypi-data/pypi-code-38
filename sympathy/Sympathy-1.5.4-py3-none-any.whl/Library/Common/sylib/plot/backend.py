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
import math
import datetime
import warnings
import re
import unicodedata
from collections import OrderedDict
import six
import numpy as np
import pandas as pd
from mpl_toolkits.axes_grid1 import parasite_axes
from mpl_toolkits import axisartist as aa
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.font_manager import FontProperties

from sympathy.api import exceptions

from . import model as models


class Backend(object):
    def __init__(self, model):
        self._model = model

    def render(self, filename):
        raise NotImplemented


def filter_none(dictionary):
    return {key: value for key, value in dictionary.items()
            if value is not None}


def format_value(value):
    """Looks for datetime and formats properly if found.
    params:
        value: The value to format.
    """
    if isinstance(value, np.datetime64):
        return pd.to_datetime(value).strftime('%c')
    if isinstance(value, np.timedelta64):
        micro = value.astype('int64')
        seconds, micro = divmod(micro, 1000000)
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        if days:
            return '%d days, %02d:%02d:%02d' % (days, hours, minutes, seconds)
        else:
            return '%02d:%02d:%02d:%06d' % (hours, minutes, seconds, micro)
    return str(value)


def col2ai(i):
    """
    Return corresponding A, B, .. AB notation for column number i.
    """
    chars = []
    c = i % 26
    chars.append(c)
    i = (i - c) // 26

    while i > 0:
        c = (i - 1) % 26
        chars.append(c)
        i = (i - c) // 26

    return ''.join([chr(ord('A') + c_) for c_ in reversed(chars)])


def range_name(column_name):
    """
    Convert column name to valid name for use in workbook named range.
    crng_ + converted compatible name.
    """
    if isinstance(column_name, six.binary_type):
        column_name = column_name.decode('ascii', errors='ignore')
    return u'crng_{}'.format(
        re.sub('[^a-zA-Z0-9]', '_', unicodedata.normalize('NFD', column_name)))


class InteractiveBackend(Backend):
    def __init__(self, model, figure):
        super(InteractiveBackend, self).__init__(model)
        self._figure = figure
        self._annotation = None
        self._axis = None
        self._axis_span = None
        self._high_lim = None
        self._low_lim = None
        self.signal_length = 0
        self.value_len = 0
        self._limits_annotation = None

    def clear(self):
        """Clears the figure."""
        self._figure.clf()

    def set_ticks(self, axis, start, stop, step, minor):
        """Sets ticks from start to stop with stepsize step on the axis.
        params:
            axis: is a Axis instance on which the ticks should be set.
            start: is the limit_min.
            stop: is the limit_max,
            minor: True if minor ticks should be set, False if major ticks.
        """
        if step:
            if isinstance(step, datetime.timedelta):
                stop_date = mdates.num2date(stop)
                start_date = mdates.num2date(start)
                range_seconds = (stop_date - start_date).total_seconds()
                step_seconds = step.total_seconds()
                nr_intervals = int(math.ceil(
                    float(range_seconds) / float(step_seconds)))
                ticks = [mdates.date2num(start_date + x * step)
                         for x in six.moves.range(nr_intervals)]
            else:
                step = float(step)
                ticks = np.arange(
                    math.ceil(start / step) * step, stop + step, step)
            if ticks[-1] > stop:
                ticks = ticks[:-1]
            if minor:
                major_ticks = set(axis.get_majorticklocs())
                minor_ticks = set(ticks)
                ticks = sorted(minor_ticks.difference(major_ticks))
            axis.set_ticks(ticks, minor)

    def fill_label_table(self, signal, label, group):
        """Fills the table to be appended to the plot legend with statistic
        information about the specified signal.
        params:
            signal: The signal of interest.
            label: the label we should append to.
            group: the Plotmodel that we are currently handling.
        return:
            label: the updated label.
        """
        for stat in group.get_statistics():
            if stat == "Std":
                value = str(signal.get_std_y())
            elif stat == "Mean":
                value = str(signal.get_mean_y())
            elif stat == "Min":
                value = str(signal.get_min_y())
            elif stat == "Max":
                value = str(signal.get_max_y())
            diff = self.value_len - len(value)
            padded = self.padd_string(value, diff, False)
            label = label + self.padd_string(padded, 4, True)
        return label

    def handle_x_axis(self, axis_model_x, host, xaxis_datetime):
        """Configures the X axis
        params:
            axis_model_x: the X axis.
            host: the subplot axes.
            xaxis_datetime: True if datetime should be used on X axis,
                            false otherwise.
        """
        label_x = axis_model_x.get_label()
        limit_min_x, limit_max_x = axis_model_x.get_limits()
        ticks_minor_x, ticks_major_x = axis_model_x.get_ticks()

        host.set_xlabel(label_x)
        host.set_xlim(limit_min_x, limit_max_x)

        if axis_model_x.get_scale() == 'linear':
            if xaxis_datetime:
                host.xaxis_date()
                self._figure.autofmt_xdate()
                host.axis['bottom'].major_ticklabels.set_rotation(60)
                host.axis['bottom'].major_ticklabels.set_pad(20)
                host.axis['bottom'].label.set_pad(30)
            else:
                host.set_xscale(axis_model_x.get_scale())
        else:
            host.set_xscale(axis_model_x.get_scale())

        axis_grid = axis_model_x.get_grid()
        if axis_grid == 'minor':
            host.grid(True, 'minor')
        elif axis_grid == 'major':
            host.grid(True, 'major')
        elif axis_grid == 'both':
            host.grid(True, 'both')

        else:
            pass

        limit_min_x, limit_max_x = host.get_xlim()
        self.set_ticks(host.xaxis, limit_min_x, limit_max_x,
                       ticks_major_x, False)
        self.set_ticks(host.xaxis, limit_min_x, limit_max_x,
                       ticks_minor_x, True)

    def handle_y_axis(self, axis_model_y, ax, yaxis_datetime):
        """Configures the Y axis
        params:
            axis_model_y: the Y axis.
            ax: the subplot axes.
            yaxis_datetime: True if datetime should be used on Y Axis,
                            false otherwise.
        """
        ax.set_ylabel(axis_model_y.get_label())
        if axis_model_y.get_scale() == 'linear':
            if yaxis_datetime:
                # To solve in the future, a secondary y-axis ruins
                # the datetime ticklabels, which become floats.
                ax.yaxis_date()
            else:
                ax.set_yscale(axis_model_y.get_scale())
        else:
            ax.set_yscale(axis_model_y.get_scale())

        axis_grid = axis_model_y.get_grid()
        if axis_grid == 'minor':
            ax.grid(True, 'minor')
        elif axis_grid == 'major':
            ax.grid(True, 'major')
        elif axis_grid == 'both':
            ax.grid(True, 'both')
        else:
            pass
        limit_min, limit_max = axis_model_y.get_limits()
        ax.set_ylim(limit_min, limit_max)

        limit_min_y, limit_max_y = ax.get_ylim()
        ticks_minor_y, ticks_major_y = axis_model_y.get_ticks()
        self.set_ticks(ax.yaxis, limit_min_y, limit_max_y,
                       ticks_major_y, False)
        self.set_ticks(ax.yaxis, limit_min_y, limit_max_y,
                       ticks_minor_y, True)

    def config_plot(
            self, host, group, axis_lookup_y, xaxis_datetime, legend, artists):
        """Configures the plot by adding legend.
        params:
            host: the subplot axes.
            group: the Plotmodel that we are currently handling.
            axis_lookup_y: List of all y axes.
            xaxis_datetime: True if datetime should be used on X axis,
                            false otherwise.
        """
        legend_rows = 0
        legend_cols = 0
        if group.get_show_legend():
            legend_cols = 2
            legend_rows = len(group.get_signals()) / 2
            if len(group.get_signals()) % legend_cols > 0:
                legend_rows += 1

        if group.get_show_statistics():
            legend_cols = 1
            legend_rows = len(group.get_statistics_signals()) + 1

        if group.get_show_statistics() and group.get_show_legend():
            legend_rows = len(group.get_signals()) + 1

        height_factor = 0.05 + legend_rows * 0.08
        legend_borderaxespad = 3.5

        if xaxis_datetime:
            height_factor = 0.10 + legend_rows * 0.05
            legend_borderaxespad = 8

        if not group.get_show_legend() and not group.get_show_statistics():
            height_factor = 0
            legend_borderaxespad = 0

        width_factor = 0
        nr_axes = len(axis_lookup_y)
        anchor = (0.5, 0)
        if nr_axes > 3:
            width_factor = 0.12 * (nr_axes - 2)
            host.axis['bottom'].major_ticklabels.set_rotation(60)
            host.axis['bottom'].major_ticklabels.set_pad(20)
            host.axis['bottom'].label.set_pad(30)
            anchor = (0.65, 0)

            if group.get_show_legend():
                    legend_borderaxespad = 8

        box = host.get_position()
        host.set_position([
            box.x0,
            box.y0 + box.height * height_factor,
            box.width * (1 - width_factor),
            box.height * (1 - height_factor)])

        if group.get_show_legend() or group.get_show_statistics():
            font_p = FontProperties(family='monospace')
            font_p.set_size('small')
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                host.legend(legend, loc='upper center', bbox_to_anchor=anchor,
                            fancybox=True, shadow=True, ncol=legend_cols,
                            borderaxespad=legend_borderaxespad,
                            labelspacing=0.1, prop=font_p, handles=artists)
        return host

    def get_label_header(self, group):
        """Fills the table header to be appended to the plot legend with the
        selected statistics settings.
        params:
            group: the Plotmodel that we are currently handling.
        return:
            label: the label header.
        """
        stat_sigs = group.get_statistics_signals()
        for signal in group.get_signals():
            if len(signal.get_label()) > self.signal_length:
                self.signal_length = len(signal.get_label())
            biggest = max(max(len(str(signal.get_std_y())),
                              len(str(signal.get_mean_y()))),
                          max(len(str(signal.get_min_y())),
                              len(str(signal.get_max_y()))))

            if biggest > self.value_len:
                self.value_len = biggest

        label = ""
        for signal in stat_sigs:
            if group.get_show_statistics():
                label = self.padd_string(label, self.signal_length + 4, False)
                for stat in group.get_statistics():
                    diff = self.value_len - len(stat)
                    stat = self.padd_string(stat, diff, False)
                    label = self.padd_string(label + stat,
                                             self.value_len - len(stat) + 4,
                                             True)
                label = label + "\n"
                return label
        return ""

    def padd_string(self, word, nbr_padds, pad_after):
        """This method pass a string with spaces before or after the string.
        params:
            word: the string to be padded
            nbr_padds: the number of spaces wanted
            pad_after: True if the padding should appear after the word,
                       False if it should appear before the word
        return:
            padded: the padded string.
        """
        padded = ""
        # Padd after word
        if pad_after is True:
            padded = padded.zfill(nbr_padds).replace('0', ' ')
            word = word + padded
            return word
        # Padd before word
        else:
            padded = padded.zfill(nbr_padds).replace('0', ' ')
            padded = padded + word
            return padded

    def append_table_to_label(self, group, label, signal):
        """Adds the table part of the plot legend for the specified signal.
        params:
            group: the Plotmodel that we are currently handling.
            label: the label we should append to.
            signal: The signal of interest.
        return:
            label: the updated label.
            reset_label: True is tabs should be expanded and the label should
                         be reset.
        """
        statistics_signals = group.get_statistics_signals()
        diff = self.signal_length - len(signal.get_label())
        padded = ""
        reset_label = False
        if group.get_show_legend() and not group.get_show_statistics():
            padded = self.padd_string(signal.get_label(),
                                      diff + 4, True)
            label = label + padded
            reset_label = True
        elif group.get_show_statistics() and not group.get_show_legend():
            if signal.get_label() in statistics_signals:
                padded = self.padd_string(signal.get_label(),
                                          diff + 4, True)
                label = label + padded
                label = self.fill_label_table(signal, label, group)
                reset_label = True
        elif group.get_show_legend() and group.get_show_statistics():
            padded = self.padd_string(signal.get_label(),
                                      diff + 4, True)
            label = label + padded
            if signal.get_label() in statistics_signals:
                label = self.fill_label_table(signal, label, group)
            reset_label = True
        return label, reset_label

    def fill_columns(self, signal, xaxis_datetime, yaxis_datetime):
        column_x = signal.get_data_x(models.Array)
        column_y = signal.get_data_y(models.Array)
        if column_x is not None and isinstance(column_x[0], np.datetime64):
            column_x = mdates.date2num(column_x.tolist())
            xaxis_datetime = True
        if column_y is not None and isinstance(column_y[0], np.datetime64):
            column_y = mdates.date2num(column_y.tolist())
            yaxis_datetime = True
        return xaxis_datetime, yaxis_datetime, column_x, column_y

    def _find_data_points(self, model, events):
        """"Sets the datapoint for every signal at the mouse click
        params:
            model: The current model.
            events: All gathered events.
        return:
            data_points: A list of all found data points.
        """
        # Loop signals
        signals = model.get_signals()
        table = model.get_table()
        data_points = []
        for event in events:
            for signal in signals:
                signal_label = signal.get_label()
                if signal_label in event[2]:
                    x = table.get_column_to_array(signal.get_data_x())
                    y = table.get_column_to_array(signal.get_data_y())
                    idx = event[3]
                    data_points.append((signal_label, x[idx], y[idx]))
        return data_points

    def _format_data_points(self, signals):
        """Returns a string with with all found signal names and values
        params:
            signals: the list of signal names, and X and Y values.
        return: A string with all signal names and values.
        """
        data_point = []
        for signal in signals:
            data_point.append(str(signal[0]))
            data_point.append('\n')
            data_point.append('X: ')
            data_point.append(format_value(signal[1]))
            data_point.append('\n')
            data_point.append('Y: ')
            data_point.append(format_value(signal[2]))
            data_point.append('\n')
        data_point.pop()
        return ''.join(data_point)

    def render_annotation(self, index=None):
        """Finds all signals in vicinity of mouse click and creates an
        annotation in the plot with x and y values for all found signals,
        if show_annotation is True. If multiple signals are found, the
        annotation is drawn on the line which first reported the event.
        params:
            index: Index of the current plot model.
        """
        if index is None:
            return
        model = self._model.get_plots()[index]
        event = model.get_annotation_event()
        if model.show_annotation() and len(event):
            data_points = self._find_data_points(model, event)
            if len(data_points) == 0:
                return
            note = self._format_data_points(data_points)
            xy = (data_points[0][1], data_points[0][2])
            dpi = self._figure.get_dpi()
            width = self._figure.get_figwidth() * dpi
            height = self._figure.get_figheight() * dpi
            x = event[0][0]
            y = event[0][1]
            x_text = -150 if x > width / 2 else -50
            y_text = -150 if y > height * 2 / 3 else 100
            self.clear_annotation()
            self._annotation = (
                self._axis.annotate(
                    note, xy=xy, xytext=(x_text, y_text),
                    textcoords='offset points',
                    arrowprops=dict(arrowstyle="->"),
                    bbox=dict(boxstyle="square", fc="yellow")))

    def clear_annotation(self):
        """Removes the annotation from the next render"""
        if self._annotation is not None:
            self._annotation.remove()
            self._annotation = None

    def clear_limits(self):
        """Clears the limit lines from the plot"""
        if self._low_lim is not None:
            self._low_lim.remove()
            self._low_lim = None
        if self._high_lim is not None:
            self._high_lim.remove()
            self._high_lim = None

    def _draw_limit(self, limit, pos, label, thick):
        """Draws a single limit line at pos with. If thick is True the line
        is drawn thicker.
        params:
            limit: previous limit line.
            pos: the x coordinate to place the line at.
            label: name of the line.
            thick: True if the line should be drawn thick, false otherwise.
        return:
            line: a referens to the new limit line.
        """
        if limit is not None:
            limit.remove()
        return self._axis.axvline(pos, label=label, color='black',
                                  picker=5, linewidth=2 if not thick else 4)

    def render_limits(self, index=None):
        """Adds the one or two selector lines to the plot, depending on
        the state of the model.
        params:
            index: Index of the current plot model.
        """
        if index is None:
            return
        model = self._model.get_plots()[index]
        low_in, high_in = model.get_limits()
        label = self._axis.get_label()
        high = None
        low = None

        if label in low_in:
            low = low_in[label]

        if label in high_in:
            high = high_in[label]

        if low:
            self._low_lim = self._draw_limit(self._low_lim, low,
                                             'low', False)
        if high:
            self._high_lim = self._draw_limit(self._high_lim, high,
                                              'high', False)
        if high and low:
            model.set_explicit_limits(label, low, high)

    def select_limit(self, name, index, line):
        """Renders the input line thicker to demark its selection
        params:
            name: name of the line.
            index: Index of the current plot model.
            line: the Line2D object.
        """
        if index is None or line is None:
            return
        low_in, high_in = self._model.get_plots()[index].get_limits()
        low, high = None, None
        if name in low_in:
            low = low_in[name]
        if name in high_in:
            high = high_in[name]

        self._low_lim = self._draw_limit(
            self._low_lim, low, 'low', True if line == 'low' else False)
        self._high_lim = self._draw_limit(
            self._high_lim, high, 'high', True if line == 'high' else False)

    def deselect_limits(self, name, index):
        """Renders both lines as deselected. Only one can be selected at
        any time so here we don't need to care which one is actually set.
        params:
            name: name of the line.
            index: index of the model.
        """
        if index is None:
            return
        low_in, high_in = self._model.get_plots()[index].get_limits()
        high = None
        low = None
        if name in low_in:
            low = low_in[name]
        if name in high_in:
            high = high_in[name]

        self._low_lim = self._draw_limit(self._low_lim, low, 'low', False)
        self._high_lim = self._draw_limit(self._high_lim, high, 'high', False)

    def move_limit(self, name, index, line, direction):
        """Renders the selected line 1% of the plot width from its previous
        position according to direction, and calculates the new position
        for the model to keep track of.
        params:
            index: index of the model.
            line: current limit line.
            direction: the direction of the scroll (up/down).
        return:
            flip: True if lines have crossed due to movement, false otherwise.
        """
        if index is None or line is None or direction is None:
            return
        model = self._model.get_plots()[index]
        low_in, high_in = model.get_limits()
        low = None
        high = None

        if name in low_in:
            low = low_in[name]
        if name in high_in:
            high = high_in[name]

        xmin, xmax = self._axis.get_xlim()
        step = (xmax - xmin) * 0.01
        flip = False
        if line == 'low':
            low = low - step if direction == 'down' else low + step
            low, high, flip = self._check_flip(low, high)
            self._low_lim = self._draw_limit(
                self._low_lim, low, 'low', False if flip else True)
        elif line == 'high':
            high = high - step if direction == 'down' else high + step
            low, high, flip = self._check_flip(low, high)
            self._high_lim = self._draw_limit(
                self._high_lim, high, 'high', False if flip else True)
        model.set_explicit_limits(name, low, high)
        return flip

    def _check_flip(self, low, high):
        """Checks if the lines have changed sides and makes the necessaray
        book keeping if so.
        params:
            low: the lower x coordinate.
            high: the higher x coordinate.
        return:
            low: updated low x coordinate.
            high: updated high x coordinate.
            bool: True if lines have been flipped, false otherwise
        """
        if low > high:
            self._low_lim, self._high_lim = self._high_lim, self._low_lim
            return high, low, True
        return low, high, False

    def update_limits_annotation(self, axes):
        if self._limits_annotation:
            try:
                self._limits_annotation.remove()
            except ValueError:
                pass
            self._limits_annotation = None
        try:
            limits = self._axis.get_xlim()
            low = mdates.num2date(limits[0]).strftime("%Y-%m-%d %H:%M:%S")
            high = mdates.num2date(limits[1]).strftime("%Y-%m-%d %H:%M:%S")
            note = 'Current limits: {}  -  {}'.format(low, high)
            self._limits_annotation = self._axis.text(
                0, -0.5, note, transform=self._axis.transAxes)
        except ValueError:
            pass

    def render(self, filename, index=None):
        if index is None:
            return

        self.clear_annotation()
        self.clear_limits()
        self.clear()
        group = self._model.get_plots()[index]
        group.clear_annotation_event()
        axis_models = {axis.get_label(): axis for axis in group.get_axes()}
        self._figure.subplots_adjust(right=0.8)
        legend_artists = []

        for i, group in enumerate([group], 1):
            sig_cnt = 0
            xaxis_datetime = False
            plot_label = list()
            axis_x = None
            axis_lookup_y = {}

            host_subplot_class = parasite_axes.host_subplot_class_factory(
                aa.Axes)
            host = host_subplot_class(self._figure, 111)
            ax = host
            self._axis = ax
            axis_dt_y = {}
            self._figure.add_subplot(host)
            label = self.get_label_header(group)

            xaxis_datetime = False
            for signal in group.get_signals():
                axis_x, axis_y = signal.get_axis()
                yaxis_datetime = False
                label, reset_label = self.append_table_to_label(
                    group, label, signal)
                add_to_legend = False

                try:
                    xaxis_datetime, yaxis_datetime, column_x, column_y = (
                        self.fill_columns(
                            signal, xaxis_datetime, yaxis_datetime))
                except (KeyError, IndexError):
                    continue

                if sig_cnt is 0:
                    # Left side axis.
                    ax = host
                    axis_lookup_y[axis_y] = ax
                    axis_dt_y[axis_y] = yaxis_datetime
                    sig_cnt += 1
                else:
                    # External axis.
                    if axis_y in axis_lookup_y:
                        ax = axis_lookup_y[axis_y]
                        axis_dt_y[axis_y] = yaxis_datetime
                    else:
                        ax = host.twinx()
                        new_fixed_axis = ax.get_grid_helper().new_fixed_axis
                        ax.axis['right'] = new_fixed_axis(
                            loc='right', axes=ax,
                            offset=((sig_cnt - 1) * 60, 0))
                        ax.axis['right'].toggle(all=True)
                        sig_cnt += 1
                        axis_lookup_y[axis_y] = ax
                        axis_dt_y[axis_y] = yaxis_datetime

                line = signal.get_line()
                marker = signal.get_marker()

                plot_extras = filter_none({
                    'linestyle': models.line_styles[line.get_style()],
                    'linewidth': line.get_width(),
                    'color': line.get_color(),
                    'marker': models.marker_styles[marker.get_style()],
                    'markersize': marker.get_size(),
                    'markeredgewidth': marker.get_edgewidth(),
                    'markeredgecolor': marker.get_edgecolor(),
                    'markerfacecolor': marker.get_facecolor()})

                if reset_label:
                    add_to_legend = True
                    plot_label.append(label.expandtabs())
                    label = ""

                try:
                    line_label = plot_label[-1]
                except:
                    line_label = ""
                if column_x is not None and column_y is not None:
                    plot, = ax.plot(
                        column_x, column_y, label=line_label, picker=5,
                        **plot_extras)
                    if add_to_legend:
                        legend_artists.append(plot)
                        add_to_legend = False

            for axis_y, ax in axis_lookup_y.items():
                try:
                    self.handle_y_axis(axis_models[axis_y], ax, yaxis_datetime)
                except KeyError:
                    pass

            self.handle_x_axis(axis_models[axis_x], host, xaxis_datetime)
            self.config_plot(
                host, group, axis_lookup_y, xaxis_datetime, plot_label,
                legend_artists)
            title = group.get_title()
            if title:
                self._figure.suptitle(title)

            self._axis.set_label(axis_models[axis_x].get_label())
            self._axis.set_picker(5)
            self._axis_span = self._axis.get_xlim()
            self._axis.callbacks.connect(
                'xlim_changed', self.update_limits_annotation)
            self.render_limits(index)


class XLSXWriterChartBackend(Backend):

    plot_formats = {
        'time': {'num_format': 'hh:mm:ss'},
        'date': {'num_format': 'yyyy-mm-dd'},
        'datetime': {'num_format': 'hh:mm:ss'}}

    dash_styles = {'dash-dotted': 'dash_dot',
                   'dashed': 'dash',
                   'dotted': 'dot',
                   'nothing': None,
                   'solid': None,
                   None: None}

    marker_styles = dict(zip(models.marker_styles,
                             models.marker_styles))
    marker_styles['nothing'] = 'none'

    grid_styles = {
        'both': {'major_gridlines': {'visible': True},
                 'minor_gridlines': {'visible': True}},
        'major': {'major_gridlines': {'visible': True},
                  'minor_gridlines': {'visible': False}},
        'minor': {'major_gridlines': {'visible': False},
                  'minor_gridlines': {'visible': True}},
        'nothing': {'major_gridlines': {'visible': False},
                    'minor_gridlines': {'visible': False}}}

    def __init__(self, model, workbook):
        self._model = model
        self._workbook = workbook
        self._wb_formats = {}
        self._wb_formats['bold'] = self._workbook.add_format({'bold': 1})
        self._wb_formats['boolean'] = self._workbook.add_format(
            {'num_format': 'BOOLEAN'})
        self._wb_formats['datetime'] = self._workbook.add_format(
            {'num_format': 'yyyy-mm-dd hh:mm:ss'})
        self._wb_formats['time'] = self._workbook.add_format(
            {'num_format': 'hh:mm:ss'})

    def render(self, sheet_name, header, render_plot):
        table = self._model.get_table()
        column_names = table.column_names()
        formats = self._formats(table)
        columns = {key: i for i, key in
                   enumerate(column_names)}
        worksheet = self._workbook.add_worksheet(sheet_name)

        # Write data columns.
        if header:
            worksheet.write_row(0, 0, column_names, self._wb_formats['bold'])
            start_row = 1
        else:
            start_row = 0

        end_row = table.number_of_rows() + start_row
        warn_about_datetimes = False
        warn_about_timedeltas = False
        for col, column_name in enumerate(column_names):
            col_format = formats[column_name]
            if col_format == 'boolean':
                for row, value in enumerate(
                        table.get_column_to_array(column_name).tolist(),
                        start_row):
                    if value is None:
                        continue
                    worksheet.write_boolean(row, col, value)
            elif col_format == 'datetime':
                for row, value in enumerate(
                        table.get_column_to_array(column_name).tolist(),
                        start_row):
                    if value is None:
                        continue
                    elif value < datetime.datetime(1900, 3, 1):
                        # All dates before 1900-03-01 are ambiguous because of
                        # a bug in Excel which incorrectly treats the year 1900
                        # as a leap year. So don't write any such dates to
                        # file.
                        warn_about_datetimes = True
                        continue
                    worksheet.write_datetime(
                        row, col, value, self._wb_formats[col_format])
            elif col_format == 'time':
                for row, value in enumerate(
                        table.get_column_to_array(column_name).tolist(),
                        start_row):
                    if value is None:
                        continue
                    elif value >= datetime.timedelta(days=1):
                        # Timedeltas can't be written to excel in general, but
                        # if the delta is less than a day, it can be
                        # represented as a time.
                        warn_about_timedeltas = True
                        continue
                    else:
                        value = value + datetime.datetime(1900, 1, 1)
                    worksheet.write_datetime(
                        row, col, value, self._wb_formats[col_format])
            else:
                column = table.get_column_to_array(column_name)
                if isinstance(column, np.ma.MaskedArray):
                    column = [None if v is np.ma.masked else v
                              for v in column.tolist()]
                try:
                    worksheet.write_column(start_row, col, column)
                except TypeError:
                    for data, row in zip(
                            column,
                            range(start_row, start_row + len(column))):
                        try:
                            worksheet.write(row, col, data)
                        except TypeError:
                            worksheet.write(row, col, '')

            ai = col2ai(col)
            self._workbook.define_name(
                "'{sheet}'!{name}".format(sheet=sheet_name,
                                          name=range_name(column_name)),
                "='{sheet}'!${col}${srow}:${col}${erow}".format(
                    sheet=sheet_name,
                    col=ai,
                    srow=start_row + 1,
                    erow=end_row))

        # Give a warning about problematic datetimes and/or timedeltas
        if warn_about_datetimes:
            exceptions.sywarn(
                "Not writing any datetimes before 1900-03-01. All dates "
                "before 1900-03-01 are ambiguous because of a bug in Excel.")
        if warn_about_timedeltas:
            exceptions.sywarn(
                "Not writing any timedeltas bigger than or equal to one full "
                "day. Such timedeltas can't be expressed in Excel.")

        if render_plot:
            if self._model.get_plots():
                worksheet = self._workbook.add_worksheet(
                    '{}-plot'.format(sheet_name))

            for index, plot in enumerate(self._model.get_plots()):
                self.render_plot(columns, plot, formats, index, worksheet,
                                 sheet_name)

    def render_plot(self, columns, plot, formats, index, worksheet,
                    sheet_name):

        def set_axis(setter, axis, num_format, label_position):
            settings = {
                'name': axis.get_label(),
                'min': axis.get_limits_min(),
                'max': axis.get_limits_max(),
                'label_position': label_position}

            settings.update(self.grid_styles[axis.get_grid()])
            if num_format:
                settings.update(self.plot_formats[num_format])
            setter(filter_none(settings))

        chart = self._workbook.add_chart({
            'type': 'scatter',
            'subtype': 'straight'})

        axis_ys = []
        signals = plot.get_signals()

        for signal in signals:
            axis_ys.append(signal.get_axis_y(models.Axis))

        axes = OrderedDict((key, i) for i, key in
                           enumerate(OrderedDict.fromkeys(axis_ys)))
        y2_num_format = {}
        length = plot.get_table().number_of_rows()

        chart.set_title({
            'name': plot.get_title()})

        for signal in signals:
            data_x, data_y = signal.get_data()
            try:
                column_x = columns[data_x]
                column_y = columns[data_y]
            except KeyError:
                continue

            label = signal.get_label()
            line = signal.get_line()
            marker = signal.get_marker()
            settings = {
                'name': label,
                'values': [sheet_name, 1, column_y, length + 1, column_y],
                'categories': [sheet_name, 1, column_x, length + 1, column_x]}

            line_settings = filter_none(
                {'color': line.get_color(models.RGBString),
                 'dash_type': self.dash_styles[line.get_style()],
                 'width': line.get_width()})
            marker_settings = filter_none(
                {'type': self.marker_styles[marker.get_style()]})

            if marker_settings:
                settings['marker'] = marker_settings

            if line_settings:
                settings['line'] = line_settings

            if len(axes) is 2:
                if axes[signal.get_axis_y(models.Axis)] == 1:
                    settings['y2_axis'] = True
                    y2_num_format = formats[data_y]
                else:
                    settings['y2_axis'] = False

            chart.add_series(filter_none(settings))

        if signals:
            first_signal = plot.get_signals()[0]
            x_axis = first_signal.get_axis_x(models.Axis)
            y_axis = first_signal.get_axis_y(models.Axis)
            try:
                x_num_format = formats[first_signal.get_data_x()]
                y_num_format = formats[first_signal.get_data_y()]
            except KeyError:
                x_num_format = None
                y_num_format = None
            set_axis(chart.set_x_axis, x_axis, x_num_format, 'low')
            set_axis(chart.set_y_axis, y_axis, y_num_format, 'low')
            if len(axes) is 2:
                set_axis(
                    chart.set_y2_axis, axes.keys()[1], y2_num_format, 'high')
        worksheet.insert_chart(16 * index, 0, chart)

    def _formats(self, table):
        column_names = table.column_names()
        if table.number_of_rows() is 0:
            return dict.fromkeys(column_names, None)

        formats = {}
        mini_table = table[:1]
        for column_name in column_names:
            column_type = mini_table.column_type(column_name).kind
            formats[column_name] = {}
            if column_type == 'M':
                formats[column_name] = 'datetime'
            elif column_type == 'm':
                formats[column_name] = 'time'
            elif column_type == 'b':
                formats[column_name] = 'boolean'
            else:
                formats[column_name] = None
        return formats


class ExporterBackend(Backend):
    def __init__(self, model, file_format):
        super(ExporterBackend, self).__init__(model)
        self._figure = Figure()
        self._file_format = file_format

    def render(self, filename_base):
        FigureCanvasAgg(self._figure)
        for i, plot in enumerate(self._model.get_plots()):
            self._figure.clf()
            backend = InteractiveBackend(self._model, self._figure)
            title = plot.get_title()
            if title == '':
                title = 'unnamed_plot_' + str(i)
            filename = '{}_{}.{}'.format(
                filename_base, title, self._file_format)
            backend.render(filename, i)
            self._figure.savefig(filename)
