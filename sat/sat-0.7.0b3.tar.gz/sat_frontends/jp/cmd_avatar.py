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
import os
import os.path
from sat.core.i18n import _
from sat_frontends.jp.constants import Const as C
from sat.tools import config
import subprocess


__commands__ = ["Avatar"]
DISPLAY_CMD = ["xv", "display", "gwenview", "showtell"]


class Set(base.CommandBase):
    def __init__(self, host):
        super(Set, self).__init__(
            host, "set", use_verbose=True, help=_("set avatar of the profile")
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "image_path", type=str, help=_("path to the image to upload")
        )

    def start(self):
        """Send files to jabber contact"""
        path = self.args.image_path
        if not os.path.exists(path):
            self.disp(_(u"file [{}] doesn't exist !").format(path), error=True)
            self.host.quit(1)
        path = os.path.abspath(path)
        self.host.bridge.avatarSet(
            path, self.profile, callback=self._avatarCb, errback=self._avatarEb
        )

    def _avatarCb(self):
        self.disp(_("avatar has been set"), 1)
        self.host.quit()

    def _avatarEb(self, failure_):
        self.disp(
            _("error while uploading avatar: {msg}").format(msg=failure_), error=True
        )
        self.host.quit(C.EXIT_ERROR)


class Get(base.CommandBase):
    def __init__(self, host):
        super(Get, self).__init__(
            host, "get", use_verbose=True, help=_("retrieve avatar of an entity")
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument("jid", type=base.unicode_decoder, help=_("entity"))
        self.parser.add_argument(
            "-s", "--show", action="store_true", help=_(u"show avatar")
        )

    def showImage(self, path):
        sat_conf = config.parseMainConf()
        cmd = config.getConfig(sat_conf, "jp", "image_cmd")
        cmds = [cmd] + DISPLAY_CMD if cmd else DISPLAY_CMD
        for cmd in cmds:
            try:
                ret = subprocess.call([cmd] + [path])
            except OSError:
                pass
            else:
                if ret in (0, 2):
                    # we can get exit code 2 with display when stopping it with C-c
                    break
        else:
            # didn't worked with commands, we try our luck with webbrowser
            # in some cases, webbrowser can actually open the associated display program
            import webbrowser

            webbrowser.open(path)

    def _avatarGetCb(self, avatar_path):
        if not avatar_path:
            self.disp(_(u"No avatar found."), 1)
            self.host.quit(C.EXIT_NOT_FOUND)

        self.disp(avatar_path)
        if self.args.show:
            self.showImage(avatar_path)

        self.host.quit()

    def _avatarGetEb(self, failure_):
        self.disp(_("error while getting avatar: {msg}").format(msg=failure_), error=True)
        self.host.quit(C.EXIT_ERROR)

    def start(self):
        self.host.bridge.avatarGet(
            self.args.jid,
            False,
            False,
            self.profile,
            callback=self._avatarGetCb,
            errback=self._avatarGetEb,
        )


class Avatar(base.CommandBase):
    subcommands = (Set, Get)

    def __init__(self, host):
        super(Avatar, self).__init__(
            host, "avatar", use_profile=False, help=_("avatar uploading/retrieving")
        )
