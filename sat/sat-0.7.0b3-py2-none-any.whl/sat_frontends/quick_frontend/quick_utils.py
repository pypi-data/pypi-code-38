#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Primitivus: a SAT frontend
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from sat.core.i18n import _
from os.path import exists, splitext
from optparse import OptionParser


def getNewPath(path):
    """ Check if path exists, and find a non existant path if needed """
    idx = 2
    if not exists(path):
        return path
    root, ext = splitext(path)
    while True:
        new_path = "%s_%d%s" % (root, idx, ext)
        if not exists(new_path):
            return new_path
        idx += 1


def check_options():
    """Check command line options"""
    usage = _(
        """
    %prog [options]

    %prog --help for options list
    """
    )
    parser = OptionParser(usage=usage)  # TODO: use argparse

    parser.add_option("-p", "--profile", help=_("Select the profile to use"))

    (options, args) = parser.parse_args()
    if options.profile:
        options.profile = options.profile.decode("utf-8")
    return options
