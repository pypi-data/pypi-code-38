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

import sys


class ANSI(object):

    ## ANSI escape sequences ##
    RESET = "\033[0m"
    NORMAL_WEIGHT = "\033[22m"
    FG_BLACK, FG_RED, FG_GREEN, FG_YELLOW, FG_BLUE, FG_MAGENTA, FG_CYAN, FG_WHITE = (
        "\033[3%dm" % nb for nb in xrange(8)
    )
    BOLD = "\033[1m"
    BLINK = "\033[5m"
    BLINK_OFF = "\033[25m"

    @classmethod
    def color(cls, *args):
        """output text using ANSI codes

        this method simply merge arguments, and add RESET if is not the last arguments
        """
        # XXX: we expect to have at least one argument
        if args[-1] != cls.RESET:
            args = list(args)
            args.append(cls.RESET)
        return u"".join(args)


try:
    tty = sys.stdout.isatty()
except (
    AttributeError,
    TypeError,
):  # FIXME: TypeError is here for Pyjamas, need to be removed
    tty = False
if not tty:
    #  we don't want ANSI escape codes if we are not outputing to a tty!
    for attr in dir(ANSI):
        if isinstance(getattr(ANSI, attr), basestring):
            setattr(ANSI, attr, u"")
del tty
