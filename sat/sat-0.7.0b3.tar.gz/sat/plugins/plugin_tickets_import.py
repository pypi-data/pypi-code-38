#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT plugin for import external ticketss
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

from sat.core.i18n import _
from sat.core.constants import Const as C
from sat.core import exceptions
from sat.core.log import getLogger

log = getLogger(__name__)
from twisted.internet import defer
from sat.tools.common import uri
from sat.tools import utils


PLUGIN_INFO = {
    C.PI_NAME: "tickets import",
    C.PI_IMPORT_NAME: "TICKETS_IMPORT",
    C.PI_TYPE: C.PLUG_TYPE_IMPORT,
    C.PI_DEPENDENCIES: ["IMPORT", "XEP-0060", "XEP-0277", "PUBSUB_SCHEMA"],
    C.PI_MAIN: "TicketsImportPlugin",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _(
        u"""Tickets import management:
This plugin manage the different tickets importers which can register to it, and handle generic importing tasks."""
    ),
}

OPT_MAPPING = "mapping"
FIELDS_LIST = (u"labels", u"cc_emails")  # fields which must have a list as value
FIELDS_DATE = (u"created", u"updated")

NS_TICKETS = "org.salut-a-toi.tickets:0"


class TicketsImportPlugin(object):
    BOOL_OPTIONS = ()
    JSON_OPTIONS = (OPT_MAPPING,)
    OPT_DEFAULTS = {}

    def __init__(self, host):
        log.info(_("plugin Tickets Import initialization"))
        self.host = host
        self._importers = {}
        self._p = host.plugins["XEP-0060"]
        self._m = host.plugins["XEP-0277"]
        self._s = host.plugins["PUBSUB_SCHEMA"]
        host.plugins["IMPORT"].initialize(self, u"tickets")

    @defer.inlineCallbacks
    def importItem(
        self, client, item_import_data, session, options, return_data, service, node
    ):
        """

        @param item_import_data(dict): no key is mandatory, but if a key doesn't exists in dest form, it will be ignored.
            Following names are recommendations which should be used where suitable in importers.
            except if specified in description, values are unicode
            'id': unique id (must be unique in the node) of the ticket
            'title': title (or short description/summary) of the ticket
            'body': main description of the ticket
            'created': date of creation (unix time)
            'updated': date of last update (unix time)
            'author': full name of reporter
            'author_jid': jid of reporter
            'author_email': email of reporter
            'assigned_to_name': full name of person working on it
            'assigned_to_email': email of person working on it
            'cc_emails': list of emails subscribed to the ticket
            'priority': priority of the ticket
            'severity': severity of the ticket
            'labels': list of unicode values to use as label
            'product': product concerned by this ticket
            'component': part of the product concerned by this ticket
            'version': version of the product/component concerned by this ticket
            'platform': platform converned by this ticket
            'os': operating system concerned by this ticket
            'status': current status of the ticket, values:
                - "queued": ticket is waiting
                - "started": progress is ongoing
                - "review": ticket is fixed and waiting for review
                - "closed": ticket is finished or invalid
            'milestone': target milestone for this ticket
            'comments': list of microblog data (comment metadata, check [XEP_0277.send] data argument)
        @param options(dict, None): Below are the generic options,
            tickets importer can have specific ones. All options are serialized unicode values
            generic options:
                - OPT_MAPPING (json): dict of imported ticket key => exported ticket key
                    e.g.: if you want to map "component" to "labels", you can specify:
                        {'component': 'labels'}
                    If you specify several import ticket key to the same dest key,
                    the values will be joined with line feeds
        """
        if "comments_uri" in item_import_data:
            raise exceptions.DataError(
                _(u"comments_uri key will be generated and must not be used by importer")
            )
        for key in FIELDS_LIST:
            if not isinstance(item_import_data.get(key, []), list):
                raise exceptions.DataError(_(u"{key} must be a list").format(key=key))
        for key in FIELDS_DATE:
            try:
                item_import_data[key] = utils.xmpp_date(item_import_data[key])
            except KeyError:
                continue
        if session[u"root_node"] is None:
            session[u"root_node"] = NS_TICKETS
        if not "schema" in session:
            session["schema"] = yield self._s.getSchemaForm(
                client, service, node or session[u"root_node"]
            )
        defer.returnValue(item_import_data)

    @defer.inlineCallbacks
    def importSubItems(self, client, item_import_data, ticket_data, session, options):
        # TODO: force "open" permission (except if private, check below)
        # TODO: handle "private" metadata, to have non public access for node
        # TODO: node access/publish model should be customisable
        comments = ticket_data.get("comments", [])
        service = yield self._m.getCommentsService(client)
        node = self._m.getCommentsNode(session["root_node"] + u"_" + ticket_data["id"])
        node_options = {
            self._p.OPT_ACCESS_MODEL: self._p.ACCESS_OPEN,
            self._p.OPT_PERSIST_ITEMS: 1,
            self._p.OPT_MAX_ITEMS: -1,
            self._p.OPT_DELIVER_PAYLOADS: 1,
            self._p.OPT_SEND_ITEM_SUBSCRIBE: 1,
            self._p.OPT_PUBLISH_MODEL: self._p.ACCESS_OPEN,
        }
        yield self._p.createIfNewNode(client, service, node, options=node_options)
        ticket_data["comments_uri"] = uri.buildXMPPUri(
            u"pubsub", subtype="microblog", path=service.full(), node=node
        )
        for comment in comments:
            if "updated" not in comment and "published" in comment:
                # we don't want an automatic update date
                comment["updated"] = comment["published"]
            yield self._m.send(client, comment, service, node)

    def publishItem(self, client, ticket_data, service, node, session):
        if node is None:
            node = NS_TICKETS
        id_ = ticket_data.pop("id", None)
        log.debug(
            u"uploading item [{id}]: {title}".format(
                id=id_, title=ticket_data.get("title", "")
            )
        )
        return self._s.sendDataFormItem(
            client, service, node, ticket_data, session["schema"], id_
        )

    def itemFilters(self, client, ticket_data, session, options):
        mapping = options.get(OPT_MAPPING)
        if mapping is not None:
            if not isinstance(mapping, dict):
                raise exceptions.DataError(_(u"mapping option must be a dictionary"))

            for source, dest in mapping.iteritems():
                if not isinstance(source, unicode) or not isinstance(dest, unicode):
                    raise exceptions.DataError(
                        _(
                            u"keys and values of mapping must be sources and destinations ticket fields"
                        )
                    )
                if source in ticket_data:
                    value = ticket_data.pop(source)
                    if dest in FIELDS_LIST:
                        values = ticket_data[dest] = ticket_data.get(dest, [])
                        values.append(value)
                    else:
                        if dest in ticket_data:
                            ticket_data[dest] = ticket_data[dest] + u"\n" + value
                        else:
                            ticket_data[dest] = value
