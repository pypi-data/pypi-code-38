# Copyright (c) 2015-2017 Combine Control Systems AB
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
import unittest
from sylib.calculator import calculator_model as model


def _check_ast(expr):
    return model.Calc('name', expr, enabled=True).exc


class TestCalculator(unittest.TestCase):
    def setUp(self):  # noqa
        self.longMessage = True

    def test_easy(self):
        calc = '{x for x in [1]}'
        self.assertIsNone(_check_ast(calc))
        calc = '{x for x in [(1,5)]}'
        self.assertIsNone(_check_ast(calc))

    def test_easy_errors(self):
        calc = '{x for y in [1]}'
        self.assertIsInstance(_check_ast(calc), NameError)

    def test__check_ast(self):
        calc = '{x:y for y in [[1]] for x in y}'
        self.assertIsNone(_check_ast(calc))

    def test_NameError(self):
        calc = '{x:y for x in y for y in [1]}'
        self.assertIsInstance(_check_ast(calc), NameError)

    def test1(self):
        calc = '{2:2 for x in [1]}'
        _check_ast(calc)
        self.assertIsNone(_check_ast(calc))

    def test2(self):
        calc = '{x:x for x in [1]}'
        _check_ast(calc)
        self.assertIsNone(_check_ast(calc))

    def test3(self):
        calc = '{x:y for x, y in [(1,1)]}'
        _check_ast(calc)
        self.assertIsNone(_check_ast(calc))

    def test4(self):
        calc = '{x:y for (x,  y) in [(1,1)]}'
        self.assertIsNone(_check_ast(calc))

    def test_lambda(self):
        calc = 'np.array(map(lambda x:  x + 1, [1, 2, 3]))'
        self.assertIsNone(_check_ast(calc))

    def test_lambda_and_compare(self):
        calc = 'np.array(map(lambda x:  x + 1 > 1, [1, 2, 3]))'
        self.assertIsNone(_check_ast(calc))
