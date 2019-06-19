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
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import collections
import copy
import unittest

from sylib.figure import gui, models
from sylib.figure.util import parse_configuration, export_config
from sylib.figure.colors import COLORS, parse_to_mpl_color


class ParseStringToMPLColorTestCase(unittest.TestCase):
    def test_mpl_colors(self):
        for c in COLORS:
            self.assertEqual(c, parse_to_mpl_color(c))

    def test_hex_color(self):
        text = '#ffffff'
        result = [1., 1., 1.]
        self.assertEqual(result, parse_to_mpl_color(text))

    def test_hexa_color(self):
        text = '#ffffffff'
        result = [1., 1., 1., 1.]
        self.assertEqual(result, parse_to_mpl_color(text))

    def test_rgb_int_color(self):
        test_cases = ['255, 255, 255',
                      '1, 1, 1']
        results = [[1., 1., 1.],
                   [1 / 255., 1 / 255., 1 / 255.]]
        for case, result in zip(test_cases, results):
            self.assertEqual(result, parse_to_mpl_color(case))

    def test_rgba_int_color(self):
        test_cases = ['255, 255, 255, 255',
                      '(255, 255, 255, 255)']
        result = [1., 1., 1., 1.]
        for case in test_cases:
            self.assertEqual(result, parse_to_mpl_color(case))

    def test_rgb_float_color(self):
        test_cases = ['1., 1., 1.',
                      '(1., 1., 1.)',
                      '1., 1. 1.',
                      '1 1 1.']
        result = [1., 1., 1.]
        for case in test_cases:
            self.assertEqual(result, parse_to_mpl_color(case))

    def test_rgba_float_color(self):
        text = '1., 1., 1., 1.'
        result = [1., 1., 1., 1.]
        self.assertEqual(result, parse_to_mpl_color(text))

    def test_wrong_imput(self):
        test_cases = ['255, 255',
                      '#ffes',
                      '#ffeegg',
                      '256, 1, 1']
        for text in test_cases:
            self.assertEqual(None, parse_to_mpl_color(text))


