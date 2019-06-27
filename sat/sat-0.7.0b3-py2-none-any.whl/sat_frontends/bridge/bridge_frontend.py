#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT communication bridge
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


class BridgeException(Exception):
    """An exception which has been raised from the backend and arrived to the frontend."""

    def __init__(self, name, message="", condition=""):
        """

        @param name (str): full exception class name (with module)
        @param message (str): error message
        @param condition (str) : error condition
        """
        Exception.__init__(self)
        self.fullname = unicode(name)
        self.message = unicode(message)
        self.condition = unicode(condition) if condition else ""
        self.module, __, self.classname = unicode(self.fullname).rpartition(".")

    def __str__(self):
        message = (": %s" % self.message) if self.message else ""
        return self.classname + message

    def __eq__(self, other):
        return self.classname == other
