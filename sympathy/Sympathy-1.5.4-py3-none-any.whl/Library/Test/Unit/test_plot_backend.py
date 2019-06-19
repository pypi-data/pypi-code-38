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
import sys
import os
import unittest

import numpy as np
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import parasite_axes
from mpl_toolkits import axisartist as aa

from sympathy.api import table
from sylib.plot import model as models
from sylib.plot import gui as guis
from sylib.plot import backend as backends


class InteractiveBackendTestCase(unittest.TestCase):
    def setUp(self): # noqa
        self.longMessage = True
        self.figure = Figure()
        my_table = table.File()
        self.data1 = np.arange(100)
        self.data2 = np.arange(100)
        my_table.set_column_from_array('data1', self.data1)
        my_table.set_column_from_array('data2', self.data2)
        self.model = guis.IndexedPlotModel(models.PlotsModel(None, my_table))
        self.backend = backends.InteractiveBackend(self.model, self.figure)
        self.host = parasite_axes.host_subplot_class_factory(aa.Axes)(
            self.figure, 111)

    def tearDown(self): # noqa
        del self.figure
        del self.model
        del self.backend
        del self.host

    def testSetMajorTicks(self): # noqa
        """ test set_ticks for major. """
        limit_min_x, limit_max_x = self.host.get_xlim()
        ticks_major_x = '0.1'
        self.backend.set_ticks(self.host.xaxis, limit_min_x, limit_max_x,
                               ticks_major_x, False)

        major = ([(tick.get_view_interval())
                 for tick in self.host.xaxis.get_major_ticks()])
        self.assertEqual(len(major), 11,
                         'Doesnt contain correct amount of major ticks.')

        for tick in major:
            self.assertEqual((tick[0]), limit_min_x,
                             'Doesnt contain correct major min boundaries.')
            self.assertEqual((tick[1]), limit_max_x,
                             'Doesnt contain correct major max boundaries.')

    def testSetMinorTicks(self): # noqa
        """ test set_ticks for minor. """
        limit_min_x, limit_max_x = self.host.get_xlim()
        ticks_major_x = '0.1'
        ticks_minor_x = '0.05'

        self.backend.set_ticks(self.host.xaxis, limit_min_x, limit_max_x,
                               ticks_major_x, False)
        self.backend.set_ticks(self.host.xaxis, limit_min_x, limit_max_x,
                               ticks_minor_x, True)

        minor = ([(tick.get_view_interval())
                 for tick in self.host.xaxis.get_minor_ticks()])
        self.assertEqual(len(minor), 10,
                         'Doesnt contain correct amount of minor ticks.')

        for tick in minor:
            self.assertEqual((tick[0]), limit_min_x,
                             'Doesnt contain correct minor min boundaries.')
            self.assertEqual((tick[1]), limit_max_x,
                             'Doesnt contain correct minor max boundaries.')

    def testFillLabelTableNoStatistics(self): # noqa
        """ test fill_label_table(self, signal, label, group)
        when no statistics is set. """
        label = ""
        group = self.model.get_plots()[0]
        signal = group.get_signals()[0]
        self.model.set_show_statistics(True)
        self.model.set_statistics([])

        _label = self.backend.fill_label_table(signal, label, group)
        self.assertEqual(_label, label, 'Doesnt return the correct label')

    def testFillLabelTableNoStatistics2(self): # noqa
        """ test fill_label_table(self, signal, label, group)
        when no statistics is set. """
        label = ""
        group = self.model.get_plots()[0]
        signal = group.get_signals()[0]
        group.set_show_statistics(True)
        group.set_statistics(['Mean', 'Std'])
        _label = self.backend.fill_label_table(signal, label, group)
        self.assertEqual(
            _label, "-    -    ", "Doesn't return the correct label")

    def testHandleXAxis(self): # noqa
        """ test handle_x_axis(self, axis_model_x, host, xaxis_datetime),
            check label, scale and ticks and gridlines.
            Doesnt test for xaxis_datetime == True.
         """
        group = self.model.get_plots()[0]
        axis_model_x = group.get_axes()[0]
        self.backend.handle_x_axis(axis_model_x, self.host, False)

        # Check set label and set scale
        self.assertEqual(self.host.get_xlabel(), axis_model_x.get_label(),
                         'Doesnt contain correct label.')
        self.assertEqual(self.host.get_xscale(), axis_model_x.get_scale(),
                         'Doesnt contain correct x_scale.')

        # Check set ticks
        limit_min_x, limit_max_x = self.host.get_xlim()
        major = ([(tick.get_view_interval())
                 for tick in self.host.xaxis.get_major_ticks()])
        for tick in major:
            self.assertEqual((tick[0]), limit_min_x,
                             'Doesnt contain correct major min boundaries.')
            self.assertEqual((tick[1]), limit_max_x,
                             'Doesnt contain correct major max boundaries.')

        # Check set gridlines
        for axis_grid in ['both', 'minor', 'major', 'nothing']:

            if axis_grid == 'both':
                ticks = self.host.xaxis.get_majorticklocs()
                lines = self.host.get_lines()
                for index in range(0, min(len(ticks), len(lines))):
                    self.assertEqual(ticks[index], lines[index].get_xdata()[0],
                                     'Doesnt contain correct gridlines.')
                    self.assertEqual(ticks[index], lines[index].get_xdata()[1],
                                     'Doesnt contain correct gridlines.')
                ticks = self.host.xaxis.get_minorticklocs()
                lines = self.host.get_lines()
                for index in range(0, min(len(ticks), len(lines))):
                    self.assertEqual(ticks[index], lines[index].get_xdata()[0],
                                     'Doesnt contain correct gridlines.')
                    self.assertEqual(ticks[index], lines[index].get_xdata()[1],
                                     'Doesnt contain correct gridlines.')
            else:
                if axis_grid == 'minor':
                    ticks = self.host.xaxis.get_minorticklocs()
                elif axis_grid == 'major':
                    ticks = self.host.xaxis.get_majorticklocs()
                else:
                    return
                lines = self.host.get_lines()
                for index in range(0, min(len(ticks), len(lines))):
                    self.assertEqual(ticks[index], lines[index].get_xdata()[0],
                                     'Doesnt contain correct gridlines.')
                    self.assertEqual(ticks[index], lines[index].get_xdata()[1],
                                     'Doesnt contain correct gridlines.')

    def testHandleYAxis(self): # noqa
        """ test handle_x_axis(self, axis_model_x, host, xaxis_datetime),
            check label, scale and ticks and gridlines.
            Doesnt test for xaxis_datetime == True.
         """
        group = self.model.get_plots()[0]
        axis_model_y = group.get_axes()[1]
        self.backend.handle_y_axis(axis_model_y, self.host, False)

        # Check set label and set scale
        self.assertEqual(self.host.get_ylabel(), axis_model_y.get_label(),
                         'Doesnt contain correct label.')
        self.assertEqual(self.host.get_yscale(), axis_model_y.get_scale(),
                         'Doesnt contain correct y_scale.')

        # Check set ticks
        limit_min_y, limit_max_y = self.host.get_ylim()
        major = ([(tick.get_view_interval())
                 for tick in self.host.yaxis.get_major_ticks()])
        for tick in major:
            self.assertEqual((tick[0]), limit_min_y,
                             'Doesnt contain correct major min boundaries.')
            self.assertEqual((tick[1]), limit_max_y,
                             'Doesnt contain correct major max boundaries.')

        # Check set gridlines
        for axis_grid in ['both', 'minor', 'major', 'nothing']:
            if axis_grid == 'both':
                ticks = self.host.yaxis.get_majorticklocs()
                lines = self.host.get_lines()
                for index in range(0, min(len(ticks), len(lines))):
                    self.assertEqual(ticks[index], lines[index].get_ydata()[0],
                                     'Doesnt contain correct gridlines.')
                    self.assertEqual(ticks[index], lines[index].get_ydata()[1],
                                     'Doesnt contain correct gridlines.')
                ticks = self.host.yaxis.get_minorticklocs()
                lines = self.host.get_lines()
                for index in range(0, min(len(ticks), len(lines))):
                    self.assertEqual(ticks[index], lines[index].get_ydata()[0],
                                     'Doesnt contain correct gridlines.')
                    self.assertEqual(ticks[index], lines[index].get_ydata()[1],
                                     'Doesnt contain correct gridlines.')
            else:
                ticks = None
                if axis_grid == 'minor':
                    ticks = self.host.yaxis.get_minorticklocs()
                elif axis_grid == 'major':
                    ticks = self.host.yaxis.get_majorticklocs()
                else:
                    return
                lines = self.host.get_lines()
                for index in range(0, min(len(ticks), len(lines))):
                    self.assertEqual(ticks[index], lines[index].get_ydata()[0],
                                     'Doesnt contain correct gridlines.')
                    self.assertEqual(ticks[index], lines[index].get_ydata()[1],
                                     'Doesnt contain correct gridlines.')

    @unittest.skip('Implement later')
    def testConfigPlotMoreThanTreeAxesShow_statistics(self): # noqa
        """ test config_plot(self, host, group,
        axis_lookup_y, xaxis_datetime). """
        group = self.model.get_plots()[0]
        axis_lookup_y = [self.host, self.host, self.host, self.host]
        xaxis_datetime = False
        group.set_show_statistics(True)
        try:
            self.backend.config_plot(self.host, group, axis_lookup_y,
                                     xaxis_datetime, '', [])
        except TypeError:
            raise unittest.SkipTest(
                'Matplotlib version has trouble with multiple handles.')

        self.assertEqual(
            self.host.axis['bottom'].major_ticklabels.get_rotation(), 60,
            'Wrong major_ticklabels rotation.')
        self.assertEqual(
            self.host.axis['bottom'].major_ticklabels.get_pad(),
            20, 'Wrong major_ticklabels pad.')
        self.assertEqual(self.host.axis['bottom'].label.get_pad(), 30,
                         'Wrong label pad.')

    def testGetLabelHeader(self): # noqa
        """test get_label_header for some different cases."""
        group = self.model.get_plots()[0]
        group.set_statistics(["Min", "Max"])
        group.set_statistics_signals(['New signal 0'])
        group.set_show_statistics(True)
        _label = self.backend.get_label_header(group)
        label = "{:16s}".format(" ")
        label = label + "{:5s}".format('Min')
        label = label + "{:5s}".format('Max')
        label = label + "\n"
        self.assertEqual(_label, label, 'Doesnt return correct header label')
        group.set_statistics_signals([])
        _label = self.backend.get_label_header(group)
        self.assertEqual(_label, "", 'Doesnt return correct header label')
        group.set_show_statistics(False)
        _label = self.backend.get_label_header(group)
        self.assertEqual(_label, "", 'Doesnt return correct header label')

    def testAppendTableToLabelNoStatistics(self): # noqa
        """ test append_table_to_label(self, group, label, signal)
        when get_show_statistics = False."""
        group = self.model.get_plots()[0]
        label = ""
        signal = group.get_signals()[0]
        group.set_show_statistics(False)
        group.set_show_legend(True)
        label, reset_label = self.backend.append_table_to_label(group, label,
                                                                signal)
        self.assertTrue(reset_label,
                        'reset_label should be False but was True')
        self.assertEqual(label, signal.get_label(),
                         'Doesnt return correct label table')
        group.set_show_legend(False)
        label = ""
        label, reset_label = self.backend.append_table_to_label(group, label,
                                                                signal)
        self.assertFalse(reset_label,
                         'reset_label should be True but was False')
        self.assertEqual(label, "", 'Doesnt return correct label table')

    def testAppendTableToLabelNoStatistics2(self): # noqa
        """ test append_table_to_label(self, group, label, signal)
        when get_show_statistics = True."""
        label = ""
        group = self.model.get_plots()[0]
        signal = group.get_signals()[0]
        group.set_show_statistics(False)
        group.set_show_legend(True)
        label, reset_label = self.backend.append_table_to_label(group, label,
                                                                signal)
        self.assertTrue(reset_label,
                        'reset_label should be False but was True')
        self.assertEqual(label, signal.get_label(),
                         'Doesnt return correct label table')
        group.set_show_legend(False)
        label = ""
        label, reset_label = self.backend.append_table_to_label(group, label,
                                                                signal)
        self.assertFalse(reset_label,
                         'reset_label should be True but was False')
        self.assertEqual(label, "", 'Doesnt return correct label table')

    @unittest.skip('Implement later')
    def testFillColumns(self): # noqa
        """ test fill_columns(self, signal, xaxis_datetime, yaxis_datetime)."""
        self.assertTrue(True)

    @unittest.skip('Needs mockup of model')
    def testFindDataPoints(self): # noqa
        pass

    def testFormatDataPoints(self): # noqa
        """ Test that annotations are formatted as expected """
        signals = [('test1', 0, 0), ('test2', 1, 2)]
        self.assertEqual(self.backend._format_data_points(signals),
                         'test1\nX: 0\nY: 0\ntest2\nX: 1\nY: 2',
                         'Formating is wrong.')

    @unittest.skip('Hard to test')
    def testRenderAnnotation(self): # noqa
        pass

    @unittest.skip('Hard to test')
    def testClearAnnotation(self): # noqa
        pass

    @unittest.skip('Hard to test')
    def testClearLimits(self): # noqa
        pass

    @unittest.skip('Hard to test')
    def testRenderLimtis(self): # noqa
        pass

    def testCheckFlip(self): # noqa
        low, high = 0.5, 0.7
        new_low, new_high, flip = self.backend._check_flip(low, high)
        self.assertEqual((new_low, new_high, flip), (low, high, False))
        new_low, new_high, flip = self.backend._check_flip(high, low)
        self.assertEqual((new_low, new_high, flip), (low, high, True))

    def testPaddString(self): # noqa
        """ test so that padd_string works correctly."""
        word = 'test'
        _word = self.backend.padd_string(word, 4, True)
        self.assertEqual(_word, word + "    ", 'String was padded wrong.')
        _word = self.backend.padd_string(word, 2, False)
        self.assertEqual(_word, "  " + word, 'String was padded wrong.')


def runBackendTest(): # noqa
    test_loader = unittest.TestLoader()
    test_loader.loadTestsFromTestCase(InteractiveBackendTestCase)
    unittest.TextTestRunner(verbosity=2)
