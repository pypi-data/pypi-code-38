# Copyright (C) 2018-2019  The Plenpy Authors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""The main package of plenpy.

Plenpy is a package that, at its core, provides an abstract camera module to
implement and work with camera models as well as a state-of-the-art
light field module.

"""
import pkg_resources  # part of setuptools

__version__ = pkg_resources.require("plenpy")[0].version
__author__ = "Maximilian Schambach"

import plenpy.logg

logger = plenpy.logg.get_logger()
