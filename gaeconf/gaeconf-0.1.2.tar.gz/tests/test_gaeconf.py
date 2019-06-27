#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `gaeconf` package."""

import pytest
from unittest.mock import patch, mock_open
from click.testing import CliRunner

from gaeconf import gaeconf
from gaeconf import cli

@pytest.fixture()
def env_vars(monkeypatch):
    monkeypatch.setenv('CUSTOM_ENV', 'some-value')
    monkeypatch.setenv('ANOTHER_ENV', '1234')


def test_yaml_output():
    """Tests simple run of gaeconf."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ['-m', 'tests/example.yaml', '-s', 'backend-staging'])
    assert "automatic_scaling" in result.stdout
    assert "python_version: '3.7'" in result.stdout


def test_yaml_output_with_overriden_host_env_variables(env_vars):
    """Tests simple run of gaeconf."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ['-m', 'tests/example.yaml', '-s', 'backend-staging', '-e', 'CUSTOM_ENV', '-e', 'ANOTHER_ENV'])
    assert "automatic_scaling" in result.stdout
    assert "CUSTOM_ENV: some-value" in result.stdout
    assert "ANOTHER_ENV: '1234'" in result.stdout
 

def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 2
    assert 'Usage: main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert 'GAE service name  [required]' in help_result.output
