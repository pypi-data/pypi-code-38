#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT plugin for managing raw XML log
# Copyright (C) 2009-2016  Jérôme Poisson (goffi@goffi.org)

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
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.core.constants import Const as C
import json

PLUGIN_INFO = {
    C.PI_NAME: "Debug Plugin",
    C.PI_IMPORT_NAME: "DEBUG",
    C.PI_TYPE: "Misc",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: [],
    C.PI_MAIN: "Debug",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""Set of method to make development and debugging easier"""),
}


class Debug(object):
    def __init__(self, host):
        log.info(_("Plugin Debug initialization"))
        self.host = host
        host.bridge.addMethod(
            "debugFakeSignal",
            ".plugin",
            in_sign="sss",
            out_sign="",
            method=self._fakeSignal,
        )

    def _fakeSignal(self, signal, arguments, profile_key):
        """send a signal from backend

        @param signal(str): name of the signal
        @param arguments(unicode): json encoded list of arguments
        @parm profile_key(unicode): profile_key to use or C.PROF_KEY_NONE if profile is not needed
        """
        args = json.loads(arguments)
        method = getattr(self.host.bridge, signal)
        if profile_key != C.PROF_KEY_NONE:
            profile = self.host.memory.getProfileName(profile_key)
            args.append(profile)
        method(*args)
