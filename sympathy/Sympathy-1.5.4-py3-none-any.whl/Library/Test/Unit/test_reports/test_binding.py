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
from sylib.report import binding


class TestBindingHooks(unittest.TestCase):
    def setUp(self):
        self.result = None
        self.base_property = binding.PropertyWrapper(lambda: self.result,
                                                     self.base_setter)
        self.base_property_initial_setter = self.base_property.set
        self.binding_context = binding.BindingContext()
        self.hook1 = binding.create_and_apply_hook(
            self.base_property, self.binding_context)
        self.hook2 = binding.create_and_apply_hook(
            self.base_property, self.binding_context)
        self.hook3 = binding.create_and_apply_hook(
            self.base_property, self.binding_context)

    def base_setter(self, x):
        self.result = x

    def test_hook_chain(self):
        self.assertIs(self.result, None)
        self.hook3(0)
        self.assertEqual(self.result, 0)

    def test_remove_hook1(self):
        self.assertEqual(self.base_property.set, self.hook3)
        binding.remove_hook(self.hook1)
        self.assertEqual(self.base_property.set, self.hook3)
        self.assertEqual(self.hook3.previous_setter, self.hook2)
        self.assertEqual(self.hook2.previous_setter,
                         self.base_property_initial_setter)
        self.assertIs(self.result, None)
        self.hook3(0)
        self.assertEqual(self.result, 0)

    def test_remove_hook2(self):
        self.assertEqual(self.base_property.set, self.hook3)
        binding.remove_hook(self.hook2)
        self.assertEqual(self.base_property.set, self.hook3)
        self.assertEqual(self.hook3.previous_setter, self.hook1)
        self.assertEqual(self.hook1.previous_setter,
                         self.base_property_initial_setter)
        self.assertIs(self.result, None)
        self.hook3(0)
        self.assertEqual(self.result, 0)

    def test_remove_hook3(self):
        self.assertEqual(self.base_property.set, self.hook3)
        binding.remove_hook(self.hook3)
        self.assertEqual(self.base_property.set, self.hook2)
        self.assertEqual(self.hook2.previous_setter, self.hook1)
        self.assertEqual(self.hook1.previous_setter,
                         self.base_property_initial_setter)
        self.assertIs(self.result, None)
        self.hook2(0)
        self.assertEqual(self.result, 0)
