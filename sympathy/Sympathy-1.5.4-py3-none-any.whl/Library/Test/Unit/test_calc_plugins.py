# -*- coding:utf-8 -*-
# Copyright (c) 2017, Combine Control Systems AB
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
import re
import unittest
import itertools
import collections

import six
import numpy as np

from sympathy.api import table
import sylib.calculator.plugins as plugins
import sylib.calculator.calculator_model as models
import sylib.old_calculator.calculator_model as old_models


class TestLogics(unittest.TestCase):
    """Test class that tests Logic operators and functions."""

    def setUp(self):
        self.longMessage = True

    def test_nand_index_array_constants(self):
        """
        Test :func:`NAND` with one index array and a constant.
        """
        signals = {"in_arr": np.ones(10)}
        expected = np.ones(10)

        out_arr = calc_wrapper("ca.nand(${in_arr}, 0)", signals)
        assert (out_arr == expected).all()
        out_arr = calc_wrapper("ca.nand(${in_arr}, False)", signals)
        assert (out_arr == expected).all()

        expected = np.zeros(10)
        out_arr = calc_wrapper("ca.nand(${in_arr}, 1)", signals)
        assert (out_arr == expected).all()
        out_arr = calc_wrapper("ca.nand(${in_arr}, True)", signals)
        assert (out_arr == expected).all()

    def test_nand_index_arrays(self):
        """
        Test :func:`NAND` with two index arrays of same length.
        """
        signals = {"in_arr": np.ones(10)}
        expected = np.zeros(10)
        out_arr = calc_wrapper("ca.nand(${in_arr}, ${in_arr})", signals)
        assert (out_arr == expected).all()

        signals = {"in_arr": np.ones(10),
                   "value": np.zeros(10)}
        expected = signals["in_arr"]
        out_arr = calc_wrapper("ca.nand(${in_arr}, ${value})", signals)
        assert (out_arr == expected).all()

        signals = {"in_arr": np.array([1, 1, 1, 0, 0, 0]),
                   "value": np.array([0, 0, 1, 0, 0, 1])}
        expected = np.array([1, 1, 0, 1, 1, 1])
        out_arr = calc_wrapper("ca.nand(${in_arr}, ${value})", signals)
        assert (out_arr == expected).all()

    def test_nor_index_array_constants(self):
        """
        Test :func:`NOR` with one index array and a constant.
        """
        signals = {"in_arr": np.ones(10)}
        expected = np.zeros(10)
        out_arr = calc_wrapper("ca.nor(${in_arr}, 0)", signals)
        assert (out_arr == expected).all()

        out_arr = calc_wrapper("ca.nor(${in_arr}, False)", signals)
        assert (out_arr == expected).all()

        out_arr = calc_wrapper("ca.nor(${in_arr}, 1)", signals)
        assert (out_arr == expected).all()

        out_arr = calc_wrapper("ca.nor(${in_arr}, True)", signals)
        assert (out_arr == expected).all()

        signals = {"in_arr": np.array([1, 1, 1, 0, 0, 0])}
        expected = np.array([0, 0, 0, 1, 1, 1])
        out_arr = calc_wrapper("ca.nor(${in_arr}, 0)", signals)
        assert (out_arr == expected).all()

        expected = np.zeros(6)
        out_arr = calc_wrapper("ca.nor(${in_arr}, 1)", signals)
        assert (out_arr == expected).all()

    def test_nor_index_arrays(self):
        """
        Test :func:`NOR` with two index arrays of same length.
        """
        signals = {"in_arr": np.ones(10)}
        expected = np.zeros(10)
        out_arr = calc_wrapper("ca.nor(${in_arr}, ${in_arr})", signals)
        assert (out_arr == expected).all()

        signals['value'] = np.zeros(10)
        out_arr = calc_wrapper("ca.nor(${in_arr}, ${value})", signals)
        assert (out_arr == expected).all()

        signals = {"in_arr": np.array([1, 1, 1, 0, 0, 0]),
                   "value": np.array([0, 0, 1, 0, 0, 1])}
        expected = np.array([0, 0, 0, 1, 1, 0])
        out_arr = calc_wrapper("ca.nor(${in_arr}, ${value})", signals)
        assert (out_arr == expected).all()


