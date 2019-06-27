#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT: a XMPP client
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

from sat.core import constants


class Const(constants.Const):

    NAME = u"bridge_constructor"
    DEST_DIR_DEFAULT = "generated"
    DESCRIPTION = u"""{name} Copyright (C) 2009-2019 Jérôme Poisson (aka Goffi)

    This script construct a SàT bridge using the given protocol

    This program comes with ABSOLUTELY NO WARRANTY;
    This is free software, and you are welcome to redistribute it
    under certain conditions.
    """.format(
        name=NAME, version=constants.Const.APP_VERSION
    )
    #  TODO: move protocoles in separate files (plugins?)
    DEFAULT_PROTOCOLE = "dbus"

    # flags used method/signal declaration (not to be confused with constructor flags)
    DECLARATION_FLAGS = ["deprecated", "async"]

    ENV_OVERRIDE = "SAT_BRIDGE_CONST_"  # Prefix used to override a constant
