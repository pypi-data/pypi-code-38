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

__all__ = ["__author__", "__description__", "__license__", "__url__", "__version__"]


def git_describe():
    import subprocess

    try:
        # git describe?
        out = subprocess.check_output(["git", "describe"], stderr=subprocess.STDOUT)
        return out.decode("utf-8").rstrip("\n")[1:]
    except Exception:
        return "git"


__author__ = "Rémi Duraffort"
__description__ = "LAVA XML-RPC command line interface"
__license__ = "AGPLv3+"
__url__ = "https://git.lavasoftware.org/lava/lavacli"
__version__ = "0.9.6"
