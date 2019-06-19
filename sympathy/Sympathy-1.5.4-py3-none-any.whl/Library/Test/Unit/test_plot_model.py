# Copyright (c) 2015, Combine Control Systems AB
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
import unittest
import itertools
import six

import numpy as np
from PySide.QtCore import Signal

from sympathy.api import table
from sylib.plot import model as models


class SignalModelTestCase(unittest.TestCase):
    def setUp(self): # noqa
        self.longMessage = True
        my_table = table.File()
        self.data1 = np.arange(100)
        self.data2 = np.arange(100)
        my_table.set_column_from_array('data1', self.data1)
        my_table.set_column_from_array('data2', self.data2)
        plot_model = models.PlotModel(None, my_table)    # Mock later
        self.signal = plot_model.get_signals()[0]
        self.signal.set_data_x('data1')
        self.signal.set_data_y('data2')

    def tearDown(self): # noqa
        del self.signal

    def testDefaultLabel(self): # noqa
        """ test get_label() returns 'New signal 0' if no label is set."""
        self.assertEqual(
            self.signal.get_label(), 'New signal 0',
            "get_label() doesn't return correct default label.")

    def testSetGetLabel_(self): # noqa
        """ test get_label() the label that have been set."""
        label = "Label"
        self.signal.set_label(label)
        self.assertEqual(
            self.signal.get_label(), label,
            "get_label() doesn't return label set by set_label(label).")

    def test_get_data_column(self): # noqa
        """ test _get_data_column
        """
        _data1 = self.signal._get_data_column('data1', models.Array)
        for i in range(0, len(_data1)):
            self.assertEqual(_data1[i], self.data1[i])

    def testSetGetData(self): # noqa
        """ tests set_data(data) and get_data() """
        data = np.random.rand(2, 10)
        self.signal.set_data(data)
        _data = self.signal.get_data()
        self.assertEqual(
            len(data[0]), len(_data[0]),
            'length of data[0] is not equal to length of _data[0]')
        self.assertEqual(
            len(data[1]), len(_data[1]),
            'length of data[1] is not equal to length of _data[1]')

        for index in range(0, len(data)):
            self.assertEqual(
                data[0][index], _data[0][index],
                'data[0] is not equal to _data[0:')
            self.assertEqual(
                data[1][index], _data[1][index],
                'data[1] is not equal to _data[0]')

    def testGetDataX(self): # noqa
        """ tests get_data_x() data have been set. """
        data = np.random.rand(2, 10)
        self.signal.set_data(data)
        x = self.signal.get_data_x()
        for index in range(0, len(data)):
            self.assertEqual(
                data[0][index], x[index],
                'data[0] is not equal to x')

    def testGetStdY(self): # noqa
        """ tests get_std_y() data have been set. """
        result = round(np.std(self.data2, dtype=np.float), 2)
        std = self.signal.get_std_y()
        self.assertEqual(std, result)

    def testGetMeanY(self): # noqa
        result = round(np.mean(self.data2), 2)
        mean = self.signal.get_mean_y()
        self.assertEqual(mean, result)

    def testGetMaxY(self): # noqa
        result = round(max(self.data2), 2)
        _max = self.signal.get_max_y(models.Array)
        self.assertEqual(_max, result)

    def testGetMinY(self): # noqa
        result = round(min(self.data2), 2)
        _min = self.signal.get_min_y(models.Array)
        self.assertEqual(_min, result)

    def testGetDataY(self): # noqa
        """ tests get_data_x() data have been set. """
        data = np.random.rand(2, 10)
        self.signal.set_data(data)
        y = self.signal.get_data_y()
        for index in range(0, len(data)):
            self.assertEqual(
                data[1][index], y[index],
                'data[1] is not equal to y')

    def test_get_axis_axis(self): # noqa
        label = 'X'
        self.assertEqual(
            label,
            self.signal._get_axis_axis(label, models.Axis).get_label())

    def testSetGetAxis(self): # noqa
        """ test set_axis(axis) and get_axis(). """
        axis = ['P', 'Q']
        self.signal.set_axis(axis)
        self.assertEqual(
            self.signal.get_axis(), axis,
            'get_axis() doesnt return axis set by set_axis(axis).')

    def testGetDefaultAxis(self): # noqa
        """ test get_axis() if no axis have been set. """
        axis = ['X', 'Y']
        self.assertEqual(
            self.signal.get_axis(), axis,
            'get_axis() doesnt return correct default axis.')

    def testGetDefaultAxisX(self): # noqa
        """ test get_axis_x() if no axis have been set. """
        self.assertEqual(
            self.signal.get_axis_x(), 'X',
            'get_axis_x() doesnt return correct default x_axis.')

    def testGetDefaultAxisY(self): # noqa
        """ test get_axis_y() if no axis have been set. """
        self.assertEqual(
            self.signal.get_axis_y(), 'Y',
            'get_axis_y() doesnt return correct default y_axis.')

    def testSetGetAxisX(self): # noqa
        """ test set_axis_x(axis) and get_axis_x(). """
        axis = 'P'
        self.signal.set_axis_x(axis)
        self.assertEqual(
            self.signal.get_axis_x(), 'P',
            'get_axis_x() doesnt return x_axis set by set_axis_x(axis).')

    def testSetGetAxisY(self): # noqa
        """ test set_axis_y(axis) and get_axis_y(). """
        axis = 'Q'
        self.signal.set_axis_y(axis)
        self.assertEqual(
            self.signal.get_axis_y(), 'Q',
            'get_axis_y() doesnt return y_axis set by set_axis_y(axis).')

    def testGetLine(self): # noqa
        """ test get_line """
        self.assertIsInstance(
            self.signal.get_line(), models.LineModel,
            'get_line() is not an instance of LineModel')

    def testGetMarker(self): # noqa
        """ test get_marker """
        self.assertIsInstance(self.signal.get_marker(), models.MarkerModel,
                              'get_marker() is not an instance of MarkerModel')

    def testSetGetDataX(self): # noqa
        """ test set_data_x(data) and get_data_x(). """
        data = np.random.rand(2, 10)
        self.signal.set_data_x(data[0])
        x = self.signal.get_data_x()
        self.assertEqual(
            len(data[0]), len(x),
            'length of data is not equal to length of x')
        for index in range(0, len(data)):
            self.assertEqual(
                data[0][index], x[index],
                'get_data_x() doesnt return x_data set by set_data_x(data).')

    def testSetGetDataY(self): # noqa
        """ test set_data_y(data) and get_data_y(). """
        data = np.random.rand(2, 10)
        self.signal.set_data_y(data[1])
        y = self.signal.get_data_y()
        self.assertEqual(
            len(data[1]), len(y),
            'length of data is not equal to length of y')

        for index in range(0, len(data[1])):
            self.assertEqual(
                data[1][index], y[index],
                'get_data_y() doesnt return y_data set by set_data_y(data).')

    @unittest.skip("Implement later")
    def set_line(self): # noqa
        self.AssertTrue(True)

    @unittest.skip("Implement later")
    def set_marker(self): # noqa
        self.AssertTrue(True)

    def testGetXLimits(self): # noqa
        """ test get_x_limits(). """
        _limits = self.signal.get_x_limits()
        self.assertEqual(_limits, (0, 99))