class ParseConfigurationTestCase(unittest.TestCase):
    stored_config = [
        ('figure.title', 'figure title'),
        ('figure.legend.show', 'True'),
        ('figure.legend.loc', 'best'),
        ('axes.axes-1.xaxis_position', 'bottom'),
        ('axes.axes-1.xlim', '(0, 1)'),
        ('axes.axes-1.xscale', 'log'),
        ('axes.axes-1.yaxis_position', 'left'),
        ('axes.axes-1.ylim', '(2, 5)'),
        ('axes.axes-1.yscale', 'linear'),
        ('axes.axes-2.xaxis_position', 'bottom'),
        ('axes.axes-2.yaxis_position', 'right'),
        ('axes.axes-1.grid.show', 'True'),
        ('axes.axes-1.grid.color', 'g'),
        ('axes.axes-1.grid.which', 'minor'),
        ('axes.axes-1.grid.linestyle', 'solid'),
        ('axes.axes-1.legend.loc', 'upper left'),
        ('axes.axes-1.legend.show', 'True'),
        ('axes.axes-2.grid.show', 'True'),
        ('line.line-1.xdata', 'index'),
        ('line.line-1.ydata', 'signal'),
        ('line.line-1.axes', 'axes-1'),
        ('scatter.scatter-1.xdata', 'index'),
        ('scatter.scatter-1.ydata', 'signal2'),
        ('scatter.scatter-1.axes', 'axes-1'),
        ('scatter.scatter-1.color', '[0.5, 0.5, 0.5]'),
        ('bar.bar-1.bin_labels', 'index'),
        ('bar.bar-1.ydata', 'signal3'),
        ('bar.bar-1.color', '[0.5, 0.5, 0.5]'),
        ('bar.bar-1.container', 'barcontainer-1'),
        ('hist.hist-1.bin_min_edges', 'index'),
        ('hist.hist-1.bin_max_edges', 'index2'),
        ('hist.hist-1.ydata', 'signal4'),
        ('hist.hist-1.axes', 'axes-1'),
        ('hist.hist-1.color', '[0.5, 0.5, 0.5]'),
        ('bar.bar-2.axes', 'axes-1'),
        ('bar.bar-2.bar_labels_font.color', 'k'),
        ('bar.bar-2.bar_labels_font.size', '12'),
        ('bar.bar-2.bin_labels', 'index'),
        ('bar.bar-2.ydata', 'signal5'),
        ('bar.bar-2.color', 'yellow'),
        ('barcontainer.barcontainer-1.grouping', 'stacked'),
        ('barcontainer.barcontainer-1.axes', 'axes-1'),
        ('barcontainer.barcontainer-1.bar_labels_font.color', 'red'),
        ('barcontainer.barcontainer-1.bar_labels_font.size', '25'),
    ]

    parsed_config = collections.OrderedDict([
        ('figure',
         collections.OrderedDict([
             ('title', 'figure title'),
             ('legend', collections.OrderedDict([('show', 'True'),
                                                 ('loc', 'best')])),
             ('axes', [collections.OrderedDict([
                 ('type', 'axes'),
                 ('xaxis', collections.OrderedDict([('position', 'bottom'),
                                                    ('lim', '(0, 1)'),
                                                    ('scale', 'log'), ])),
                 ('yaxis', collections.OrderedDict([('position', 'left'),
                                                    ('lim', '(2, 5)'),
                                                    ('scale', 'linear'), ])),
                 ('plots', [
                     collections.OrderedDict([
                         ('plots', [
                             collections.OrderedDict([
                                 ('ydata', 'signal3'),
                                 ('bin_labels', 'index'),
                                 ('type', 'bar'),
                                 ('color', '[0.5, 0.5, 0.5]'),
                             ]),
                         ]),
                         ('type', 'barcontainer'),
                         ('grouping', 'stacked'),
                         ('bar_labels_font', collections.OrderedDict([
                             ('color', 'red'),
                             ('size', '25')])),
                     ]),
                     collections.OrderedDict([('xdata', 'index'),
                                              ('ydata', 'signal'),
                                              ('type', 'line'), ]),
                     collections.OrderedDict([('xdata', 'index'),
                                              ('ydata', 'signal2'),
                                              ('type', 'scatter'),
                                              ('color', '[0.5, 0.5, 0.5]'), ]),
                     collections.OrderedDict([('ydata', 'signal5'),
                                              ('bin_labels', 'index'),
                                              ('type', 'bar'),
                                              ('bar_labels_font',
                                               collections.OrderedDict([
                                                   ('color', 'k'),
                                                   ('size', '12'), ]),),
                                              ('color', 'yellow'), ]),
                     collections.OrderedDict([('bin_min_edges', 'index'),
                                              ('bin_max_edges', 'index2'),
                                              ('ydata', 'signal4'),
                                              ('type', 'hist'),
                                              ('color', '[0.5, 0.5, 0.5]'), ]),
                 ]),
                 ('grid', collections.OrderedDict([('show', 'True'),
                                                   ('color', 'g'),
                                                   ('which', 'minor'),
                                                   ('linestyle', 'solid'), ])),
                 ('legend', collections.OrderedDict([('show', 'True'),
                                                     (
                                                     'loc', 'upper left'), ])),
             ]),
                 collections.OrderedDict([
                     ('type', 'axes'),
                     ('xaxis', collections.OrderedDict([
                         ('position', 'bottom'), ])),
                     ('yaxis', collections.OrderedDict([
                         ('position', 'right'), ])),
                     ('plots', []),
                     ('grid', collections.OrderedDict([
                         ('show', 'True'), ])),
                 ]),
             ]),
         ]),
         )])

    # @unittest.skip(u"Temporary disabled")
    def test_parse_configuration(self):
        self.maxDiff = None
        parsed_config = parse_configuration(copy.deepcopy(self.stored_config))
        self.assertDictEqual(self.parsed_config, parsed_config)

    def test_export_config(self):
        model = gui.DataModel(copy.deepcopy(self.parsed_config))
        font_nodes = model.root.find_all_nodes_with_class(models.BarLabelsFont)
        self.assertEqual(len(font_nodes), 2)
        exported_config = sorted(export_config(model))
        stored_config = sorted(self.stored_config)
        self.maxDiff = None
        self.assertEqual(exported_config, stored_config)
        self.assertEqual(len(exported_config), len(stored_config))


def runModelTest():  # noqa
    test_loader = unittest.TestLoader()
    test_loader.loadTestsFromTestCase(ParseStringToMPLColorTestCase)
    test_loader.loadTestsFromTestCase(ParseConfigurationTestCase)
    unittest.TextTestRunner(verbosity=2)
