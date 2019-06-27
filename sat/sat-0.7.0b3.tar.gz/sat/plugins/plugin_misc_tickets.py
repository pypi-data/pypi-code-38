#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for Pubsub Schemas
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
from twisted.internet import defer
from sat.tools.common import uri
from sat.tools import utils
import shortuuid
from sat.core.log import getLogger

log = getLogger(__name__)

NS_TICKETS = "org.salut-a-toi.tickets:0"

PLUGIN_INFO = {
    C.PI_NAME: _(u"Tickets management"),
    C.PI_IMPORT_NAME: u"TICKETS",
    C.PI_TYPE: u"EXP",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: [u"XEP-0060", u"PUBSUB_SCHEMA", u"XEP-0277", u"IDENTITY"],
    C.PI_MAIN: u"Tickets",
    C.PI_HANDLER: u"no",
    C.PI_DESCRIPTION: _(u"""Tickets management plugin"""),
}


class Tickets(object):
    def __init__(self, host):
        log.info(_(u"Tickets plugin initialization"))
        self.host = host
        host.registerNamespace(u"tickets", NS_TICKETS)
        self._p = self.host.plugins[u"XEP-0060"]
        self._s = self.host.plugins[u"PUBSUB_SCHEMA"]
        self._m = self.host.plugins[u"XEP-0277"]
        host.bridge.addMethod(
            u"ticketsGet",
            u".plugin",
            in_sign=u"ssiassa{ss}s",
            out_sign=u"(asa{ss})",
            method=utils.partial(
                self._s._get,
                default_node=NS_TICKETS,
                form_ns=NS_TICKETS,
                filters={
                    u"author": self._s.valueOrPublisherFilter,
                    u"created": self._s.dateFilter,
                    u"updated": self._s.dateFilter,
                },
            ),
            async=True,
        )
        host.bridge.addMethod(
            "ticketSet",
            ".plugin",
            in_sign="ssa{sas}ssss",
            out_sign="s",
            method=self._set,
            async=True,
        )
        host.bridge.addMethod(
            "ticketsSchemaGet",
            ".plugin",
            in_sign="sss",
            out_sign="s",
            method=utils.partial(self._s._getUISchema, default_node=NS_TICKETS),
            async=True,
        )

    def _set(self, service, node, values, schema=None, item_id=None, extra=u'',
             profile_key=C.PROF_KEY_NONE):
        client, service, node, schema, item_id, extra = self._s.prepareBridgeSet(
            service, node, schema, item_id, extra, profile_key
        )
        d = self.set(
            client, service, node, values, schema, item_id, extra, deserialise=True
        )
        d.addCallback(lambda ret: ret or u"")
        return d

    @defer.inlineCallbacks
    def set(self, client, service, node, values, schema=None, item_id=None, extra=None,
            deserialise=False, form_ns=NS_TICKETS):
        """Publish a tickets

        @param node(unicode, None): Pubsub node to use
            None to use default tickets node
        @param values(dict[key(unicode), [iterable[object]|object]]): values of the ticket

            if value is not iterable, it will be put in a list
            'created' and 'updated' will be forced to current time:
                - 'created' is set if item_id is None, i.e. if it's a new ticket
                - 'updated' is set everytime
        @param extra(dict, None): same as for [XEP-0060.sendItem] with additional keys:
            - update(bool): if True, get previous item data to merge with current one
                if True, item_id must be None
        other arguments are same as for [self._s.sendDataFormItem]
        @return (unicode): id of the created item
        """
        if not node:
            node = NS_TICKETS

        if not item_id:
            comments_service = yield self._m.getCommentsService(client, service)

            # we need to use uuid for comments node, because we don't know item id in
            # advance (we don't want to set it ourselves to let the server choose, so we
            # can have a nicer id if serial ids is activated)
            comments_node = self._m.getCommentsNode(
                node + u"_" + unicode(shortuuid.uuid())
            )
            options = {
                self._p.OPT_ACCESS_MODEL: self._p.ACCESS_OPEN,
                self._p.OPT_PERSIST_ITEMS: 1,
                self._p.OPT_MAX_ITEMS: -1,
                self._p.OPT_DELIVER_PAYLOADS: 1,
                self._p.OPT_SEND_ITEM_SUBSCRIBE: 1,
                self._p.OPT_PUBLISH_MODEL: self._p.ACCESS_OPEN,
            }
            yield self._p.createNode(client, comments_service, comments_node, options)
            values[u"comments_uri"] = uri.buildXMPPUri(
                u"pubsub",
                subtype="microblog",
                path=comments_service.full(),
                node=comments_node,
            )

        item_id = yield self._s.set(
            client, service, node, values, schema, item_id, extra, deserialise, form_ns
        )
        defer.returnValue(item_id)
