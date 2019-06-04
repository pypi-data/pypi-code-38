# -*- coding: utf-8 -*-
# vim: set ts=4

# Copyright 2017 Rémi Duraffort
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

import re
import xmlrpc.client
import yaml


def print_u(string):
    try:
        print(string)
    except UnicodeEncodeError:
        print(string.encode("ascii", errors="replace").decode("ascii"))


VERSION_LATEST = (3000, 1)


def parse_version(version):
    pattern = re.compile(r"(?P<major>20\d{2})\.(?P<minor>\d{1,2})")
    if not isinstance(version, str):
        version = str(version)
    m = pattern.match(version)
    if m is None:
        return VERSION_LATEST
    res = m.groupdict()
    return (int(res["major"]), int(res["minor"]))


def loader(safe=True):
    try:
        return yaml.CSafeLoader if safe else yaml.CLoader
    except AttributeError:
        # TODO log a warning on stderr
        return yaml.SafeLoader if safe else yaml.Loader


def exc2str(exc):
    if isinstance(exc, xmlrpc.client.ProtocolError):
        return exc.errmsg
    return str(exc)