class TestEventDetection(unittest.TestCase):
    """Test class that tests Event detection functions."""

    longMessage = True

    def test_changed_functions(self):
        """Test changed, changed_up, and changed_down."""
        N = np.nan
        I = np.inf
        ma_inval = np.ma.masked_invalid

        tests = [
            (np.ones(10),
             np.zeros(10),
             np.zeros(10)),
            (np.array([1, 0, 1, 0, 0, 1, 1]),
             np.array([0, 0, 1, 0, 0, 1, 0]),
             np.array([0, 1, 0, 1, 0, 0, 0])),
            (np.array([4, 0, -5, 0, 0, 3, 1]),
             np.array([0, 0,  0, 1, 0, 1, 0]),
             np.array([0, 1,  1, 0, 0, 0, 1])),
            (np.array([1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1]),
             np.array([0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0]),
             np.array([0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0])),
            (np.array([I, 0, 0, -I, 0, 0, I, -I, I]),
             np.array([0, 0, 0,  0, 1, 0, 1,  0, 1]),
             np.array([0, 1, 0,  1, 0, 0, 0,  1, 0])),
            (np.array([N, 0, -5, N, N, 3, 1]),
             np.array([0, 0,  0, 0, 0, 0, 0]),
             np.array([0, 0,  1, 0, 0, 0, 1])),
            (ma_inval([N, 0, -5, N, 0, 3, 1]),
             ma_inval([N, N,  0, N, N, 1, 0]),
             ma_inval([N, N,  1, N, N, 0, 1])),
            (ma_inval([0, 0, -5, 0, 0, 3, 1]),
             ma_inval([0, 0,  0, 1, 0, 1, 0]),
             ma_inval([0, 0,  1, 0, 0, 0, 1])),
        ] + list(six.moves.zip(  # Avoid repeating expected for all of these:
            [
                np.array([4, 0, 5, 0, 0, 3, 1], dtype='uint8'),
                np.array([4, 0, 5, 0, 0, 3, 1], dtype='int32'),
                np.array([4, 0, 5, 0, 0, 3, 1], dtype='float'),
                np.array([4, 0, 5, 0, 0, 3, 1], dtype='timedelta64[us]'),
                np.array([4, 0, 5, 0, 0, 3, 1], dtype='timedelta64[s]'),
                np.array([4, 0, 5, 0, 0, 3, 1], dtype='timedelta64[D]'),
                np.array([4, 0, 5, 0, 0, 3, 1], dtype='datetime64[us]'),
                np.array([4, 0, 5, 0, 0, 3, 1], dtype='datetime64[s]'),
                np.array([4, 0, 5, 0, 0, 3, 1], dtype='datetime64[D]'),
                np.array([1, 0, 1, 0, 0, 1, 0], dtype='bool'),
            ],
            itertools.repeat(np.array([0, 0, 1, 0, 0, 1, 0])),
            itertools.repeat(np.array([0, 1, 0, 1, 0, 0, 1]))))

        for i, (in_arr, chu_exp, chd_exp) in enumerate(tests):
            signals = {"in_arr": in_arr}
            chu_out = calc_wrapper("ca.changed_up(${in_arr})", signals)
            chd_out = calc_wrapper("ca.changed_down(${in_arr})", signals)
            ch_out = calc_wrapper("ca.changed(${in_arr})", signals)

            msg = 'Test {}: signal = {!r}'.format(i, in_arr)
            ch_exp = np.logical_or(chu_exp, chd_exp)
            self.assertEqual(chu_out.dtype.kind, 'b', msg=msg)
            self.assertEqual(chd_out.dtype.kind, 'b', msg=msg)
            self.assertEqual(ch_out.dtype.kind, 'b', msg=msg)
            if np.ma.isMA(ch_out):
                np.testing.assert_array_equal(
                    ch_out.mask, ch_exp.mask, err_msg=msg)
            if np.ma.isMA(chd_out):
                np.testing.assert_array_equal(
                    chd_out.mask, chd_exp.mask, err_msg=msg)
            if np.ma.isMA(chu_out):
                np.testing.assert_array_equal(
                    chu_out.mask, chu_exp.mask, err_msg=msg)
            np.testing.assert_array_equal(
                chu_out, chu_exp.astype(bool), err_msg=msg)
            np.testing.assert_array_equal(
                chd_out, chd_exp.astype(bool), err_msg=msg)
            np.testing.assert_array_equal(
                ch_out, ch_exp.astype(bool), err_msg=msg)


