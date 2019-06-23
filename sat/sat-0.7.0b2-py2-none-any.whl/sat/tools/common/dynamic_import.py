#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT: a XMPP
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

""" tools dynamic import """

from importlib import import_module


def bridge(name, module_path="sat.bridge"):
    """Import bridge module

    @param module_path(str): path of the module to import
    @param name(str): name of the bridge to import (e.g.: dbus)
    @return (module, None): imported module or None if nothing is found
    """
    try:
        bridge_module = import_module(module_path + "." + name)
    except ImportError:
        try:
            bridge_module = import_module(module_path + "." + name + "_bridge")
        except ImportError:
            bridge_module = None
    return bridge_module
