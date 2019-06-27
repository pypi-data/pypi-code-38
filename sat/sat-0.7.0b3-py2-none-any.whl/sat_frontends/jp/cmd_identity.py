#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# jp: a SàT command line tool
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
from sat_frontends.jp.constants import Const as C
from functools import partial

__commands__ = ["Identity"]

# TODO: move date parsing to base, it may be useful for other commands


class Get(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "get",
            use_output=C.OUTPUT_DICT,
            use_verbose=True,
            help=_(u"get identity data"),
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "jid", type=base.unicode_decoder, help=_(u"entity to check")
        )

    def identityGetCb(self, data):
        self.output(data)
        self.host.quit()

    def start(self):
        jid_ = self.host.check_jids([self.args.jid])[0]
        self.host.bridge.identityGet(
            jid_,
            self.profile,
            callback=self.identityGetCb,
            errback=partial(
                self.errback,
                msg=_(u"can't get identity data: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class Set(base.CommandBase):
    def __init__(self, host):
        super(Set, self).__init__(host, "set", help=_("modify an existing event"))

    def add_parser_options(self):
        self.parser.add_argument(
            "-f",
            "--field",
            type=base.unicode_decoder,
            action="append",
            nargs=2,
            dest="fields",
            metavar=(u"KEY", u"VALUE"),
            required=True,
            help=_(u"identity field(s) to set"),
        )
        self.need_loop = True

    def start(self):
        fields = dict(self.args.fields)
        self.host.bridge.identitySet(
            fields,
            self.profile,
            callback=self.host.quit,
            errback=partial(
                self.errback,
                msg=_(u"can't set identity data data: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class Identity(base.CommandBase):
    subcommands = (Get, Set)

    def __init__(self, host):
        super(Identity, self).__init__(
            host, "identity", use_profile=False, help=_("identity management")
        )
