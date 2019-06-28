# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA-pytest-Commmons test fixtures."""


from __future__ import absolute_import, print_function

import os

import pytest


def test_tmp_shared_volume_path_fixture(testdir):
    """Make sure that pytest accepts our fixture."""

    # create a temporary pytest test module
    testdir.makepyfile("""
        def test_sth(tmp_shared_volume_path):
            import os
            os.path.exists(tmp_shared_volume_path)
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest()
    testdir.runpytest().assert_outcomes(passed=1)
