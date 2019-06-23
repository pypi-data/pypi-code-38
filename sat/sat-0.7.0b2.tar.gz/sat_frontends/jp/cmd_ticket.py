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
from sat_frontends.jp import common
from sat_frontends.jp.constants import Const as C
from functools import partial
import json
import os

__commands__ = ["Ticket"]

FIELDS_MAP = u"mapping"


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
            use_output=C.OUTPUT_LIST_XMLUI,
            help=_(u"get tickets"),
        )
        self.need_loop = True

    def add_parser_options(self):
        pass

    def ticketsGetCb(self, tickets_data):
        self.output(tickets_data[0])
        self.host.quit(C.EXIT_OK)

    def getTickets(self):
        self.host.bridge.ticketsGet(
            self.args.service,
            self.args.node,
            self.args.max,
            self.args.items,
            u"",
            self.getPubsubExtra(),
            self.profile,
            callback=self.ticketsGetCb,
            errback=partial(
                self.errback,
                msg=_(u"can't get tickets: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )

    def start(self):
        common.URIFinder(self, os.getcwd(), "tickets", self.getTickets, meta_map={})


class Import(base.CommandAnswering):
    # TODO: factorize with blog/import

    def __init__(self, host):
        super(Import, self).__init__(
            host,
            "import",
            use_progress=True,
            help=_(u"import tickets from external software/dataset"),
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "importer",
            type=base.unicode_decoder,
            nargs="?",
            help=_(u"importer name, nothing to display importers list"),
        )
        self.parser.add_argument(
            "-o",
            "--option",
            action="append",
            nargs=2,
            default=[],
            metavar=(u"NAME", u"VALUE"),
            help=_(u"importer specific options (see importer description)"),
        )
        self.parser.add_argument(
            "-m",
            "--map",
            action="append",
            nargs=2,
            default=[],
            metavar=(u"IMPORTED_FIELD", u"DEST_FIELD"),
            help=_(
                u"specified field in import data will be put in dest field (default: use same field name, or ignore if it doesn't exist)"
            ),
        )
        self.parser.add_argument(
            "-s",
            "--service",
            type=base.unicode_decoder,
            default=u"",
            metavar=u"PUBSUB_SERVICE",
            help=_(u"PubSub service where the items must be uploaded (default: server)"),
        )
        self.parser.add_argument(
            "-n",
            "--node",
            type=base.unicode_decoder,
            default=u"",
            metavar=u"PUBSUB_NODE",
            help=_(
                u"PubSub node where the items must be uploaded (default: tickets' defaults)"
            ),
        )
        self.parser.add_argument(
            "location",
            type=base.unicode_decoder,
            nargs="?",
            help=_(
                u"importer data location (see importer description), nothing to show importer description"
            ),
        )

    def onProgressStarted(self, metadata):
        self.disp(_(u"Tickets upload started"), 2)

    def onProgressFinished(self, metadata):
        self.disp(_(u"Tickets uploaded successfully"), 2)

    def onProgressError(self, error_msg):
        self.disp(_(u"Error while uploading tickets: {}").format(error_msg), error=True)

    def error(self, failure):
        self.disp(
            _("Error while trying to upload tickets: {reason}").format(reason=failure),
            error=True,
        )
        self.host.quit(1)

    def start(self):
        if self.args.location is None:
            for name in ("option", "service", "node"):
                if getattr(self.args, name):
                    self.parser.error(
                        _(
                            u"{name} argument can't be used without location argument"
                        ).format(name=name)
                    )
            if self.args.importer is None:
                self.disp(
                    u"\n".join(
                        [
                            u"{}: {}".format(name, desc)
                            for name, desc in self.host.bridge.ticketsImportList()
                        ]
                    )
                )
            else:
                try:
                    short_desc, long_desc = self.host.bridge.ticketsImportDesc(
                        self.args.importer
                    )
                except Exception as e:
                    msg = [l for l in unicode(e).split("\n") if l][
                        -1
                    ]  # we only keep the last line
                    self.disp(msg)
                    self.host.quit(1)
                else:
                    self.disp(
                        u"{name}: {short_desc}\n\n{long_desc}".format(
                            name=self.args.importer,
                            short_desc=short_desc,
                            long_desc=long_desc,
                        )
                    )
            self.host.quit()
        else:
            # we have a location, an import is requested
            options = {key: value for key, value in self.args.option}
            fields_map = dict(self.args.map)
            if fields_map:
                if FIELDS_MAP in options:
                    self.parser.error(
                        _(
                            u"fields_map must be specified either preencoded in --option or using --map, but not both at the same time"
                        )
                    )
                options[FIELDS_MAP] = json.dumps(fields_map)

            def gotId(id_):
                self.progress_id = id_

            self.host.bridge.ticketsImport(
                self.args.importer,
                self.args.location,
                options,
                self.args.service,
                self.args.node,
                self.profile,
                callback=gotId,
                errback=self.error,
            )


class Ticket(base.CommandBase):
    subcommands = (Get, Import)

    def __init__(self, host):
        super(Ticket, self).__init__(
            host, "ticket", use_profile=False, help=_("tickets handling")
        )
