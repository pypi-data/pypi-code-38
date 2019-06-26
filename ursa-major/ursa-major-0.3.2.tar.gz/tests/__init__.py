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

import math
import os
import json
try:
    import unittest2 as unittest
except ImportError:
    import unittest


from ursa_major.utils import Modulemd
from six.moves.configparser import ConfigParser

TESTS_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DATA_DIR = os.path.join(TESTS_DIR, 'test_data')

CONFIG_FILE = os.path.join(TEST_DATA_DIR, 'ursa-major-test.conf')
URSA_MAJOR_TEST_CONFIG = ConfigParser()
URSA_MAJOR_TEST_CONFIG.read(CONFIG_FILE)


def make_mmd(name, stream, version, context, requires=None, buildrequires=None):
    """Creates new Modulemd.Module instance

    :param name: module name
    :param stream: module stream
    :param version: module version
    :param context: module context
    :param requires: Dict of requires, example:
        {'platform': ['rhel-8.0'], 'python3': 'master'}
    :param buildrequires: Dict of build_requires, example:
        {'platform': 'rhel-8.0', 'bootstrap': ['rhel-8.0']}
    :rtype: Modulemd.Module instance
    """
    mmd = Modulemd.Module()
    mmd.set_name(name)
    mmd.set_stream(stream)
    mmd.set_version(int(version))
    mmd.set_context(context)
    # required options
    mmd.set_mdversion(2)
    mmd.set_summary("A test module in all its beautiful beauty.")
    description = ("This module demonstrates how to write simple "
                   "modulemd files And can be used for testing "
                   "the build and release pipeline.")
    mmd.set_description(description)
    licenses = Modulemd.SimpleSet()
    licenses.add("GPL")
    mmd.set_module_licenses(licenses)

    deps_list = []
    requires = requires or {}
    buildrequires = buildrequires or {}

    deps = Modulemd.Dependencies()
    for req_name, req_streams in requires.items():
        if not isinstance(req_streams, list):
            req_streams = [req_streams]
        deps.add_requires(req_name, req_streams)

    for req_name, req_streams in buildrequires.items():
        if not isinstance(req_streams, list):
            req_streams = [req_streams]
        deps.add_buildrequires(req_name, req_streams)
    deps_list.append(deps)
    mmd.set_dependencies(deps_list)

    return mmd


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


class UrsaMajorTestCase(unittest.TestCase):
    def load_json_from_file(self, filename):
        test_data_file = os.path.join(TEST_DATA_DIR, filename)
        with open(test_data_file, 'r') as f:
            return json.load(f)


class MockMBSBuildsData(object):
    def __init__(self, module_builds, per_page=2):
        self.module_builds = module_builds
        self.total = len(module_builds)
        self.per_page = per_page

    def _page_url(self, page_number):
        return (
            'https://mbs.example.com/module-build-service/1/module-builds/'
            '?per_page={}&page={}'.format(self.per_page, page_number)
        )

    def get(self, url, **kwargs):
        params = kwargs.get('params', {})
        q_page = params.get('page', None)
        q_per_page = params.get('per_page', None)

        page = q_page or 1

        if q_per_page is not None:
            self.per_page = q_per_page
        pages = int(math.ceil(float(self.total)/float(self.per_page)))

        start = self.per_page * (page - 1)
        stop = self.per_page * page
        modules = self.module_builds[start:stop]

        next_page_url = None
        if pages > page:
            next_page_url = self._page_url(page + 1)

        prev_page_url = None
        if page > 1:
            prev_page_url = self._page_url(page - 1)

        json_data = {
            'items': modules,
            'meta': {
                'first': self._page_url(1),
                'last': self._page_url(pages),
                'next': next_page_url,
                'page': page,
                'pages': pages,
                'per_page': self.per_page,
                'prev': prev_page_url,
                'total': self.total
            }
        }
        return MockResponse(json_data, 200)
