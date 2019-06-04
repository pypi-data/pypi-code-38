# -*- coding: utf-8 -*-
# vim: set ts=4

# Copyright 2018 Rémi Duraffort
# This file is part of lavacli.
#
# lavacli is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# lavacli is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with lavacli.  If not, see <http://www.gnu.org/licenses/>

import sys
import xmlrpc.client

from lavacli import main
from lavacli.__about__ import __version__


def test_lavacli_version(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "--version"])

    assert main() == 0  # nosec
    assert capsys.readouterr()[0] == "lavacli %s\n" % __version__  # nosec


def test_lavacli_missing_arguments(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "--help"])
    assert main() == 0  # nosec
    help_out = capsys.readouterr()[0]

    monkeypatch.setattr(sys, "argv", ["lavacli"])
    assert main() == 1  # nosec
    assert capsys.readouterr()[0] == help_out  # nosec


def test_lavacli_wrong_identity(setup, monkeypatch, capsys):
    version = "2018.4"
    monkeypatch.setattr(sys, "argv", ["lavacli", "-i", "bla", "devices" "list"])

    assert main() == 1  # nosec
    assert capsys.readouterr()[0] == "Unknown identity 'bla'\n"  # nosec
