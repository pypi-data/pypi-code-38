#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `glb` package."""

import pytest  # noqa: F401

from click.testing import CliRunner

from glb.glb import my_groups
from glb import cli


def test_my_groups():
    # TODO mock endpoint instead of calling directly
    r = my_groups()
    assert r.status_code == 200


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert "glb" in result.output
    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0
    assert "--help  Show this message and exit." in help_result.output
