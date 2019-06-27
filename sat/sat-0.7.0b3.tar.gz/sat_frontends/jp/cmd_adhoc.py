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
from functools import partial
from sat_frontends.jp.constants import Const as C
from sat_frontends.jp import xmlui_manager

__commands__ = ["AdHoc"]

FLAG_LOOP = "LOOP"
MAGIC_BAREJID = "@PROFILE_BAREJID@"


class Remote(base.CommandBase):
    def __init__(self, host):
        super(Remote, self).__init__(
            host, "remote", use_verbose=True, help=_(u"remote control a software")
        )

    def add_parser_options(self):
        self.parser.add_argument("software", type=str, help=_(u"software name"))
        self.parser.add_argument(
            "-j",
            "--jids",
            type=base.unicode_decoder,
            nargs="*",
            default=[],
            help=_(u"jids allowed to use the command"),
        )
        self.parser.add_argument(
            "-g",
            "--groups",
            type=base.unicode_decoder,
            nargs="*",
            default=[],
            help=_(u"groups allowed to use the command"),
        )
        self.parser.add_argument(
            "--forbidden-groups",
            type=base.unicode_decoder,
            nargs="*",
            default=[],
            help=_(u"groups that are *NOT* allowed to use the command"),
        )
        self.parser.add_argument(
            "--forbidden-jids",
            type=base.unicode_decoder,
            nargs="*",
            default=[],
            help=_(u"jids that are *NOT* allowed to use the command"),
        )
        self.parser.add_argument(
            "-l", "--loop", action="store_true", help=_(u"loop on the commands")
        )

    def start(self):
        name = self.args.software.lower()
        flags = []
        magics = {jid for jid in self.args.jids if jid.count("@") > 1}
        magics.add(MAGIC_BAREJID)
        jids = set(self.args.jids).difference(magics)
        if self.args.loop:
            flags.append(FLAG_LOOP)
        bus_name, methods = self.host.bridge.adHocDBusAddAuto(
            name,
            jids,
            self.args.groups,
            magics,
            self.args.forbidden_jids,
            self.args.forbidden_groups,
            flags,
            self.profile,
        )
        if not bus_name:
            self.disp(_("No bus name found"), 1)
            return
        self.disp(_("Bus name found: [%s]" % bus_name), 1)
        for method in methods:
            path, iface, command = method
            self.disp(
                _(
                    "Command found: (path:%(path)s, iface: %(iface)s) [%(command)s]"
                    % {"path": path, "iface": iface, "command": command}
                ),
                1,
            )


class Run(base.CommandBase):
    """Run an Ad-Hoc command"""

    def __init__(self, host):
        super(Run, self).__init__(
            host, "run", use_verbose=True, help=_(u"run an Ad-Hoc command")
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "-j",
            "--jid",
            type=base.unicode_decoder,
            default=u"",
            help=_(u"jid of the service (default: profile's server"),
        )
        self.parser.add_argument(
            "-S",
            "--submit",
            action="append_const",
            const=xmlui_manager.SUBMIT,
            dest="workflow",
            help=_(u"submit form/page"),
        )
        self.parser.add_argument(
            "-f",
            "--field",
            type=base.unicode_decoder,
            action="append",
            nargs=2,
            dest="workflow",
            metavar=(u"KEY", u"VALUE"),
            help=_(u"field value"),
        )
        self.parser.add_argument(
            "node",
            type=base.unicode_decoder,
            nargs="?",
            default=u"",
            help=_(u"node of the command (default: list commands)"),
        )

    def adHocRunCb(self, xmlui_raw):
        xmlui = xmlui_manager.create(self.host, xmlui_raw)
        workflow = self.args.workflow
        xmlui.show(workflow)
        if not workflow:
            if xmlui.type == "form":
                xmlui.submitForm()
            else:
                self.host.quit()

    def start(self):
        self.host.bridge.adHocRun(
            self.args.jid,
            self.args.node,
            self.profile,
            callback=self.adHocRunCb,
            errback=partial(
                self.errback,
                msg=_(u"can't get ad-hoc commands list: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class List(base.CommandBase):
    """Run an Ad-Hoc command"""

    def __init__(self, host):
        super(List, self).__init__(
            host, "list", use_verbose=True, help=_(u"list Ad-Hoc commands of a service")
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "-j",
            "--jid",
            type=base.unicode_decoder,
            default=u"",
            help=_(u"jid of the service (default: profile's server"),
        )

    def adHocListCb(self, xmlui_raw):
        xmlui = xmlui_manager.create(self.host, xmlui_raw)
        xmlui.readonly = True
        xmlui.show()
        self.host.quit()

    def start(self):
        self.host.bridge.adHocList(
            self.args.jid,
            self.profile,
            callback=self.adHocListCb,
            errback=partial(
                self.errback,
                msg=_(u"can't get ad-hoc commands list: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class AdHoc(base.CommandBase):
    subcommands = (Run, List, Remote)

    def __init__(self, host):
        super(AdHoc, self).__init__(
            host, "ad-hoc", use_profile=False, help=_("Ad-hoc commands")
        )
