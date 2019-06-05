# Copyright 2019 Red Hat
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from __future__ import absolute_import

import tobiko
from tobiko.tests import unit


class TestFail(unit.TobikoUnitTest):

    def test_fail(self):
        self._test_fail('some_reason')

    def test_fail_with_args(self):
        self._test_fail('some {1!r} {0!s}', 'reason', 'strange')

    def test_fail_with_kwargs(self):
        self._test_fail('some {b!r} {a!s}', a='reason', b='strange')

    def _test_fail(self, reason, *args, **kwargs):
        ex = self.assertRaises(
            tobiko.FailureException, tobiko.fail, reason, *args, **kwargs)
        if args or kwargs:
            expected_reason = reason.format(*args, **kwargs)
        else:
            expected_reason = reason
        self.assertEqual(expected_reason, str(ex))