def calc_wrapper(line, in_dict=None, extra_globals=None):
    """Simple wrapper around models.python_calculator."""
    in_table = table.File()
    if in_dict:
        for k, v in six.iteritems(in_dict):
            in_table.set_column_from_array(k, v)

    calc = update_calc("a = {}".format(line))
    line = old_models.format_calculation(calc, False)
    line = line.split('= ', 1)[1]
    extra_globals = dict(extra_globals or {})
    extra_globals['arg'] = in_table
    output = models.python_calculator(
        line, extra_globals or {})
    return output


def update_calc(calc):
    names = []
    ekv = calc.split("=", 1)
    left_side = ekv[0]
    name = re.findall(r'\${([^{}]+)}', left_side)
    if name:
        names.append(name[0])
    right_side = ekv[1]
    columns = re.findall(r'\${([^{}]+)}', right_side)
    for col in columns:
        var = "arg"
        if col in names:
            var = "res"
        right_side = right_side.replace('${{{}}}'.format(col), var +
                                        ".col('{}').data".format(col))
        name = re.findall(r'\${([^{}]+)}', left_side)
        if name:
            left_side = name[0]
    return left_side.strip() + " = " + right_side.strip()


def walk_gui_dict(gui_dict):
    """
    Traverse the dict/list gui_dict structure to find all eval texts yielding
    one test per eval text.
    """
    if isinstance(gui_dict, collections.Mapping):
        for value in gui_dict.values():
            for test in walk_gui_dict(value):
                yield test
    elif isinstance(gui_dict, collections.Iterable):
        for value in gui_dict:
            line = value[1]
            yield line
    else:
        raise TypeError("gui_dict() should return Mapping or Iterable. "
                        "Got {} instead.".format(type(gui_dict)))


def test_all_eval_strings():
    """Test that all plugin eval texts can be evaluated."""
    for plugin in plugins.available_plugins('python'):
        gui_dict = plugin.gui_dict()
        signals = plugin.signals_dict()
        variables = plugin.variables_dict()
        for line in walk_gui_dict(gui_dict):
            calc_wrapper(line, signals, variables)


def test_enable():
    """Test original requirements on some functions in ca."""
    def check_mask(i, eval_string):
        output = calc_wrapper(eval_string, signals)
        assert (output == result_rows[i]).all()

    signals = {'signal':
        np.array([4, 4, 4, 4, 4, 0, 0, 0, 0, 0, 0, 4, 4, 4, 4, 4, 0, 0, 1, 2, 3, 1, 1, 1, 1, 2, 2, 1, 0, 0])}                       # noqa
    result_rows = [
        np.array([0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0]).astype(bool),   # 0    # noqa
        np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]).astype(bool),   # 1    # noqa
        np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0]).astype(bool),   # 2    # noqa
        np.array([0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0]).astype(bool),   # 3    # noqa
        np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0]).astype(bool),   # 4    # noqa
        np.array([0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0]).astype(bool),   # 5    # noqa
        np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0]).astype(bool),   # 6    # noqa
        np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0]).astype(bool),   # 7    # noqa
        np.array([0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]).astype(bool),   # 8    # noqa
        np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1]).astype(bool)]   # 9    # noqa

    check_mask(0, "ca.shift_array(${signal} == 0, -1)")
    check_mask(1, "ca.first(${signal} == 1)")
    check_mask(2, "ca.last(${signal} == 1)")
    check_mask(3, "ca.changed(${signal})")
    check_mask(4, "ca.changed_up(${signal})")
    check_mask(5, "ca.changed_down(${signal})")
    check_mask(6, "ca.local_max(${signal})")
    check_mask(7, "ca.local_min(${signal})")
    check_mask(8, "ca.shift_seq_start(${signal} == 0, 3)")
    check_mask(9, "ca.shift_seq_end(${signal} == 0, 3)")
