#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# (c) Copyright 2018 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import sys
import platform as orig_platform
from os.path import exists as orig_exists

try:  # Python2
    from __builtin__ import open as orig_open
except ImportError:  # Python3
    from builtins import open as orig_open

try:  # Python3
    from urllib.request import urlopen as orig_urlopen
except ImportError:  # Python2
    from urllib2 import urlopen as orig_urlopen


class MockPlatform():
    '''
    Mock implementation of platform module.
    '''

    def __init__(self):
        self._system = 'Linux'
        self._linux_dist_short = ('Ubuntu', '16.04', 'xenial')
        self._machine = 'x86_64'

    def system(self):
        return self._system

    def linux_distribution(self, full_distribution_name=True):
        return self._linux_dist_short

    def mac_ver(self):
        return self._linux_dist_short

    def win32_ver(self):
        return self._linux_dist_short

    def machine(self):
        return self._machine


class MockOpen():
    '''
    Mock open function to hijack read of some system files.
    '''

    def __init__(self):
        self._overrides = {}

    def __call__(self, *args, **kwargs):
        from io import StringIO
        try:
            from io import BytesIO
        except ImportError:
            BytesIO = StringIO

        if args[0] in self._overrides:
            data = self._overrides[args[0]]
            if data is None:
                raise IOError('file not found')
            if isinstance(data, bytes):
                return BytesIO(data)
            else:
                return StringIO(data)
        else:
            return orig_open(*args, **kwargs)


def setup_open():
    try:
        import __builtin__
    except ImportError:
        import builtins as __builtin__
    __builtin__.open = MockOpen()

    def mock_exists(path):
        if path in open._overrides:
            return open._overrides[path] is not None
        else:
            return orig_exists(path)

    import os.path
    os.path.exists = mock_exists


def teardown_open():
    try:
        import __builtin__
    except ImportError:
        import builtins as __builtin__
    __builtin__.open = orig_open
    import os.path
    os.path.exists = orig_exists


def setup_urlopen():
    try:
        import urllib.request as module
    except ImportError:
        import urllib2 as module
    module.urlopen = MockOpen()


def teardown_urlopen():
    try:
        import urllib.request as module
    except ImportError:
        import urllib2 as module
    module.urlopen = orig_urlopen


def setup_platform():
    sys.modules['platform'] = MockPlatform()


def teardown_platform():
    sys.modules['platform'] = orig_platform


def setup_all():
    setup_open()
    setup_urlopen()
    setup_platform()


def teardown_all():
    teardown_open()
    teardown_urlopen()
    teardown_platform()
