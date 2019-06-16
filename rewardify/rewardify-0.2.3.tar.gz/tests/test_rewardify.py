#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `rewardify` package.

import pytest

from click.testing import CliRunner

from rewardify import rewardify_base
from rewardify import cli


@pytest.fixture
def response():

    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):

    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'rewardify.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output
"""
