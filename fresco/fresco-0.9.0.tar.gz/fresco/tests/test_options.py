# Copyright 2015 Oliver Cope
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
from __future__ import absolute_import

import sys
from tempfile import NamedTemporaryFile
from fresco.options import Options


class TestOptions(object):

    def test_options_dictionary_access(self):
        options = Options()
        options['x'] = 1
        assert options['x'] == 1

    def test_options_attribute_access(self):
        options = Options()
        options.x = 1
        assert options.x == 1

    def test_options_update_from_object(self):

        class Foo:
            a = 1
            b = 2

        options = Options()
        options.update_from_object(Foo())
        assert options == {'a': 1, 'b': 2}

    def test_options_update_from_object_loads_underscore_names(self):

        class Foo:
            pass

        options = Options()
        options.update_from_object(Foo(), True)
        assert '__module__' in options

    def test_options_update_from_file(self):

        with NamedTemporaryFile() as tmpfile:
            tmpfile.write(b"a = 1\nb = 2\n")
            tmpfile.flush()

            options = Options()
            options.update_from_file(tmpfile.name)
            assert options == {'a': 1, 'b': 2}

    def test_options_respects_all(self):
        with NamedTemporaryFile() as tmpfile:
            tmpfile.write(b"__all__ = ['a']\n"
                          b"a = 1\n"
                          b"b = 2\n")
            tmpfile.flush()

            options = Options()
            options.update_from_file(tmpfile.name)
            assert options == {'a': 1}

    def test_update_from_file_doesnt_add_module(self):
        with NamedTemporaryFile() as tmpfile:
            options = Options()
            saved_modules = list(sorted(sys.modules.keys()))
            options.update_from_file(tmpfile.name)
            assert list(sorted(sys.modules.keys())) == saved_modules
