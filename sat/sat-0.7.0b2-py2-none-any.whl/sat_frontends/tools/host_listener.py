#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
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

"""This module is only used launch callbacks when host is ready, used for early initialisation stuffs"""


listeners = []


def addListener(cb):
    """Add a listener which will be called when host is ready

    @param cb: callback which will be called when host is ready with host as only argument
    """
    listeners.append(cb)


def callListeners(host):
    """Must be called by frontend when host is ready.

    The call will launch all the callbacks, then remove the listeners list.
    @param host(QuickApp): the instancied QuickApp subclass
    """
    global listeners
    while True:
        try:
            cb = listeners.pop(0)
            cb(host)
        except IndexError:
            break
    del listeners
