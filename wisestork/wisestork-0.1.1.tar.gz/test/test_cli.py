#    Copyright (C) 2016-2019  Sander Bollen
#
#    This file is part of wisestork
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see {http://www.gnu.org/licenses/}.

from click.testing import CliRunner
import pytest

from wisestork.wisestork import count_cli, gcc_cli, newref_cli, zscore_cli


@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_count_help(runner):
    result = runner.invoke(count_cli, "--help")
    assert result.exit_code == 0


def test_cli_gc_correct_help(runner):
    result = runner.invoke(gcc_cli, "--help")
    assert result.exit_code == 0


def test_cli_newref_help(runner):
    result = runner.invoke(newref_cli, "--help")
    assert result.exit_code == 0


def test_cli_zscore_help(runner):
    result = runner.invoke(zscore_cli, "--help")
    assert result.exit_code == 0
