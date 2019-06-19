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
import unittest
import numpy as np
import six
from sylib.report import scales


class TestScales(unittest.TestCase):
    def test_identity_scale(self):
        identity_scale = scales.IdentityScale()
        self.assertEqual(identity_scale(0.0), 0.0)
        self.assertEqual(identity_scale(1.0), 1.0)

        domain_list = [1, 2, 3]
        domain_np_array = np.array(domain_list)

        range_list = identity_scale(domain_list)
        range_np_array = identity_scale(domain_np_array)

        self.assertIsInstance(range_list, type(domain_list))
        self.assertIsInstance(range_np_array, type(range_np_array))

        # Ensure types are ok.
        self.assertListEqual(domain_list, range_list)
        if six.PY2:
            self.assertItemsEqual(domain_np_array, range_np_array)

    def test_color_conversion(self):
        color_string = '#224466'

        color_tuple = scales.color_string_to_tuple(color_string)
        self.assertEqual(color_tuple[0], 0x22)
        self.assertEqual(color_tuple[1], 0x44)
        self.assertEqual(color_tuple[2], 0x66)

        new_color_string = scales.tuple_to_color_string(color_tuple)
        self.assertEqual(color_string, new_color_string)

        color1_string = '#ffffff'
        color2_string = '#000000'
        color1_tuple = scales.color_string_to_tuple(color1_string)
        color2_tuple = scales.color_string_to_tuple(color2_string)
        mid_color_tuple = scales.interpolate_color_tuples(
            color1_tuple, color2_tuple, 0.5)
        mid_color_string = scales.tuple_to_color_string(mid_color_tuple)
        self.assertEqual(mid_color_string, '#7f7f7f')

    def test_linear_scale(self):
        # Test numerics.
        linear_scale = scales.LinearScale([0, 1], [1, 2])

        self.assertEqual(linear_scale(0), 1)
        self.assertEqual(linear_scale(0.5), 1.5)
        self.assertEqual(linear_scale(1), 2)

        domain_values = [0, 0.5, 1]
        range_values = linear_scale(domain_values)

        if six.PY2:
            self.assertItemsEqual(range_values, [1, 1.5, 2])

        # Test colors.
        linear_color_scale = scales.LinearScale([0, 1], ['#ff0000', '#0000ff'])

        self.assertEqual(linear_color_scale(0), '#ff0000')
        self.assertEqual(linear_color_scale(1), '#0000ff')
        self.assertEqual(linear_color_scale(0.5), '#7f007f')

    def test_ordinal_scale(self):
        dom = ('a', 'b', 20)
        rng = (1, 2, 3)
        ordinal_scale = scales.OrdinalScale(dom, rng)

        for d, r in zip(dom, rng):
            self.assertEqual(ordinal_scale(d), r)
