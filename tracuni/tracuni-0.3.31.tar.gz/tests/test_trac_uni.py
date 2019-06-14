#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `trac_uni` package."""

import pytest

from click.testing import CliRunner
from tracuni.trac_uni import main


# pytest.skip('skipping {} tests'.format(__name__), allow_module_level=True)


@pytest.fixture
def argument():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    from tracuni.trac_uni import cube_primitive_test
    value = 2
    return value, cube_primitive_test


def test_content(argument):
    """Sample pytest test function with the pytest fixture as an argument."""
    value, fn = argument
    fn(value)


@pytest.fixture
def runner():
    return CliRunner()


def test_main(runner):
    result = runner.invoke(main)

    assert result.exit_code == 0
    assert 'Demo app for trac uni package' in result.output
    assert '2 x 2 = 4\n' in result.output

    help_result = runner.invoke(main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output
