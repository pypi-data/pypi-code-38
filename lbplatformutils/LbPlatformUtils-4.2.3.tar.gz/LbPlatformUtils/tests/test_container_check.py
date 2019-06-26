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
from __future__ import print_function

import os
from contextlib import contextmanager

try:
    from unittest import mock
except ImportError:
    import mock

try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory


@contextmanager
def reroot_cvm(root):
    from LbPlatformUtils import inspect
    try:
        bkup = inspect.SINGULARITY_ROOTS
        inspect.SINGULARITY_ROOTS = [
            (os.path.join(root, os.path.basename(path)), os_id)
            for path, os_id in inspect.SINGULARITY_ROOTS
        ]
        yield
    finally:
        inspect.SINGULARITY_ROOTS = bkup


def test_singularity():
    from LbPlatformUtils import inspect
    with TemporaryDirectory() as temp_dir:
        os.environ['PATH'] = temp_dir + os.pathsep + os.environ['PATH']
        # Write a test singularity "binary" which just echos it's arguments
        with open(os.path.join(temp_dir, 'singularity'), 'wb') as script:
            script.writelines([b'#!/bin/sh\n',
                               b'echo "$@"\n',
                               b'exit ${TEST_SING_EXIT:-0}\n'])
        os.chmod(os.path.join(temp_dir, 'singularity'), 0o775)
        os.mkdir(os.path.join(temp_dir, 'cvm4'))
        os.mkdir(os.path.join(temp_dir, 'cvm3'))
        with reroot_cvm(temp_dir):
            # test no singularity
            os.environ['TEST_SING_EXIT'] = '1'
            assert inspect.singularity_os_ids() == []

            del os.environ['TEST_SING_EXIT']
            assert inspect.singularity_os_ids() == inspect.SINGULARITY_ROOTS

            from LbPlatformUtils import get_viable_containers
            from LbPlatformUtils.describe import platform_info
            assert 'singularity' in get_viable_containers(
                platform_info(), 'x86_64-slc6-gcc49-opt')

            from LbPlatformUtils import dirac_platform
            from LbPlatformUtils.inspect import architecture
            arch = architecture()
            assert '-'.join([arch, 'any']) != dirac_platform()
            assert '-'.join([arch, 'any']) != dirac_platform(allow_containers=False)
            assert '-'.join([arch, 'any']) == dirac_platform(allow_containers=True)

            with mock.patch('os.path.expanduser', return_value='/a/missing/home/directory'):
                assert inspect.singularity_os_ids() == inspect.SINGULARITY_ROOTS

            # Singularity is unable to bind the a home directory if it doesn't
            # belong to the current user (this applies on some grid nodes)
            # Explicitly test for this
            class PatchedStat():
                def __init__(self, spec):
                    self.spec = spec

                def __call__(self, path):
                    if path.startswith(os.path.expanduser('~')):
                        # Return an ~impossible user ID
                        return os.stat_result([999999999999999999999]*10)
                    else:
                        return self.spec(path)

            class PatchedCheckOutput():
                def __init__(self, spec, expected_arg=None):
                    assert expected_arg is not None
                    self.expected_arg = expected_arg
                    self.spec = spec

                def __call__(self, cmd_args, *args, **kwargs):
                    assert self.expected_arg in cmd_args
                    return self.spec(cmd_args, *args, **kwargs)

            with mock.patch('LbPlatformUtils.inspect.check_output',
                            new_callable=PatchedCheckOutput,
                            spec=True, expected_arg='--home'):
                assert inspect.singularity_os_ids() == inspect.SINGULARITY_ROOTS

            with mock.patch('LbPlatformUtils.inspect.check_output',
                            new_callable=PatchedCheckOutput,
                            spec=True, expected_arg='--no-home'):
                with mock.patch('os.stat', new_callable=PatchedStat, spec=True):
                    assert inspect.singularity_os_ids() == inspect.SINGULARITY_ROOTS
