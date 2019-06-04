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

import pytest

from fresco.util import security


class TestSecurity(object):

    def test_check_equal_constant_time_returns_equality(self):
        assert security.check_equal_constant_time('', '') is True
        assert security.check_equal_constant_time('abcabcabc', 'abcabcabc') \
                is True

    def test_check_equal_constant_time_returns_inequality(self):
        assert security.check_equal_constant_time(' ', '') is False
        assert security.check_equal_constant_time('abcabcabc', 'abcabcabx') \
                is False
        assert security.check_equal_constant_time('abcabcabc', 'abcabcabx') \
                is False
        assert security.check_equal_constant_time('abcabcabc', 'abcabcabde') \
                is False
        assert security.check_equal_constant_time('abcabcabc', 'abcabcab') \
                is False

    def test_check_equal_constant_time_raises_an_error_on_non_strings(self):
        with pytest.raises(TypeError):
            security.check_equal_constant_time(None, None)
