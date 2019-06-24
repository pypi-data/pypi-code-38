#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `amt` package."""


import unittest
from click.testing import CliRunner

from amt import amt
from amt import cli


class TestAmtool(unittest.TestCase):
    """Tests for `amtool` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        # assert 'amt.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert 'Show this message and exit.' in help_result.output