class PlotModelTestCase(unittest.TestCase):
    def setUp(self): # noqa
        self.longMessage = True
        table = None
        dict_arg = None
        self.plot = models.PlotModel(dict_arg, table)

    def tearDown(self): # noqa
        del self.plot

    def testGetDefaultTitle(self): # noqa
        """ test get_title() when title haven't been set. """
        self.assertEqual(
            self.plot.get_title(), '',
            'get_title() doesnt return correct default title')

    def testSetGetTitle(self): # noqa
        """ test get_title() set by set_title(title). """
        title = 'Title'
        self.plot.set_title(title)
        self.assertEqual(
            self.plot.get_title(), title,
            'get_title() doesnt return title set set_title(title)')

    def testGetDefaultShowLegend(self): # noqa
        """ test get_show_legend when show_legend haven't been set. """
        self.assertTrue(
            self.plot.get_show_legend(),
            'get_show_legend() doesnt return correct default value')

    def testGetSetShowLegend(self): # noqa
        """ test get_show_legend set by set_show_legend. """
        self.plot.set_show_legend(False)
        self.assertFalse(
            self.plot.get_show_legend(),
            'get_show_legend() doesnt return value set ' +
            'by set_show_legend(value)')

    def testGetDefaultShowStatistics(self): # noqa
        """ test get_show_statistics when show_statistics haven't been set. """
        self.assertFalse(
            self.plot.get_show_statistics(),
            'get_show_statistics() doesnt return correct default value.')

    def testGetSetShowStatistics(self): # noqa
        """ test get_show_statistics set by set_show_statistics """
        self.plot.set_show_statistics(True)
        self.assertTrue(
            self.plot.get_show_statistics(),
            'get_show_statistics() doesnt return value set ' +
            'by set_show_statistics(value).')

    def testGetDefaultStatistics(self): # noqa
        """ test get_statistics when statistics haven't been set."""
        self.assertEqual(
            self.plot.get_statistics(), [],
            'get_statistics() doesnt return correct default value.')

    def testGetSetStatistics(self): # noqa
        """ test get_statistics set by set_statistics."""
        signals = list()
        signals.append('Mean')
        signals.append('Max')
        self.plot.set_statistics(signals)
        self.assertListEqual(
            self.plot.get_statistics(), signals,
            'get_statistics() doesnt return value set ' +
            'by set_statistics(value)')

        del signals

    def testGetDefaultStatisticsSignals(self): # noqa
        """ test get_statistics_signals when statistics haven't been set."""
        self.assertEqual(
            self.plot.get_statistics_signals(), [],
            'get_statistics_signals() doesnt return correct default value.')

    def testGetSetStatisticsSignals(self): # noqa
        """ test get_statistics_signals set by set_statistics_signals. """
        signals = list()
        signals.append('Signal 0')
        signals.append('Signal 1')
        self.plot.set_statistics_signals(signals)
        self.assertListEqual(
            self.plot.get_statistics_signals(), signals,
            'get_statistics_signals() doesnt return value set ' +
            'by get_statistics_signals(signals).')
        del signals

    def testGetDefaultAxes(self): # noqa
        """ test get_axes() when axes haven't been set. """
        _names = [_ax.get_label() for _ax in self.plot.get_axes()]

        self.assertListEqual(_names, list(['X', 'Y']),
                             'get_axes() doesnt return correct default value.')
        del _names

    def testGetSetAxes(self): # noqa
        """ test get_axes() set by set_axes(axes). """
        axes = [models.AxisModel(self, axis)
                for axis in [models.AxisModel(self, None, 'P').to_dict(),
                             models.AxisModel(self, None, 'Q').to_dict()]]
        self.plot.set_axes(axes)
        self.assertListEqual(
            self.plot.get_axes(), axes,
            'get_axes() doesnt return axes set by set_axes(axes)')
        del axes

    def testGetDefaultSignals(self): # noqa
        """ test get_signals when signals haven't been set. """
        _names = [_signal.get_label() for _signal in self.plot.get_signals()]
        self.assertListEqual(
            _names, list(['New signal 0']),
            'get_signals() doesnt return correct default value.')
        del _names

    def testGetSetSignals(self): # noqa
        """ test get_signals set by set_signals(signals). """
        signals = [models.SignalModel(self, None, 'New signal 0'),
                   models.SignalModel(self, None, 'New signal 1')]
        self.plot.set_signals(signals)
        self.assertListEqual(
            self.plot.get_signals(), signals,
            'get_signals() doesnt return value set by set_signals(signals).')
        del signals

    def testGetSignalsByAxisX(self): # noqa
        """ test get_signals_by_axis_x. """
        signals = list()
        signals.append('New signal 0')
        _signals_by_axis_x = self.plot.get_signals_by_axis_x()
        _signals = list(itertools.chain(*_signals_by_axis_x))
        _names = [_signal.get_label() for _signal in _signals]
        self.assertListEqual(
            _names, signals,
            'get_signals_by_axis_x() doesnt return correct default value.')
        del _names
        del _signals
        del signals

    def testGetDefaultTable(self): # noqa
        """ test get_table when table haven't been set. """
        if six.PY2:
            self.assertItemsEqual(
                self.plot.get_table(), models.sytable.File(),
                'get_table() doesnt return correct default value.')

    def testAddAxis(self): # noqa
        """ test add_axis  """
        axes = self.plot.get_axes()
        self.plot.add_axis(models.AxisModel(self, None, 'P'))
        _axes = self.plot.get_axes()
        self.assertNotEqual(
            len(_axes), len(axes),
            'Size of axes list didnt increase after adding a new axes.')

    def testAddExistingAxis(self): # noqa
        """ test so that adding an existing axis raises a key error. """
        with self.assertRaises(KeyError):
            self.plot.add_axis(models.AxisModel(self, None, 'X'))

    def testAddSignal(self): # noqa
        """ test add_signal.  """
        signals = self.plot.get_signals()
        self.plot.add_signal(models.SignalModel(self, None, 'New signal 1'))
        _signals = self.plot.get_signals()
        self.assertNotEqual(
            len(_signals), len(signals),
            'Size of signal list didnt increase after adding a new signal.')

    def testAddExistingSignal(self): # noqa
        """ test so that adding an existing signals raises a key error. """
        with self.assertRaises(KeyError):
            self.plot.add_signal(
                models.SignalModel(self, None, 'New signal 0'))

    def testRemoveExistingAxis(self): # noqa
        """ test to remove an existing axis  """
        self.plot.add_axis(models.AxisModel(self, None, 'P'))
        axes = self.plot.get_axes()
        self.plot.remove_axis(models.AxisModel(self, None, 'P'))
        _axes = self.plot.get_axes()
        self.assertNotEqual(
            len(_axes), len(axes),
            'Size of axes list didnt decrease after removing an axes.')

    def testRemoveNotExistingAxis(self): # noqa
        """ test to remove an not existing axis  """
        self.plot.add_axis(models.AxisModel(self, None, 'P'))
        with self.assertRaises(KeyError):
            self.plot.remove_axis(models.AxisModel(self, None, 'Q'))

    def testRemoveOnlyAxis(self): # noqa
        """ test to remove the only existing axis, except ValueError. """
        with self.assertRaises(ValueError):
            self.plot.remove_axis(models.AxisModel(self, None, 'X'))

    def testRemoveExistingSignal(self): # noqa
        """ test to remove an existing axis  """
        self.plot.add_signal(models.SignalModel(self, None, 'New signal 1'))
        signals = self.plot.get_signals()
        self.plot.remove_signal(models.SignalModel(self, None, 'New signal 1'))
        _signals = self.plot.get_signals()
        self.assertNotEqual(
            len(_signals), len(signals),
            'Size of signals list didnt decrease after removing a signal.')

    def testRemoveNotExistingSignal(self): # noqa
        """ test to remove a not existing signal, except KeyError. """
        self.plot.add_signal(models.SignalModel(self, None, 'New signal 1'))
        with self.assertRaises(KeyError):
            self.plot.remove_signal(
                models.SignalModel(self, None, 'New signal 2'))

    def testRemoveOnlySignal(self): # noqa
        """ test to remove the only existing signal, except ValueError. """
        with self.assertRaises(ValueError):
            self.plot.remove_signal(
                models.SignalModel(self, None, 'New signal 0'))

    def testGetSetClearAnnotationEvent(self): # noqa
        """ test to check that the annotation event gets set and reset """
        event = self.plot.get_annotation_event()
        self.assertEqual(event, [])

        self.plot.set_annotation_event(1, 2, 'three', 4)
        event = self.plot.get_annotation_event()
        self.assertEqual(event, [(1, 2, 'three', 4)])

        self.plot.set_annotation_event(1, 2, 'three', 4)
        event = self.plot.get_annotation_event()
        self.assertEqual(event, [(1, 2, 'three', 4)])

        self.plot.set_annotation_event(1, 2, 'seven', 8)
        event = self.plot.get_annotation_event()
        self.assertEqual(event, [(1, 2, 'three', 4),
                                 (1, 2, 'seven', 8)])

        self.plot.set_annotation_event(3, 4, 'three', 4)
        event = self.plot.get_annotation_event()
        self.assertEqual(event, [(3, 4, 'three', 4)])

        self.plot.clear_annotation_event()
        self.assertEqual(event, [])

    def testToggleAnnotationEvent(self): # noqa
        """ test to see that the annotaion event get toogles as expected """
        self.assertEqual(self.plot.show_annotation(), False)
        self.plot.toggle_annotation()
        self.assertEqual(self.plot.show_annotation(), True)
        self.plot.toggle_annotation()
        self.assertEqual(self.plot.show_annotation(), False)

    def testToggleSelectorsEvent(self): # noqa
        """ test to see that the selector event get toogles as
        expected and show_selectors works as intended. """
        self.assertEqual(self.plot.show_selectors(), False)
        self.plot.toggle_selectors()
        self.assertEqual(self.plot.show_selectors(), True)
        self.plot.toggle_selectors()
        self.assertEqual(self.plot.show_selectors(), False)

    def testClearLimits(self): # noqa
        """ test to see that limits are cleared correctly """
        self.plot.clear_limits()
        limits = self.plot.get_limits()
        self.assertEqual(limits, ({}, {}))

    def testGetSetClearLimits_olderTest(self): # noqa
        """ test to see that limits are set correctly """
        axis = 'Axis 1'

        self.plot.set_limits(axis, 0)
        limits = self.plot.get_limits()
        self.assertEqual(len(limits[0]), 1)
        self.assertTrue(axis in limits[0])
        self.assertFalse(axis in limits[1])

        self.assertEqual(limits[0][axis], 0)
        self.assertEqual(limits[1], {})

        self.plot.set_limits(axis, 2)
        limits = self.plot.get_limits()
        self.assertEqual(len(limits[0]), 1)
        self.assertTrue(axis in limits[0])
        self.assertEqual(limits[0][axis], 0)
        self.assertEqual(limits[1][axis], 2)

        self.plot.set_limits(axis, 4)
        limits = self.plot.get_limits()
        self.assertEqual(len(limits[0]), 1)
        self.assertTrue(axis in limits[0])
        self.assertTrue(axis in limits[1])

        self.assertEqual(limits[0][axis], 0)
        self.assertEqual(limits[1][axis], 2)

        self.plot.clear_limits()
        limits = self.plot.get_limits()
        self.assertFalse(axis in limits[0])
        self.assertFalse(axis in limits[1])

        self.plot.set_limits(axis, 10)
        self.plot.set_limits(axis, 0)
        limits = self.plot.get_limits()
        self.assertEqual(len(limits[0]), 1)
        self.assertTrue(axis in limits[0])
        self.assertTrue(axis in limits[1])
        self.assertEqual(limits[0][axis], 0)
        self.assertEqual(limits[1][axis], 10)

    def testGetSetClearLimits(self): # noqa
        axis1 = 'Axis 1'
        axis2 = 'Axis 2'

        self.plot.set_limits(axis1, 1)
        low, high = self.plot.get_limits()
        self.assertTrue(axis1 in low)
        self.assertFalse(axis1 in high)
        self.assertEqual(low[axis1], 1)

        self.plot.set_limits(axis1, 2)
        low, high = self.plot.get_limits()
        self.assertTrue(axis1 in low)
        self.assertTrue(axis1 in high)
        self.assertEqual(high[axis1], 2)
        self.assertEqual(low[axis1], 1)
        self.plot.clear_limits()

        self.plot.set_limits(axis1, 1)
        self.plot.set_limits(axis2, 2)
        low, high = self.plot.get_limits()

        self.assertTrue(axis1 in low)
        self.assertTrue(axis2 in low)
        self.assertFalse(axis1 in high)
        self.assertFalse(axis2 in high)
        self.assertEqual(low[axis1], 1)
        self.assertEqual(low[axis2], 2)

        self.plot.set_limits(axis1, 2)
        low, high = self.plot.get_limits()
        self.assertTrue(axis1 in low)
        self.assertTrue(axis2 in low)
        self.assertTrue(axis1 in high)
        self.assertFalse(axis2 in high)
        self.assertEqual(high[axis1], 2)
        self.assertEqual(low[axis1], 1)
        self.assertEqual(low[axis2], 2)
        self.plot.clear_limits()

        self.plot.set_limits(axis1, 2)
        self.plot.set_limits(axis1, 1)
        low, high = self.plot.get_limits()
        self.assertTrue(axis1 in low)
        self.assertTrue(axis1 in high)
        self.assertEqual(high[axis1], 2)
        self.assertEqual(low[axis1], 1)
        self.plot.clear_limits()

        self.plot.set_limits(axis1, 2)
        self.plot.set_limits(axis2, 2)
        low, high = self.plot.get_limits()
        self.assertTrue(axis1 in low)
        self.assertTrue(axis2 in low)
        self.assertFalse(axis1 in high)
        self.assertFalse(axis2 in high)
        self.assertEqual(low[axis1], 2)
        self.assertEqual(low[axis2], 2)

        self.plot.set_limits(axis1, 1)
        low, high = self.plot.get_limits()
        self.assertTrue(axis1 in low)
        self.assertTrue(axis2 in low)
        self.assertTrue(axis1 in high)
        self.assertFalse(axis2 in high)
        self.assertEqual(high[axis1], 2)
        self.assertEqual(low[axis1], 1)
        self.assertEqual(low[axis2], 2)

        self.plot.set_limits(axis2, 1)
        low, high = self.plot.get_limits()
        self.assertTrue(axis1 in low)
        self.assertTrue(axis2 in low)
        self.assertTrue(axis1 in high)
        self.assertTrue(axis2 in high)
        self.assertEqual(high[axis1], 2)
        self.assertEqual(high[axis2], 2)
        self.assertEqual(low[axis1], 1)
        self.assertEqual(low[axis2], 1)

    def testSetExplicitLimits(self): # noqa
        """ test to see that limits are set correctly when set explicitly"""
        axis = 'Axis 1'
        self.plot.set_explicit_limits(axis, 1, 2)
        low, high = self.plot.get_limits()
        self.assertEqual((low[axis], high[axis]), (1, 2))

    def testGetLimitTrigger(self): # noqa
        """  test get_limits_trigger. """
        _limit_trigger = self.plot.get_limits_trigger()
        self.assertIsInstance(
            _limit_trigger, Signal,
            'get_limits_trigger() doesnt retrn a Signal')


