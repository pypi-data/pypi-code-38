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

"""This module manage configuration specific to Primitivus"""

from sat_frontends.primitivus.constants import Const as C
from sat_frontends.primitivus.keys import action_key_map
import ConfigParser


def applyConfig(host):
    """Parse configuration and apply found change

    raise: can raise various Exceptions if configuration is not good
    """
    config = ConfigParser.SafeConfigParser()
    config.read(C.CONFIG_FILES)
    try:
        options = config.items(C.CONFIG_SECTION)
    except ConfigParser.NoSectionError:
        options = []
    shortcuts = {}
    for name, value in options:
        if name.startswith(C.CONFIG_OPT_KEY_PREFIX.lower()):
            action = name[len(C.CONFIG_OPT_KEY_PREFIX) :].upper()
            shortcut = value
            if not action or not shortcut:
                raise ValueError("Bad option: {} = {}".format(name, value))
            shortcuts[action] = shortcut
        if name == "disable_mouse":
            host.loop.screen.set_mouse_tracking(False)

    action_key_map.replace(shortcuts)
    action_key_map.check_namespaces()
