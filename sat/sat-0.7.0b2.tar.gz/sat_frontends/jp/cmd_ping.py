#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# jp: a SAT command line tool
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

import base
from sat.core.i18n import _

__commands__ = ["Ping"]


class Ping(base.CommandBase):

    def __init__(self, host):
        super(Ping, self).__init__(host, 'ping', help=_('ping XMPP entity'))
        self.need_loop=True

    def add_parser_options(self):
        self.parser.add_argument(
            "jid", type=base.unicode_decoder, help=_(u"jid to ping")
        )
        self.parser.add_argument(
            "-d", "--delay-only", action="store_true", help=_(u"output delay only (in s)")
        )

    def _pingCb(self, pong_time):
        fmt = u"{time}" if self.args.delay_only else  u"PONG ({time} s)"
        self.disp(fmt.format(time=pong_time))
        self.host.quit()

    def start(self):
        self.host.bridge.ping(self.args.jid, self.profile,
            callback=self._pingCb, errback=self.errback)