class PlotsModelTestCase(unittest.TestCase):
    def setUp(self): # noqa
        self.longMessage = True
        table = None
        dict_arg = None
        dict_attr = None
        self.plots = models.PlotsModel(dict_arg, table, dict_attr)

    def tearDown(self): # noqa
        del self.plots

    def testWriteTableAttributesOnNoneTable(self): # noqa
        """ Test to write_table_attribute if table is None,
        except AssertionError.  """
        self.plots.set_table(None)
        with self.assertRaises(AssertionError):
            self.plots.write_table_attribute()

    def testGetDefaultTable(self): # noqa
        """ test get_table when table haven't been set. """
        if six.PY2:
            self.assertItemsEqual(
                self.plots.get_table(), models.sytable.File(),
                'get_table() doesnt return correct default value.')

    def testSetGetTable(self): # noqa
        """ tests get_table set by set_table. """
        table = models.sytable.File()
        table.set_name("TestTable")
        self.plots.set_table(table)

        if six.PY2:
            self.assertItemsEqual(
                self.plots.get_table(), table,
                'get_table() doesnt return value set by set_table(table).')

    def testGetDefaultPlots(self): # noqa
        """ test get_plots when plots haven't been set. """
        _tables = [_plot.get_table() for _plot in self.plots.get_plots()]
        if six.PY2:
            self.assertItemsEqual(
                _tables[0], models.sytable.File(),
                'get_plots() doesnt return correct default value.')

    def testSetgetPlots(self): # noqa
        """ test get_plots set by set_plots(plots). """
        plot = models.PlotModel(None, None)
        plot.set_title("Test Plot")
        self.plots.set_plots([plot])
        _plot = self.plots.get_plots()
        self.assertEqual(
            len(_plot), 1, 'PlotsModel holds wrong amount of plots')
        self.assertListEqual(
            _plot, list([plot]),
            'get_plots doesnt return plot set by set_plots(plots).')

    def testAddPlot(self): # noqa
        """ tests add_plot. """
        plots = self.plots.get_plots()
        self.plots.add_plot(models.PlotModel(None, None))
        _plots = self.plots.get_plots()
        self.assertNotEqual(
            len(_plots), len(plots),
            'Size of plots list didnt increase after adding a new plot.')

    def testRemoveExistingPlot(self): # noqa
        """ tests remove_plot for existing plot. """
        plot = models.PlotModel(None, None)
        plot.set_title("Test Plot")
        self.plots.add_plot(plot)
        plots = self.plots.get_plots()
        self.plots.remove_plot(plot)
        _plots = self.plots.get_plots()
        self.assertNotEqual(
            len(_plots), len(plots),
            'Size of plots list didnt decrease after removing a plot.')

    def testRemoveNotExistingPlot(self): # noqa
        """ tests remove_plot for non existing plot. """
        plot = models.PlotModel(None, None)
        plot.set_title("Test Plot")
        self.plots.add_plot(plot)
        with self.assertRaises(KeyError):
            self.plots.remove_plot(models.PlotModel(None, None))

    def testRemoveOnlyPlot(self): # noqa
        """ tests remove_plot on only plot. """
        plot = models.PlotModel(None, None)
        with self.assertRaises(ValueError):
            self.plots.remove_plot(plot)


