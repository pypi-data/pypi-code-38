# Copyright (c) 2016, Combine Control Systems AB
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
import sys
import os
from sympathy.utils.library_info import LibraryInfo, _parse_input


def _create_library_info(string):
    """Dummy fpr testing"""
    return LibraryInfo('test', _parse_input(string))


class TestLibraryInfo(unittest.TestCase):
    def test_one_section(self):
        info = ['[Section]\n',
                'Property1=property1\n',
                'Property2=property2\n']
        lib_info = _create_library_info(info)
        if lib_info._to_string() == ''.join(info):
            print('one_section pass')
        else:
            print('one_section fail')

    def test_two_sections(self):
        info = ['[Section1]\n',
                'Property1=property1\n',
                '[Section2]\n',
                'Property2=property2\n']
        lib_info = _create_library_info(info)
        self.assertEqual(lib_info._to_string(), ''.join(info))

    def test_only_section(self):
        info = ['[Section1]\n']
        lib_info = _create_library_info(info)
        self.assertEqual(lib_info._to_string(), ''.join(info))

    def test_faulty_section(self):
        info = ['[Section1\n']
        lib_info = _create_library_info(info)
        self.assertEqual(lib_info._to_string(), '')

    def test_no_section(self):
        info = ['']
        lib_info = _create_library_info(info)
        self.assertEqual(lib_info._to_string(), '')

    def test_property_before_section(self):
        info = ['Property1=property1\n',
                '[Section1]\n']
        lib_info = _create_library_info(info)
        self.assertEqual(lib_info._to_string(), '')

    def test_faulty_property(self):
        info = ['[Section1]\n',
                'Property1\n']
        stderr = sys.stderr
        sys.stderr = open(os.devnull, 'w')
        lib_info = _create_library_info(info)
        sys.stderr = stderr
        self.assertEqual(lib_info._to_string(), '[Section1]\n')

    def test_keys(self):
        info = ['[section]\n',
                'Property=prop\n']
        out = {'section': ['Property']}
        lib_info = _create_library_info(info)
        self.assertEqual('section' in lib_info.keys(), True)
        self.assertEqual(out, lib_info.keys())

    def test_contains(self):
        info = {}
        info['section'] = {'key': 'value'}
        lib_info = LibraryInfo('test', info)
        self.assertEqual('section' in lib_info, True)
        self.assertEqual(('section', 'key') in lib_info, True)

    def test_getitem(self):
        info = ['[section]\n',
                'key=value\n']
        lib_info = _create_library_info(info)
        self.assertEqual('section' in lib_info, True)
        self.assertEqual(lib_info['section']['key'], 'value')
        prop = lib_info[('section', 'key')]
        self.assertEqual(prop, 'value')

    def test_setitem(self):
        lib_info = LibraryInfo('test', {})
        lib_info['section'] = {}
        lib_info['section']['key'] = 'value'
        self.assertEqual('section' in lib_info, True)
        self.assertEqual(lib_info['section']['key'], 'value')
        lib_info[('section', 'property')] = 'key'
        self.assertEqual('section' in lib_info, True)
        self.assertEqual(lib_info[('section', 'property')], 'key')


if __name__ == '__main__':
    unittest.main()
