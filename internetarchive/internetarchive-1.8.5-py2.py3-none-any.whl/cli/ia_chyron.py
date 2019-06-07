# -*- coding: utf-8 -*-
#
# The internetarchive module is a Python/CLI interface to Archive.org.
#
# Copyright (C) 2012-2016 Internet Archive
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""This is an `ia` plugin for the "Third Eye: API for TV News Archive chyrons".

API docs: https://archive.org/services/third-eye.php

usage:
    ia chyron <identifier>

options:
    -h, --help
    -v, --verbose               Print column headers. [default: False]
"""
import sys
import csv
from itertools import chain
from fnmatch import fnmatch
import six

from docopt import docopt


def main(argv, session):
    args = docopt(__doc__, argv=argv)

    url = '{}archive.org/services/third-eye.php'.format(session.protocol)
    p = dict(last=3)
    r = session.get(url, params=p)
    print(r.content.decode('utf-8'))
