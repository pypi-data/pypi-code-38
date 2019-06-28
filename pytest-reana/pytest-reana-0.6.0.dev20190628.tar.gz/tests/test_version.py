# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REANA-pytest-Commmons tests."""

from __future__ import absolute_import, print_function


def test_version():
    """Test version import."""
    from pytest_reana import __version__
    assert __version__