class AxisModelTestCase(unittest.TestCase):
    def setUp(self): # noqa
        self.longMessage = True
        dict_arg = None
        label = None
        plot_model = None
        self.axis = models.AxisModel(plot_model, dict_arg, label)

    def tearDown(self): # noqa
        del self.axis

    def to_dict(self): # noqa
        return self.__data

    def testGetDefaultLabel(self): # noqa
        """ test get_label when no label have been set. """
        self.assertEqual(
            self.axis.get_label(),
            'New axis 0', 'get_label doesnt return correct default value.')

    def testGetSetLabel(self): # noqa
        """ test get_label when label is set by set_label(label). """
        plot = models.PlotModel(None, None)
        label = "Test Axis"
        self.axis = models.AxisModel(plot, None, None)
        self.axis.set_label(label)
        self.assertEqual(
            self.axis.get_label(), label,
            'get_label doesnt return value set by set_label(label).')
        del plot

    def testGetDefaultScale(self): # noqa
        """ test get_scale when no scale have been set. """
        self.assertEqual(
            self.axis.get_scale(), 'linear',
            'get_scale doesnt return correct default value.')

    def testGetSetScale(self): # noqa
        """ test get_scale when scale is set by set_scale. """
        self.axis.set_scale("log")
        self.assertEqual(
            self.axis.get_scale(), 'log',
            'get_scale doesnt return value set by set_scale(scale).')

    def testGetDefaultLimit(self): # noqa
        """ test get_limits when no limits have been set. """
        self.assertListEqual(
            self.axis.get_limits(), [None, None],
            'get_limits doesnt return correct default value.')

    def testGetSetLimits(self): # noqa
        """ test get_limits when limits is set by set_limits. """
        limits = [10, 100]
        self.axis.set_limits(limits)
        self.assertListEqual(
            self.axis.get_limits(), limits,
            'get_limits doesnt return value set by set_limits(limits).')

    def testGetDefaultLimitsMin(self): # noqa
        """ test get_limits_min when limits_min haven't been set. """
        self.assertEqual(
            self.axis.get_limits_min(), None,
            'get_limits_min doesnt return correct default value.')

    def testGetSetLimitsMin(self): # noqa
        """ test get_limits_min when limits_min have been set
        by set_limits_min. """
        min_limit = 10
        self.axis.set_limits_min(min_limit)
        self.assertEqual(
            self.axis.get_limits_min(), min_limit,
            'get_limits_min doesnt return value set by ' +
            'set_limits_min(min_limit).')

    def testGetDefaultLimitsMax(self): # noqa
        """ test get_limits_max when limits_min haven't been set. """
        self.assertEqual(
            self.axis.get_limits_max(), None,
            'get_limits_max doesnt return correct default value. ')

    def testGetSetLimitsMax(self): # noqa
        """ test get_limits_min when limits_min have been set
        by set_limits_min. """
        max_limit = 20
        self.axis.set_limits_max(max_limit)
        self.assertEqual(
            self.axis.get_limits_max(), max_limit,
            'get_limits_max doesnt return value set by ' +
            'set_limits_max(max_limit). ')

    def testGetDefaultTicks(self): # noqa
        """ test get_ticks when ticks haven't been set. """
        self.assertEqual(
            self.axis.get_ticks(), [None, None],
            'get_ticks doesnt return correct default value. ')

    def testGetSetTicks(self): # noqa
        """ test get_ticks when ticks have been set by set_ticks. """
        ticks = [20, 50]
        self.axis.set_ticks(ticks)
        self.assertEqual(
            self.axis.get_ticks(), ticks,
            'get_ticks doesnt return value set by set_ticks(ticks). ')

    def testGetDefaultMinorTicks(self): # noqa
        """ test get_ticks_minor when ticks_minor haven't been set. """
        self.assertEqual(
            self.axis.get_ticks_minor(), None,
            'get_ticks_minor doesnt return correct default value.')

    def testGetSetMinorTicks(self): # noqa
        """ test get_ticks_minor when ticks have been set by
        set_ticks_minor. """
        ticks = 10
        self.axis.set_ticks_minor(ticks)
        self.assertEqual(
            self.axis.get_ticks_minor(), ticks,
            'get_ticks_minor doesnt return value set by ' +
            'set_ticks_minor(ticks).')

    def testGetDefaultMajorTicks(self): # noqa
        """ test get_limits_max when limits_min haven't been set. """
        self.assertEqual(
            self.axis.get_limits_max(), None,
            'get_limits_max doesnt return correct default value.')

    def testGetSetMajorTicks(self): # noqa
        """ test get_ticks_major when limits_min have been set
        by set_ticks_major. """
        ticks = 20
        self.axis.set_ticks_major(ticks)
        self.assertEqual(
            self.axis.get_ticks_major(), ticks,
            'get_ticks_major doesnt return value set by ' +
            'set_ticks_major(ticks).')

    def testGetDefaultGrid(self): # noqa
        """  test get_grid when grid haven't been set. """
        self.assertEqual(
            self.axis.get_grid(), 'nothing',
            'get_grid doesnt return correct default value.')

    def testGetSetGrid(self): # noqa
        """  test get_grid set by set_grid. """
        grid = "Some Grid"
        self.axis.set_grid(grid)
        self.assertEqual(
            self.axis.get_grid(), grid,
            'get_grid doesnt return value set by get_grid(grid).')


def runModelTest(): # noqa
    test_loader = unittest.TestLoader()
    test_loader.loadTestsFromTestCase(SignalModelTestCase)
    test_loader.loadTestsFromTestCase(PlotModelTestCase)
    test_loader.loadTestsFromTestCase(PlotsModelTestCase)
    test_loader.loadTestsFromTestCase(AxisModelTestCase)
    unittest.TextTestRunner(verbosity=2)
