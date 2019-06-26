# -*- coding: utf-8 -*-
# Copyright (c) 2018  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Chenxiong Qi <cqi@redhat.com>
#            Qixiang Wan <qwan@redhat.com>

from tests import UrsaMajorTestCase
from ursa_major.utils import mmd_has_requires
from tests import make_mmd


class TestMmdHasRequires(UrsaMajorTestCase):
    def test_mmd_has_neg_requires(self):
        requires = {'platform': 'f26'}
        mmd = make_mmd('testmodule', 'master', '123', '00000000', requires)
        check_requires = {'platform': '-f26'}
        result = mmd_has_requires(mmd, check_requires)
        self.assertFalse(result)

    def test_mmd_missing_requires(self):
        requires = {'platform': 'f28'}
        mmd = make_mmd('testmodule', 'master', '123', '00000000', requires)
        check_requires = {'platform': 'f28', 'python3': 'master'}
        result = mmd_has_requires(mmd, check_requires)
        self.assertFalse(result)

    def test_mmd_not_has_neg_requires(self):
        requires = {'platform': 'f28', 'python3': 'master'}
        mmd = make_mmd('testmodule', 'master', '123', '00000000', requires)
        check_requires = {'platform': '-f26', 'python3': 'master'}
        result = mmd_has_requires(mmd, check_requires)
        self.assertTrue(result)

    def test_mmd_does_not_has_pos_requires(self):
        requires = {'platform': 'f28', 'python3': 'master'}
        mmd = make_mmd('testmodule', 'master', '123', '00000000', requires)
        check_requires = {'platform': 'f28', 'python3': 'f28'}
        result = mmd_has_requires(mmd, check_requires)
        self.assertFalse(result)

    def test_mmd_has_more_requires_than_checks(self):
        requires = {'platform': 'f28', 'python3': 'master'}
        mmd = make_mmd('testmodule', 'master', '123', '00000000', requires)
        check_requires = {'platform': 'f28'}
        result = mmd_has_requires(mmd, check_requires)
        self.assertTrue(result)

    def test_mmd_has_more_require_streams_than_checks(self):
        requires = {'platform': ['f28', 'f29'], 'python3': 'master'}
        mmd = make_mmd('testmodule', 'master', '123', '00000000', requires)
        check_requires = {'platform': 'f28'}
        result = mmd_has_requires(mmd, check_requires)
        self.assertTrue(result)

    def test_mmd_has_a_neg_stream_in_streams_list(self):
        requires = {'platform': ['f28', 'f29'], 'python3': 'master'}
        mmd = make_mmd('testmodule', 'master', '123', '00000000', requires)
        check_requires = {'platform': '-f28'}
        result = mmd_has_requires(mmd, check_requires)
        self.assertFalse(result)

    def test_mmd_has_a_neg_stream_in_multi_neg_streams(self):
        requires = {'platform': ['f27'], 'python3': 'master'}
        mmd = make_mmd('testmodule', 'master', '123', '00000000', requires)
        check_requires = {'platform': ['-f26', '-f27']}
        result = mmd_has_requires(mmd, check_requires)
        self.assertFalse(result)

    def test_check_with_empty_requires(self):
        requires = {'platform': ['f27'], 'python3': 'master'}
        mmd = make_mmd('testmodule', 'master', '123', '00000000', requires)
        result = mmd_has_requires(mmd, {})
        self.assertTrue(result)
