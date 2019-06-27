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
from sat_frontends.jp import common
from sat.tools.common.ansi import ANSI as A
from functools import partial
import codecs
import json

__commands__ = ["Forums"]

FORUMS_TMP_DIR = u"forums"


class Edit(base.CommandBase, common.BaseEdit):
    use_items = False

    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "edit",
            use_pubsub=True,
            use_draft=True,
            use_verbose=True,
            help=_(u"edit forums"),
        )
        common.BaseEdit.__init__(self, self.host, FORUMS_TMP_DIR)
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "-k",
            "--key",
            type=base.unicode_decoder,
            default=u"",
            help=_(u"forum key (DEFAULT: default forums)"),
        )

    def getTmpSuff(self):
        """return suffix used for content file"""
        return u"json"

    def forumsSetCb(self):
        self.disp(_(u"forums have been edited"), 1)
        self.host.quit()

    def publish(self, forums_raw):
        self.host.bridge.forumsSet(
            forums_raw,
            self.args.service,
            self.args.node,
            self.args.key,
            self.profile,
            callback=self.forumsSetCb,
            errback=partial(
                self.errback,
                msg=_(u"can't set forums: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )

    def forumsGetCb(self, forums_json):
        content_file_obj, content_file_path = self.getTmpFile()
        forums_json = forums_json.strip()
        if forums_json:
            # we loads and dumps to have pretty printed json
            forums = json.loads(forums_json)
            # cf. https://stackoverflow.com/a/18337754
            f = codecs.getwriter("utf-8")(content_file_obj)
            json.dump(forums, f, ensure_ascii=False, indent=4)
            content_file_obj.seek(0)
        self.runEditor("forums_editor_args", content_file_path, content_file_obj)

    def forumsGetEb(self, failure_):
        # FIXME: error handling with bridge is broken, need to be properly fixed
        if failure_.condition == u"item-not-found":
            self.forumsGetCb(u"")
        else:
            self.errback(
                failure_,
                msg=_(u"can't get forums structure: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            )

    def start(self):
        self.host.bridge.forumsGet(
            self.args.service,
            self.args.node,
            self.args.key,
            self.profile,
            callback=self.forumsGetCb,
            errback=self.forumsGetEb,
        )


class Get(base.CommandBase):
    def __init__(self, host):
        extra_outputs = {"default": self.default_output}
        base.CommandBase.__init__(
            self,
            host,
            "get",
            use_output=C.OUTPUT_COMPLEX,
            extra_outputs=extra_outputs,
            use_pubsub=True,
            use_verbose=True,
            help=_(u"get forums structure"),
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "-k",
            "--key",
            type=base.unicode_decoder,
            default=u"",
            help=_(u"forum key (DEFAULT: default forums)"),
        )

    def default_output(self, forums, level=0):
        for forum in forums:
            keys = list(forum.keys())
            keys.sort()
            try:
                keys.remove(u"title")
            except ValueError:
                pass
            else:
                keys.insert(0, u"title")
            try:
                keys.remove(u"sub-forums")
            except ValueError:
                pass
            else:
                keys.append(u"sub-forums")

            for key in keys:
                value = forum[key]
                if key == "sub-forums":
                    self.default_output(value, level + 1)
                else:
                    if self.host.verbosity < 1 and key != u"title":
                        continue
                    head_color = C.A_LEVEL_COLORS[level % len(C.A_LEVEL_COLORS)]
                    self.disp(
                        A.color(level * 4 * u" ", head_color, key, A.RESET, u": ", value)
                    )

    def forumsGetCb(self, forums_raw):
        if not forums_raw:
            self.disp(_(u"no schema found"), 1)
            self.host.quit(1)
        forums = json.loads(forums_raw)
        self.output(forums)
        self.host.quit()

    def start(self):
        self.host.bridge.forumsGet(
            self.args.service,
            self.args.node,
            self.args.key,
            self.profile,
            callback=self.forumsGetCb,
            errback=partial(
                self.errback,
                msg=_(u"can't get forums: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class Forums(base.CommandBase):
    subcommands = (Get, Edit)

    def __init__(self, host):
        super(Forums, self).__init__(
            host, "forums", use_profile=False, help=_(u"Forums structure edition")
        )
