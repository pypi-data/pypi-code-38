#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT plugin for import external blogs
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

from sat.core.i18n import _, D_
from sat.core.constants import Const as C
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.core import exceptions

# from twisted.internet import threads
from twisted.internet import defer
import os.path
from lxml import etree
from sat.tools.common import date_utils


PLUGIN_INFO = {
    C.PI_NAME: "Bugzilla import",
    C.PI_IMPORT_NAME: "IMPORT_BUGZILLA",
    C.PI_TYPE: C.PLUG_TYPE_BLOG,
    C.PI_DEPENDENCIES: ["TICKETS_IMPORT"],
    C.PI_MAIN: "BugzillaImport",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _("""Tickets importer for Bugzilla"""),
}

SHORT_DESC = D_(u"import tickets from Bugzilla xml export file")

LONG_DESC = D_(
    u"""This importer handle Bugzilla xml export file.

To use it, you'll need to export tickets using XML.
Tickets will be uploaded with the same ID as for Bugzilla, any existing ticket with this ID will be replaced.

location: you must use the absolute path to your .xml file
"""
)

STATUS_MAP = {
    "NEW": "queued",
    "ASSIGNED": "started",
    "RESOLVED": "review",
    "CLOSED": "closed",
    "REOPENED": "started",  # we loose data here because there is no need on basic workflow to have a reopened status
}


class BugzillaParser(object):
    # TODO: add a way to reassign values

    def parse(self, file_path):
        tickets = []
        root = etree.parse(file_path)

        for bug in root.xpath("bug"):
            ticket = {}
            ticket["id"] = bug.findtext("bug_id")
            ticket["created"] = date_utils.date_parse(bug.findtext("creation_ts"))
            ticket["updated"] = date_utils.date_parse(bug.findtext("delta_ts"))
            ticket["title"] = bug.findtext("short_desc")
            reporter_elt = bug.find("reporter")
            ticket["author"] = reporter_elt.get("name")
            if ticket["author"] is None:
                if "@" in reporter_elt.text:
                    ticket["author"] = reporter_elt.text[
                        : reporter_elt.text.find("@")
                    ].title()
                else:
                    ticket["author"] = u"no name"
            ticket["author_email"] = reporter_elt.text
            assigned_to_elt = bug.find("assigned_to")
            ticket["assigned_to_name"] = assigned_to_elt.get("name")
            ticket["assigned_to_email"] = assigned_to_elt.text
            ticket["cc_emails"] = [e.text for e in bug.findall("cc")]
            ticket["priority"] = bug.findtext("priority").lower().strip()
            ticket["severity"] = bug.findtext("bug_severity").lower().strip()
            ticket["product"] = bug.findtext("product")
            ticket["component"] = bug.findtext("component")
            ticket["version"] = bug.findtext("version")
            ticket["platform"] = bug.findtext("rep_platform")
            ticket["os"] = bug.findtext("op_sys")
            ticket["status"] = STATUS_MAP.get(bug.findtext("bug_status"), "queued")
            ticket["milestone"] = bug.findtext("target_milestone")

            body = None
            comments = []
            for longdesc in bug.findall("long_desc"):
                if body is None:
                    body = longdesc.findtext("thetext")
                else:
                    who = longdesc.find("who")
                    comment = {
                        "id": longdesc.findtext("commentid"),
                        "author_email": who.text,
                        "published": date_utils.date_parse(longdesc.findtext("bug_when")),
                        "author": who.get("name", who.text),
                        "content": longdesc.findtext("thetext"),
                    }
                    comments.append(comment)

            ticket["body"] = body
            ticket["comments"] = comments
            tickets.append(ticket)

        tickets.sort(key=lambda t: int(t["id"]))
        return (tickets, len(tickets))


class BugzillaImport(object):
    def __init__(self, host):
        log.info(_(u"Bugilla Import plugin initialization"))
        self.host = host
        host.plugins["TICKETS_IMPORT"].register(
            "bugzilla", self.Import, SHORT_DESC, LONG_DESC
        )

    def Import(self, client, location, options=None):
        if not os.path.isabs(location):
            raise exceptions.DataError(
                u"An absolute path to XML data need to be given as location"
            )
        bugzilla_parser = BugzillaParser()
        # d = threads.deferToThread(bugzilla_parser.parse, location)
        d = defer.maybeDeferred(bugzilla_parser.parse, location)
        return d
