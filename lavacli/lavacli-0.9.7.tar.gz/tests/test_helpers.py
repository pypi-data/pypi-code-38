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

from lavacli.utils import parse_version, VERSION_LATEST


def test_parse_version():
    assert parse_version("2018.5.post1-2~bpo9+1.1debian9.1") == (2018, 5)  # nosec
    assert parse_version("2018.5.post1-1+stretch") == (2018, 5)  # nosec
    assert parse_version("2018.4-1-1") == (2018, 4)  # nosec
    assert parse_version("2018.4.post2-1+stretch") == (2018, 4)  # nosec
    assert parse_version("2019.01.post2-1+stretch") == (2019, 1)  # nosec


def test_parse_version_errors():
    assert parse_version(1) == VERSION_LATEST  # nosec
    assert parse_version("201812") == VERSION_LATEST  # nosec
