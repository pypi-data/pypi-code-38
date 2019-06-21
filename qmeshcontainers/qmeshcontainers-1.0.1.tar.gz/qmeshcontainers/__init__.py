#!/usr/bin/env python

#    Copyright (C) 2013 Alexandros Avdis and others.
#    See the AUTHORS.md file for a full list of copyright holders.
#
#    This file is part of qmesh-containers.
#
#    qmesh-containers is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    qmesh-containers is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with qmesh-containers.  If not, see <http://www.gnu.org/licenses/>.
'''Module containing command-line utility for creating qmesh Docker containers
'''

import pkg_resources
#Set the version attribute
try:
    __packaged_distro__ = pkg_resources.get_distribution('setuptools_qmesh')
    __version__ = __packaged_distro__.version
    del __packaged_distro__
except (pkg_resources.DistributionNotFound, AttributeError):
    __version__ = None
