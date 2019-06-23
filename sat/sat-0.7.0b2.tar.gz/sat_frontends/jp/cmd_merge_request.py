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
from sat.tools.common import data_format
from sat_frontends.jp.constants import Const as C
from sat_frontends.jp import xmlui_manager
from sat_frontends.jp import common
from functools import partial
import os.path

__commands__ = ["MergeRequest"]


class Set(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "set",
            use_pubsub=True,
            pubsub_defaults={u"service": _(u"auto"), u"node": _(u"auto")},
            help=_(u"publish or update a merge request"),
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "-i",
            "--item",
            type=base.unicode_decoder,
            default=u"",
            help=_(u"id or URL of the request to update, or nothing for a new one"),
        )
        self.parser.add_argument(
            "-r",
            "--repository",
            metavar="PATH",
            type=base.unicode_decoder,
            default=u".",
            help=_(u"path of the repository (DEFAULT: current directory)"),
        )
        self.parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help=_(u"publish merge request without confirmation"),
        )
        self.parser.add_argument(
            "-l",
            "--label",
            dest="labels",
            type=base.unicode_decoder,
            action="append",
            help=_(u"labels to categorize your request"),
        )

    def mergeRequestSetCb(self, published_id):
        if published_id:
            self.disp(u"Merge request published at {pub_id}".format(pub_id=published_id))
        else:
            self.disp(u"Merge request published")
        self.host.quit(C.EXIT_OK)

    def sendRequest(self):
        extra = {"update": True} if self.args.item else {}
        values = {}
        if self.args.labels is not None:
            values[u"labels"] = self.args.labels
        self.host.bridge.mergeRequestSet(
            self.args.service,
            self.args.node,
            self.repository,
            u"auto",
            values,
            u"",
            self.args.item,
            data_format.serialise(extra),
            self.profile,
            callback=self.mergeRequestSetCb,
            errback=partial(
                self.errback,
                msg=_(u"can't create merge request: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )

    def askConfirmation(self):
        if not self.args.force:
            message = _(
                u"You are going to publish your changes to service [{service}], are you sure ?"
            ).format(service=self.args.service)
            self.host.confirmOrQuit(message, _(u"merge request publication cancelled"))
        self.sendRequest()

    def start(self):
        self.repository = os.path.expanduser(os.path.abspath(self.args.repository))
        common.URIFinder(self, self.repository, "merge requests", self.askConfirmation)


class Get(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "get",
            use_verbose=True,
            use_pubsub=True,
            pubsub_flags={C.MULTI_ITEMS},
            pubsub_defaults={u"service": _(u"auto"), u"node": _(u"auto")},
            help=_(u"get a merge request"),
        )
        self.need_loop = True

    def add_parser_options(self):
        pass

    def mergeRequestGetCb(self, requests_data):
        if self.verbosity >= 1:
            whitelist = None
        else:
            whitelist = {"id", "title", "body"}
        for request_xmlui in requests_data[0]:
            xmlui = xmlui_manager.create(self.host, request_xmlui, whitelist=whitelist)
            xmlui.show(values_only=True)
            self.disp(u"")
        self.host.quit(C.EXIT_OK)

    def getRequests(self):
        extra = {}
        self.host.bridge.mergeRequestsGet(
            self.args.service,
            self.args.node,
            self.args.max,
            self.args.items,
            u"",
            extra,
            self.profile,
            callback=self.mergeRequestGetCb,
            errback=partial(
                self.errback,
                msg=_(u"can't get merge request: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )

    def start(self):
        common.URIFinder(
            self, os.getcwd(), "merge requests", self.getRequests, meta_map={}
        )


class Import(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "import",
            use_pubsub=True,
            pubsub_flags={C.SINGLE_ITEM, C.ITEM},
            pubsub_defaults={u"service": _(u"auto"), u"node": _(u"auto")},
            help=_(u"import a merge request"),
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "-r",
            "--repository",
            metavar="PATH",
            type=base.unicode_decoder,
            default=u".",
            help=_(u"path of the repository (DEFAULT: current directory)"),
        )

    def mergeRequestImportCb(self):
        self.host.quit(C.EXIT_OK)

    def importRequest(self):
        extra = {}
        self.host.bridge.mergeRequestsImport(
            self.repository,
            self.args.item,
            self.args.service,
            self.args.node,
            extra,
            self.profile,
            callback=self.mergeRequestImportCb,
            errback=partial(
                self.errback,
                msg=_(u"can't import merge request: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )

    def start(self):
        self.repository = os.path.expanduser(os.path.abspath(self.args.repository))
        common.URIFinder(
            self, self.repository, "merge requests", self.importRequest, meta_map={}
        )


class MergeRequest(base.CommandBase):
    subcommands = (Set, Get, Import)

    def __init__(self, host):
        super(MergeRequest, self).__init__(
            host, "merge-request", use_profile=False, help=_("merge-request management")
        )
